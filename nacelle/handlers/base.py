"""
    nacelle microframework

    These are our base handlers which all others should inherit from
"""
import logging
import sys
import webapp2
from nacelle import error
from nacelle.conf import settings
from nacelle.conf import sentry


class BaseHandler(webapp2.RequestHandler):

    def handle_exception(self, exception, debug):

        # Log the exception
        logging.exception(exception)

        # collect our error data
        exc_info = sys.exc_info()
        error_report = {
                'method': self.request.method,
                'url': self.request.path_url,
                'query_string': self.request.query_string,
                # 'data': environ.get('wsgi.input'),
                'headers': dict(self.request.headers),
                'env': dict((
                        ('REMOTE_ADDR', self.request.environ['REMOTE_ADDR']),
                        ('SERVER_NAME', self.request.environ['SERVER_NAME']),
                        ('SERVER_PORT', self.request.environ['SERVER_PORT']),
                    )),
            }

        if settings.ENABLE_SENTRY:
            # Log the error to sentry
            sentry.capture('Exception',
                exc_info=exc_info,
                data={'sentry.interfaces.Http': error_report},
            )

        # Set a custom message.
        if settings.DEBUG:
            if hasattr(self, 'template_response'):
                error.render_html(self)
            elif hasattr(self, 'json_response'):
                frames = []
                for frame in error._get_frames(exc_info[2], False):
                    new_frame = {}
                    for k, v in frame.__dict__.items():
                        new_frame[k] = str(v)
                    frames.append(new_frame)
                exc_info_str = {
                    'exc_type': str(exc_info[0]),
                    'exc_value': str(exc_info[1]),
                }
                response = {'exc_info': exc_info_str, 'error_report': error_report, 'traceback': frames}
                self.json_response(response)
        else:
            self.response.write('Oops... An error occurred.')

        # If the exception is a HTTPException, use its error code.
        # Otherwise use a generic 500 error code.
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
        else:
            self.response.set_status(500)
