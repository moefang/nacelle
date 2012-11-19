"""
A collection of nacelle handlers which are useful
for building RESTful(ish) APIs
"""
# stdlib imports
import json
import logging

# appengine SDK imports
from google.appengine.api import memcache
from google.appengine.ext import db

# local imports
from nacelle.handlers.base import JSONHandler
from unidecode import unidecode


class FixedQueryAPIHandler(JSONHandler):

    """
    This handler allows simple building of RESTful APIs with a defined
    query which will be used when accessing the root endpoint with a GET
    request
    """

    # specify the model type on which the handler will operate
    # this is only necessary when the handler makes use of POST
    # or DELETE support
    model = None
    # default page size for results returned from this handler
    page_size = 20
    # specify the amount of time to cache all GET requests to
    # this handler. Set to any boolean value of False to disable.
    cache = 60
    # list of HTTP methods to allow for this handler
    # Accepts GET, POST, and DELETE
    allowed_methods = ['GET']

    def get_query(self):

        """
        This method should be overridden to provide a
        query for any list requests
        """

        pass

    def get_cache_key(self, query, page_size, cursor):

        """
        Build and return a cache key for storing a response in memcache
        """

        # build and return key
        cache_key = '%s-%s-%s' % (self.__class__.__name__, page_size or str(page_size), str(cursor))
        return cache_key

    def get_next_page(self, query, page_size, cursor):

        """
        Build and return a relative URL which a client can use to get
        the next set of results in an efficient manner using a cursor
        """

        # build and return URL
        next_page = "%s?page_size=%s&cursor=%s" % (self.request.path, str(page_size), cursor)
        return next_page

    def get_context(self):

        """
        Build and return query page for JSON response
        """

        # get page size from query params or use default
        page_size = self.request.GET.get('page_size', None) or self.page_size
        # get cursor from query params if specified
        cursor = self.request.GET.get('cursor', None)
        # get query to use
        query = self.get_query()

        if self.cache:
            # build cache key
            cache_key = self.get_cache_key(query, page_size, cursor)
            # check if response has been cached
            cached_response = memcache.get(cache_key)
            if cached_response is not None:
                # return cached response
                logging.info('Cache hit: %s' % cache_key)
                return cached_response
            else:
                # log the cache miss
                logging.info('Cache miss: %s' % cache_key)

        if cursor is None:
            # run query without cursor
            entities = query.fetch(int(page_size))
            # get cursor string
            cursor = query.cursor()
        else:
            # run query with cursor
            entities = query.with_cursor(cursor).fetch(int(page_size))
            # get cursor string
            cursor = query.cursor()

        # convert entities to list of dicts
        entities = [x.get_json(encode=False) for x in entities]
        # build next page url
        next_page = self.get_next_page(query, page_size, cursor)
        # get number of entities on page
        page_size = len(entities)

        # build response object
        response = {'entities': entities, 'next_page': next_page, 'page_size': page_size}

        if self.cache:
            # cache response if enabled
            memcache.set(cache_key, response, self.cache)

        # return dict for serialisation
        return response

    def get_single_entity(self, key):

        """
        Retrieve entity from the datastore by encoded key
        """

        # check if cached
        obj = memcache.get(key)
        # get from datastore if not cached
        if obj is None:
            logging.info('Cache miss: %s' % key)
            obj = db.get(db.Key(encoded=key))
        else:
            logging.info('Cache hit: %s' % key)
        # throw 404 if retrieved object is not of type self.model
        if not isinstance(obj, self.model):
            self.abort(404)
        if self.cache:
            memcache.set(key, obj, self.cache)
        obj = obj.get_json()
        return obj

    def get(self, key=None):

        """
        Handles all get requests for the handler
        """

        # return individual key
        if key is not None:
            entity = self.get_single_entity(key)
            return self.json_response(entity)
        # build response object
        context = self.get_context()
        # return JSON response
        return self.json_response(context)

    def post(self, key=None):

        """
        Handles all post requests for this handler and allows
        creation or modification of entities via a RESTful API.
        """

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
            new_entity = new_entity.get_json(encode=False)
        # return newly created/updated entity
        self.json_response(new_entity)

    def delete(self, key):

        """
        Handles all delete requests for this handler and allows
        deletion of entities via a RESTful API.
        """

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
        # return 200 OK
        self.json_response({'status': '200 OK'})


class DynamicQueryAPIHandler(FixedQueryAPIHandler):

    """
    This handler allows simple building of RESTful APIs with a dynamic
    query which will be used when accessing the root endpoint with a GET
    request.  The query will be built from parsed GET parameters
    """

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
                query = query.order(order_param)
        return query

    def get_cache_key(self, query, page_size, cursor):

        """
        Build and return a cache key for storing a response in memcache
        """

        # build initial cache key
        cache_key = '%s-%s-%s' % (self.__class__.__name__, page_size or str(page_size), str(cursor))
        # add any filter params to cache key
        if 'filter' in self.request.GET:
            filter_params = self.request.GET.getall('filter')
            for filter_param in filter_params:
                cache_key = cache_key + '&filter=%s' % unidecode(filter_param)
        # add any order params to cache key
        if 'order' in self.request.GET:
            order_params = self.request.GET.getall('order')
            for order_param in order_params:
                cache_key = cache_key + '&order=%s' % unidecode(order_param)
        # return newly built cache key
        return cache_key

    def get_next_page(self, query, page_size, cursor):

        """
        Build and return a relative URL which a client can use to get
        the next set of results in an efficient manner using a cursor
        """

        # build initial url
        next_page = "%s?page_size=%s&cursor=%s" % (self.request.path, str(page_size), cursor)
        # add any filter params to url
        if 'filter' in self.request.GET:
            filter_params = self.request.GET.getall('filter')
            for filter_param in filter_params:
                next_page = next_page + '&filter=%s' % unidecode(filter_param)
        # add any order params to url
        if 'order' in self.request.GET:
            order_params = self.request.GET.getall('order')
            for order_param in order_params:
                next_page = next_page + '&order=%s' % unidecode(order_param)
        # return newly built url
        return next_page

    def get_query(self):

        """
        Build and return a dynamic query
        """

        query = self.build_query()
        return query
