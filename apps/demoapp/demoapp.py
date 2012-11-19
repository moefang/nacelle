"""
This is a simple nacelle demo app.

It has been specified in one file for simplicity's sake but
could be laid out and organised however you like
"""
# stdlib imports
import datetime

# third party imports
from google.appengine.ext import db
from webapp2 import Route

# local imports
from nacelle.handlers.api import DynamicQueryAPIHandler
from nacelle.handlers.api import FixedQueryAPIHandler
from nacelle.handlers.base import JSONHandler
from nacelle.decorators.cache import memorise
from nacelle.models.base import JSONModel
from nacelle.utils import counter
from nacelle.utils.datastore import count_query


class DemoModel(JSONModel):

    """
    Define a simple model to use for our demo. JSONModel is
    an Expando model so we don't need to explicitly define
    any fields, however, the handlers below work equally well
    with reqular db.Model instances.
    """

    pass


class DemoMemoHandler(JSONHandler):

    """
    Very simple demo handler showing the capabilities
    of nacelle's built in caching decorator
    """

    # using the memorise decorator for easy memcache support
    @memorise(ttl=60)
    def get_context(self):

        """
        Override the get_context method to provide a dictionary
        for serialisation
        """

        return {'time': datetime.datetime.utcnow().isoformat()}


class DemoCountHandler(JSONHandler):

    """
    Simple handler to illustrate nacelle's built in count functions.
    While these functions do their best to count datastore entities
    efficiently, this is always going to be a suboptimal solution for
    any problem due to the nature of appengine.  If at all possible
    you should avoid attempting to count datastore entities synchronously.
    A better solution in this case would be to make use of nacelle's
    sharded counter support.
    """

    def get_context(self):

        # count DemoModel records
        count = count_query(DemoModel.all(keys_only=True))
        # return dict for serialisation
        return {'count': count}

    def post(self):

        """
        To provide POST support for a handler, simply define a post() method
        """

        # build 100 new DemoModel instances (for testing purposes)
        instances = [DemoModel(someint=1) for x in range(100)]
        # store the newly created DemoModel instances
        db.put(instances)
        # return a JSON response to the client
        return self.json_response({'status': '200 OK'})


class DemoQueryHandler(FixedQueryAPIHandler):

    """
    This handler makes use of nacelle's FixedQueryAPIHandler to provide a
    read/write API for DemoModel with a fixed query for the root listview
    """

    # specify the model type on which the handler will operate
    # this is only necessary when the handler makes use of POST
    # or DELETE support
    model = DemoModel
    # default page size for results returned from this handler
    page_size = 100
    # allowed HTTP methods for this handler
    allowed_methods = ['GET', 'POST']

    def get_query(self):

        """
        The get_query() method of FixedQueryAPIHandler should be overridden
        to provide a query for any list requests
        """

        # build and return a query
        return DemoModel.all()


class DemoDynamicQueryHandler(DynamicQueryAPIHandler):

    """
    This handler makes use of nacelle's DynamicQueryAPIHandler to provide a
    read/write API for DemoModel with a dynamic query for the root listview
    which is specified in query params
    """

    # default page size for results returned from this handler
    page_size = 100
    # specify the model type on which the handler will operate
    model = DemoModel
    # allowed HTTP methods for this handler
    allowed_methods = ['GET', 'POST']


class DemoCounterAPIHandler(JSONHandler):

    """
    This handler demonstrates the use of nacelle's simple sharded counters
    """

    def get(self):

        """
        Retrieve and return the specified counter's value
        """

        # retireve counter value
        hit_count = counter.get_count('hit_count')
        # return counter value as JSON object
        self.json_response({'status': '200 OK', 'hit_count': hit_count})

    def post(self):

        """
        Increment and return the specified counter's value
        """

        # increment the specified counter
        counter.increment('hit_count')
        # get the counter value
        hit_count = counter.get_count('hit_count')
        # return the counter value as JSON object
        self.json_response({'status': '200 OK', 'hit_count': hit_count})


# Define the required routes for our demo app
ROUTES = [
    # memcache handler route
    Route(r'/memorise', 'demoapp.demoapp.DemoMemoHandler'),
    # entity count handler route
    Route(r'/count', 'demoapp.demoapp.DemoCountHandler'),
    # fixed query handler routes
    Route(r'/fixed_query', 'demoapp.demoapp.DemoQueryHandler'),
    Route(r'/fixed_query/(.*)', 'demoapp.demoapp.DemoQueryHandler'),
    # dynamic query handler routes
    Route(r'/dynamic_query', 'demoapp.demoapp.DemoDynamicQueryHandler'),
    Route(r'/dynamic_query/(.*)', 'demoapp.demoapp.DemoDynamicQueryHandler'),
    # sharded counter handler route
    Route(r'/hitcount', 'demoapp.demoapp.DemoCounterAPIHandler'),
]
