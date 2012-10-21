Building RESTful APIs with Nacelle
==================================

Nacelle provides a couple of simple tools to make building RESTful APIs as
simple as possible.  Nacelle's tools allow the building of simple APIs with
full read/write support and the ability to either serve a fixed query or one
specified by the client in the API call.

Building a RESTful API with nacelle requires 2 things, a model and a handler.
(A fully functional Demo app and command lineapi client are available in the
demoapp folder)

Part 1: Defining your model
---------------------------

You can define your model as you normally would, with only 2 additional
requirements.  For read (GET) support your model should implement a get_json()
method which should return a JSON serialisable representation of your model (in
any format, nacelle doesn't care).  For write (POST, DELETE) support, your
model needs to implement a set_json() method which accepts a JSON object and
builds a model instance.

The simplest way to meet this requirement is to include nacelle's JSONMixins in
your model like so:

    >>> from nacelle.models.mixins import JSONMixins
    >>> from google.appengine.ext import db
    >>>
    >>> class YourModel(db.Expando, JSONMixins):
    >>>     pass

You can either use a standard db.Model instance to allow a fixed schema for
your API, or you can choose a db.Expando instance for a schemaless API.

Part 2: Defining your handler
-----------------------------

Nacelle's API handler provides a quick and easy way to build a pageable /
queryable / sortable API from any appengine model instance.

To use nacelle's built-in API handler you simply need to subclass it and
configure a few required options:

    >>> # Dynamically queryable API Handler example
    >>> from nacelle.handlers.api import APIHandler
    >>> from yourapp.models import SomeModel
    >>>
    >>> class DemoAPIHandlerQueryable(APIHandler):
    >>>     model = SomeModel

    >>> # Fixed query API Handler example
    >>> from nacelle.handlers.api import APIHandler
    >>> from yourapp.models import SomeModel
    >>>
    >>> class DemoAPIHandlerFixed(APIHandler):
    >>>     model = SomeModel
    >>>     query = SomeModel.all().filter('someproperty =', 'somevalue')

Nacelle's APIHandler supports the following configuration parameters:

    Required:
        model (db.Model or db.Expando): The model from which to build the API
    Optional:
        query (db.Query): A fixed query for any GET requests
        cache (bool): enable caching via memcache
        cache_key_prefix (string): String to prefix on all cache keys
        cache_time (int): Timeout for cached values in seconds
        allowed_methods (list): List of allowed HTTP methods for this resource

Part 3: Defining your routes
----------------------------

All that's left to do is define your routes.  This is done using webapp2 standard routes and so allows all the flexibility that that provides:

    >>> ROUTES = [
    >>>     (r'/api', 'demoapp.handlers.DemoAPIHandler'),
    >>>     (r'/api/(.*)', 'demoapp.handlers.DemoAPIHandler'),
    >>> ]

Et voila! We have REST! Making API calls is very simple and follows a
consistent pattern.


API Client Documentation:
-------------------------

GET requests to the main resource endpoint accept the following parameters:

    page (int): page number for paginating results
    page_size (int): number of results per page

GET requests to endpoints which do not have a fixed query specified also accept
the following parameters:

    filter (str): filter query to append to query
        filter=field__value: .filter('field =', 'value')
        filter=field__lt__value: .filter('field <', 'value')
        filter=field__gt__value: .filter('field >', 'value')
        filter=field__lte__value: .filter('field <=', 'value')
        filter=field__gte__value: .filter('field >=', 'value')
    order (str): order query on field
        order=field: .order('field')
        order=-field: .order('-field')

POSTing a JSON representation of an entity to the main resource endpoint will create a new entity of the type configured.

    /api:
        GET: Paged JSON response
        POST: Create new entity

GET requests to a specific key url will return a JSON representation of
a specific entity.
POSTing a JSON representation of an entity to the key specific endpoint will
update that entity and save the updated values in the datastore.
DELETE requests to the key spefic endpoint will delete the specified entity.

    /api/key:
        GET: Retrieve JSON representation of entity
        POST: Update entity
        DELETE: Delete entity
