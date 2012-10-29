"""
    nacelle microframework

    this is our main wsgi entry point so any initial setup should happen here
"""
# Add 'lib' dir to the python path
import os
import sys
PROJECT_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)
this_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(this_dir, 'lib'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'apps'))

# import required modules
from nacelle.conf import settings

import itertools
import webapp2

# Create one big list from our list of route lists
ROUTES = list(itertools.chain.from_iterable(settings.ROUTES))

# Define our WSGI app so GAE can run it
wsgi = webapp2.WSGIApplication(ROUTES, debug=settings.DEBUG)
