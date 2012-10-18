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

    model = None
    cache = False
    cache_key_prefix = ''
    cache_time = 300

    def json_response(self, response_text):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(response_text)

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

        # Generate the cache key
        cache_key = self.cache_key_prefix + '-'
        for k, v in self.request.GET.items():
            cache_key += k + '=' + unidecode(v)

        if self.cache:
            # check if value stored in cache
            cached_response = memcache.get(cache_key)
            # return cached value if present
            if cached_response is not None:
                self.json_response(cached_response)
                return None

        # Retrieve a single entity from the DB by key
        if 'key' in self.request.GET:
            key_str = self.request.GET['key']
            response_text = db.get(db.Key(encoded=key_str)).json

            if self.cache:
                # store computed json object in cache
                memcache.set(cache_key, response_text, self.cache_time)

            self.json_response(response_text)
            return None

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
        # order the results of our query
        if 'order' in self.request.GET:
            order_params = self.request.GET.getall('order')
            for order_param in order_params:
                try:
                    query = query.order(order_param)
                except db.PropertyError:
                    sentry.captureException()
                    self.json_response('[]')
                    return None

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
        objects_as_list = [obj.get_json(encode=False) for obj in objects]
        feed_as_dict['feed'] = objects_as_list
        feed_as_json = json.dumps(feed_as_dict)

        if self.cache:
            # store computed json object in cache
            memcache.set(cache_key, feed_as_json, self.cache_time)

        self.json_response(feed_as_json)
