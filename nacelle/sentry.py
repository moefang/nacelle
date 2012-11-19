"""
Useful sentry related functions for use in a nacelle project
"""
# third-party imports
from raven import Client

# local imports
import settings


# check if sentry enabled
if settings.ENABLE_SENTRY:
    sentry = Client(settings.SENTRY_DSN)


def capture_exception(request, exc_info):

    """
    Report an error to a specified sentry server
    """

    # abort if sentry disabled
    if not settings.ENABLE_SENTRY:
        return None

    # build our error report
    error_report = {
            'method': request.method,
            'url': request.path_url,
            'query_string': request.query_string,
            # 'data': environ.get('wsgi.input'),
            'headers': dict(request.headers),
            'env': dict((
                    ('REMOTE_ADDR', request.environ['REMOTE_ADDR']),
                    ('SERVER_NAME', request.environ['SERVER_NAME']),
                    ('SERVER_PORT', request.environ['SERVER_PORT']),
                )),
        }

    # Log the error to sentry
    sentry.capture('Exception',
        exc_info=exc_info,
        data={'sentry.interfaces.Http': error_report},
    )
