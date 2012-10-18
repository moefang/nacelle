def webapp_add_wsgi_middleware(app):
    from google.appengine.ext.appstats import recording
    # from nacelle.middleware.cachecontrol import CacheControlMiddleware
    app = recording.appstats_wsgi_middleware(app)
    # app = CacheControlMiddleware(app, 300)
    return app
