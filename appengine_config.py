"""
All WSGI middleware should be applied here
"""
# stdlib imports
import os
import sys

# we need to make sure our lib dir is on the path
# before doing any settings stuff
this_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(this_dir, 'nacelle', 'lib'))

# local imports
import settings

# check if auth middleware is configured
enable_auth = hasattr(settings, 'engineauth')

if enable_auth:
    # get engineauth settings from settings file
    engineauth = settings.engineauth


def webapp_add_wsgi_middleware(app):
    # from google.appengine.ext.appstats import recording
    # from nacelle.middleware.cachecontrol import CacheControlMiddleware
    # app = recording.appstats_wsgi_middleware(app)
    # app = CacheControlMiddleware(app, 300)
    if enable_auth:
        from engineauth import middleware
        app = middleware.AuthMiddleware(app)
    return app
