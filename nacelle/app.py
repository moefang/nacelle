"""
Nacelle microframework
Copyright (C) Patrick Carey 2012

This is our main WSGI entry point so any initial setup should happen here
"""
# Add 'lib' and 'apps' dirs to the python path
import os
import sys


def find_lib_directories(root):

    """
    Walk the project tree and find any lib directories so that we can
    add them to the path before running our app
    """

    for r, d, f in os.walk(root):
        for dirname in d:
            if dirname == 'lib':
                yield os.path.join(r, dirname)


PROJECT_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)

# Find lib directories and add them to the python path
LIB_DIRS = find_lib_directories(PROJECT_ROOT)
for directory in LIB_DIRS:
    sys.path.insert(0, directory)

# Add our 'apps' directory to the system path
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'apps'))

# import required modules
import settings
import routes
import itertools
import webapp2

# Create one big list from our list of route lists
ROUTES = list(itertools.chain.from_iterable(routes.ROUTES))

# Define our WSGI app so GAE can run it
wsgi = webapp2.WSGIApplication(ROUTES, debug=settings.DEBUG, config=settings.WSGI_CONFIG)
