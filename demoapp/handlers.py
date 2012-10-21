# stdlib imports
import datetime
import time

# local imports
from nacelle.handlers.api import APIHandler
from nacelle.handlers.base import BaseHandler
from nacelle.handlers.mixins import JSONMixins
from nacelle.decorators.cache import memorise
from demoapp.models import DemoModel


class DemoMemoHandler(BaseHandler, JSONMixins):

    def get(self):
        output = self.get_output()
        self.json_response(output)

    @memorise(ttl=60)
    def get_output(self):
        time.sleep(5)
        return {'time': datetime.datetime.now().isoformat()}


class DemoAPIHandler(APIHandler):

    model = DemoModel
    query = DemoModel.all().filter('randomnum <=', 5000).order('randomnum')
    cache_key_prefix = 'demo-api'
    cache = True
    cache_time = 60
