"""
All WSGI middleware should be applied here
"""


def webapp_add_wsgi_middleware(app):
    # app = recording.appstats_wsgi_middleware(app)
    return app
