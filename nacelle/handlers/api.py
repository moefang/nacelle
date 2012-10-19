# stdlib imports
import json

# appengine SDK imports
from google.appengine.api import memcache
from google.appengine.ext import db

# local imports
from nacelle.conf import sentry
from nacelle.handlers.base import BaseHandler
from nacelle.handlers.mixins import JSONMixins
from nacelle.utils.paginator import EmptyPage
from nacelle.utils.paginator import PageNotAnInteger
from nacelle.utils.paginator import Paginator
from unidecode import unidecode


class APIHandler(BaseHandler, JSONMixins):

    """
    This handler provides a quick and easy way to build a
    pageable/queryable/sortable API from any appengine model instance.

    Simply subclass this handler and configure the options below:
        model: Appengine model instance
        cache: Enable/disable storing results in memcache
        cache_key_prefix: String to prepend to memcache keys (required if cache = True)
        cache_time: Time in seconds to cache result
        query: Any iterable which implements count() or __len__() methods

    You should set one of model or query, but not both.  Setting model
    will allow you to filter and sort results using query parameter in the
    url.  Setting query will lock the handler to one specific iterable and
    only the page and page_size query parameters will have any effect.

    >>> class SomeDynamicAPIHandler(APIHandler):
    >>>     model = someapp.SomeModel

    >>> class SomeStaticAPIHandler(APIHandler):
    >>>     query = ['john', 'paul', 'joe', 'bob', 'peter', 'paddy', 'jim']
    >>>     cache = True
    >>>     cache_key_prefix = 'some_prefix'

    """

    model = None
    cache = False
    cache_key_prefix = ''
    cache_time = 300
    query = None

    def normalise_value(self, value):
        # check if value is int
        try:
            value = int(value)
        except ValueError:
            pass
        else:
            return value

        # check if value is float
        try:
            value = float(value)
        except ValueError:
            pass
        else:
            return value

        # return value if string
        return value

    def get(self):

        if self.cache:

            # raise error if cache prefix not set
            if not self.cache_key_prefix:
                raise AttributeError('cache_key_prefix is required when cache is enabled')

            # Generate the cache key using query params if any
            cache_key = self.cache_key_prefix + '-'
            for k, v in self.request.GET.items():
                cache_key += k + '=' + unidecode(v)

            # check if value stored in cache
            cached_response = memcache.get(cache_key)
            # return cached value if present
            if cached_response is not None:
                self.json_response(cached_response)
                return None

        # Retrieve a single entity from the DB by key
        if self.model is not None:
            if 'key' in self.request.GET:
                key_str = self.request.GET['key']
                obj = db.get(db.Key(encoded=key_str))
                # throw 404 if retrieved object is not of type self.model
                if not isinstance(obj, self.model):
                    self.abort(404)

                # serialise retrieved object
                try:
                    response_text = obj.get_json()
                except AttributeError:
                    response_text = json.dumps(obj)

                if self.cache:
                    # store computed json object in cache
                    memcache.set(cache_key, response_text, self.cache_time)

                self.json_response(response_text)
                return None

        if self.query is not None:
            query = self.query
        else:
            # Define our base query
            query = self.model.all()

            # Add any filters to our query
            if 'filter' in self.request.GET:
                filter_params = self.request.GET.getall('filter')
                for filter_param in filter_params:
                    if '__lt__' in filter_param:
                        key, val = filter_param.split('__lt__')
                        val = self.normalise_value(val)
                        query = query.filter('%s <' % key, val)
                    elif '__gt__' in filter_param:
                        key, val = filter_param.split('__gt__')
                        val = self.normalise_value(val)
                        query = query.filter('%s >' % key, val)
                    elif '__lte__' in filter_param:
                        key, val = filter_param.split('__lte__')
                        val = self.normalise_value(val)
                        query = query.filter('%s <=' % key, val)
                    elif '__gte__' in filter_param:
                        key, val = filter_param.split('__gte__')
                        val = self.normalise_value(val)
                        query = query.filter('%s >=' % key, val)
                    elif '__' in filter_param:
                        key, val = filter_param.split('__')
                        val = self.normalise_value(val)
                        query = query.filter('%s =' % key, val)
                    else:
                        self.abort(400)
            # order the results of our query
            if 'order' in self.request.GET:
                order_params = self.request.GET.getall('order')
                for order_param in order_params:
                    try:
                        query = query.order(order_param)
                    except db.PropertyError:
                        sentry.captureException()
                        self.abort(400)

        feed_as_dict = {}

        # paginate the query if specified
        if 'page' in self.request.GET:
            if 'page_size' in self.request.GET:
                p_size = int(self.request.GET['page_size'])
            else:
                p_size = 20
            p = Paginator(query, p_size)
            feed_as_dict['pagesize'] = p_size
            feed_as_dict['pagecount'] = p.num_pages
            try:
                # paginate the result set
                page = p.page(self.request.GET['page'])
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                page = p.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                page = p.page(p.num_pages)
            feed_as_dict['page'] = page.number
            objects = page.object_list
        else:
            objects = query

        # get JSON representations of the objects and return
        objects_as_list = []
        for obj in objects:
            try:
                objects_as_list.append(obj.get_json(encode=False))
            except AttributeError:
                objects_as_list.append(obj)
        feed_as_dict['feed'] = objects_as_list
        feed_as_json = json.dumps(feed_as_dict)

        if self.cache:
            # store computed json object in cache
            memcache.set(cache_key, feed_as_json, self.cache_time)

        self.json_response(feed_as_json)
