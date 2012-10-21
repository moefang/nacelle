# stdlib imports
import json
import logging

# appengine SDK imports
from google.appengine.api import memcache
from google.appengine.ext import db

# local imports
from nacelle.conf import sentry
from nacelle.handlers.base import BaseHandler
from nacelle.handlers.mixins import JSONMixins
from nacelle.handlers.mixins import TemplateMixins
from nacelle.models.api import CacheKey
from unidecode import unidecode


class APIHandler(BaseHandler, JSONMixins, TemplateMixins):

    """
    This handler provides a quick and easy way to build a
    pageable/queryable/sortable/RESTful(ish) API from any
    appengine model (full read/write support) or other
    iterable (read only).
    """

    model = None
    query = None

    # iterable = None

    cache = False
    cache_key_prefix = ''
    cache_time = 300
    allowed_methods = ['GET', 'POST', 'DELETE']

    def normalise_value(self, value):

        """
        Simple conversion of query string params to correct types for use in queries
        """

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

    @property
    def cache_key(self):
        """
        Generate the cache key using query params if any
        """
        cache_key = ''
        for k, v in self.request.GET.items():
            cache_key += k + '=' + unidecode(v)
        return cache_key

    def update_cache(self, key, value):
        """
        Add object to memcache and add its key to a global list we can use for flushing on change
        """
        # Set value in cache for configured time
        if self.cache_time:
            memcache.set(key, value, time=self.cache_time)
        else:
            memcache.set(key, value)
        # Add key to stored list of keys
        parent_key = self.__class__.__name__
        keys = CacheKey.all().filter('par_key =', parent_key).get()
        if keys is None:
            keys = CacheKey()
            keys.par_key = parent_key
        if key not in keys.cache_keys:
            keys.cache_keys.append(key)
            keys.put()

    def flush_cache(self):
        """
        Flush all relevant keys from memcache
        """
        if self.cache:
            # get key list from datastore
            parent_key = self.__class__.__name__
            keys = CacheKey.all().filter('par_key =', parent_key).get()
            # get list of keys to flush
            if keys is None:
                del_keys = []
            else:
                del_keys = keys.cache_keys
            # flush keys
            memcache.delete_multi(del_keys)

    def get(self, key=None):

        # check if method allowed
        if not 'GET' in self.allowed_methods:
            self.abort(405)

        # check if cached
        if self.cache:
            # Build cache key and attempt to pull result from memcache
            if key:
                cache_key = self.cache_key_prefix + '-' + key
            else:
                cache_key = self.cache_key_prefix + '-' + self.cache_key
            cached_response = memcache.get(cache_key)
            if cached_response is not None:
                return self.json_response(cached_response)

        # get by key only works if a model has been defined, otherwise
        # iterable access is performed by index
        if key:
            logging.info('Retrieving entity by key: %s' % str(key))
            if self.model:
                if 'key:' in key:
                    key = key.replace('key:', '')
                entity = self.get_entity_by_key(key)
            else:
                entity = self.get_entity_by_index(key)
            if self.cache:
                self.update_cache(cache_key, entity)
            self.json_response(entity)
        else:
            # paginate the query if specified
            if 'page' in self.request.GET:
                page = int(self.request.GET['page'])
                if 'page_size' in self.request.GET:
                    p_size = int(self.request.GET['page_size'])
                else:
                    p_size = 20
                feed_as_dict = self.get_entities(page, p_size)
            else:
                feed_as_dict = self.get_entities()
            if self.cache:
                self.update_cache(cache_key, feed_as_dict)
            self.json_response(feed_as_dict)

    def get_entity_by_key(self, key):
        """
        Retrieve entity from the datastore by encoded key
        """
        obj = db.get(db.Key(encoded=key))
        # throw 404 if retrieved object is not of type self.model
        if not isinstance(obj, self.model):
            self.abort(404)
        return obj.get_json()

    def get_entity_by_index(self, index):
        """
        Retrieve entity by list index
        """
        index = int(index)
        try:
            obj = self.iterable[index]
        except IndexError:
            self.abort(404)
        return json.dumps(obj)

    def build_query(self):
        """
        Build a datastore query from GET params
        """

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
        return query

    def get_entities(self, page=None, page_size=None):
        """
        Retrieve our entities and return in specified format
        """
        # check if results should be paginated
        if page is not None:
            offset = (page - 1) * page_size
            limit = page_size
        else:
            offset = 0
            limit = None

        # initialise response dict
        feed_as_dict = {
            'page': page,
            'pagesize': page_size,
        }
        # check if we have predetermined query
        if self.query:
            results = self.query.run(offset=offset, limit=limit)
            feed_as_dict['items_total'] = self.query.count(limit=1000000000)
        # check if model is defined
        elif self.model:
            q = self.build_query()
            feed_as_dict['items_total'] = q.count(limit=1000000000)
            results = q.run(offset=offset, limit=limit)
        # elif self.iterable:
        #     results = self.iterable()
        #     feed_as_dict['total_items'] = len(results)
        # else abort with 403 as not allowed
        else:
            self.abort(403)
        # get page size
        if page_size is None:
            page_size = feed_as_dict['items_total']
        # get page count
        try:
            pagecount = feed_as_dict['items_total'] / page_size
        except ZeroDivisionError:
            pagecount = 0
        # add 1 to page count if evenly divides into total
        if feed_as_dict['items_total']:
            if feed_as_dict['items_total'] % page_size:
                pagecount += 1
        feed_as_dict['pagecount'] = pagecount
        # get JSON reprs of entities
        feed_as_dict['feed'] = [obj.get_json(encode=False) for obj in results]
        # get total number of items on page
        feed_as_dict['items_on_page'] = len(feed_as_dict['feed'])
        # return response dict
        return feed_as_dict

    def post(self, key=None):

        # check if method is allowed
        if not 'POST' in self.allowed_methods:
            self.abort(405)

        # check if key has been passed to POST
        if key is not None:
            # sanitise key string
            if 'key:' in key:
                key = key.replace('key:', '')
            # get entity from db
            obj = db.get(db.Key(encoded=key))
            # throw 404 if retrieved object is not of type self.model
            if not isinstance(obj, self.model):
                self.abort(404)
            # update entity with JSON values
            obj.set_json(self.request.body)
            # save entity
            obj.put()
            # return entity
            new_entity = obj.get_json()
        else:
            # JSON parse posted entity
            posted_entity = json.loads(self.request.body)
            # create new model entity
            new_entity = self.model()
            # update model properties with POSTed data
            new_entity.set_json(posted_entity)
            # save entity
            new_entity.put()
            # get JSON repr of new entity
            new_entity = new_entity.get_json()
        # flush memcache
        self.flush_cache()
        # return newly created/updated entity
        self.json_response(new_entity)

    def delete(self, key):

        # check if method is allowed
        if not 'DELETE' in self.allowed_methods:
            self.abort(405)

        # sanitise key
        if 'key:' in key:
            key = key.replace('key:', '')
        # retrieve entity from datastore
        obj = db.get(db.Key(encoded=key))
        # throw 404 if retrieved object is not of type self.model
        if not isinstance(obj, self.model):
            self.abort(404)
        # delete entity
        try:
            obj.delete()
        except AttributeError:
            # throw 404 if entity doesn't exist
            self.abort(404)
        # flush memcache
        self.flush_cache()
        # return 200 OK
        self.json_response({'status': '200 OK'})
