# stdlib imports
import datetime
import time

# local imports
from nacelle.handlers.api import APIHandler
from nacelle.handlers.base import BaseHandler
from nacelle.handlers.mixins import JSONMixins
from nacelle.decorators.cache import memorise
from nacelle.models.base import JSONModel


class DemoModel(JSONModel):
    """
    Simple Expando model allowing storage of arbitrary JSON objects
    """
    pass


class DemoMemoHandler(BaseHandler, JSONMixins):

    """
    Simple demo handler showing the capabilities of nacelle's built in caching
    """

    def get(self):
        output = self.get_output()
        self.json_response(output)

    # using the memorise decorator for easy memcache support
    @memorise(ttl=60)
    def get_output(self):
        time.sleep(5)
        return {'time': datetime.datetime.now().isoformat()}


class DemoAPIHandlerFixed(APIHandler):

    """
    API Handler with a fixed query and caching enabled
    """

    model = DemoModel
    query = DemoModel.all().filter('randomnum <=', 250000).order('randomnum')
    cache_key_prefix = 'demo-api-fixed'
    cache = True
    cache_time = None
    auth = {
        'GET': 'all',
        'POST': 'all',
        'DELETE': 'all'
    }


class DemoAPIHandlerDynamic(APIHandler):

    """
    API Handler with no fixed query and caching disabled
    """

    model = DemoModel
    allowed_methods = ['GET']


ROUTES = [
    (r'/memorise', 'demoapp.demoapp.DemoMemoHandler'),
    (r'/api/fixed', 'demoapp.demoapp.DemoAPIHandlerFixed'),
    (r'/api/fixed/(.*)', 'demoapp.demoapp.DemoAPIHandlerFixed'),
    (r'/api/dynamic', 'demoapp.demoapp.DemoAPIHandlerDynamic'),
    (r'/api/dynamic/(.*)', 'demoapp.demoapp.DemoAPIHandlerDynamic'),
]
