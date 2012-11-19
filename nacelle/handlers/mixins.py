"""
A collection of useful handler mixins for nacelle
"""
# stdlib imports
import json
import logging
import os
import sys

# third-party imports
import webapp2
from webapp2_extras import jinja2

# local imports
import settings
from nacelle import error
from nacelle import sentry


class TemplateMixins(object):

    """
    This class contains a collection of useful mixins for template related
    functions such as locating template directories and rendering templates
    """

    def get_template_dirs(self):

        """
        Find all directories within the project called 'templates' and build
        a Jinja2 FileSystemLoader for each one
        """

        # loop over all directories in project
        for root, dirs, files in os.walk(settings.PROJECT_ROOT):
            # check if any template directories present
            for dirname in dirs:
                if dirname == 'templates':
                    # build and yield a FileSystemLoader for each template directory
                    yield jinja2.jinja2.FileSystemLoader(os.path.join(root, dirname))

    def get_jinja2(self, factory=jinja2.Jinja2, app=None, config=None):

        """
        Build and return a configured Jinja" instance cached in the app registry
        """

        # registry key
        key = 'webapp2_extras.jinja2.Jinja2'
        # get current WSGI app
        app = app or webapp2.get_app()
        # attempt to get jinja instance from app registry
        jinja2 = app.registry.get(key)
        if not jinja2:
            # build and cache jinja instance
            jinja2 = app.registry[key] = factory(app, config)
        # return jinja instance
        return jinja2

    @webapp2.cached_property
    def jinja2(self):

        """
        Configure and return an initialised jinja instance
        """

        # build a choiceloader from our found template directories
        template_loader = jinja2.jinja2.ChoiceLoader(self.get_template_dirs())
        # define our default template extensions
        template_extensions = [
            'jinja2.ext.autoescape',
            'jinja2.ext.with_',
        ]
        # add any defined template extensions from settings file
        if hasattr(settings, 'TEMPLATE_EXTENSIONS'):
            for ext in settings.TEMPLATE_EXTENSIONS:
                template_extensions.append(ext)

        # add any defined template filters from settings file
        if hasattr(settings, 'TEMPLATE_FILTERS'):
            filters = settings.TEMPLATE_FILTERS
        else:
            filters = None

        # build our jinja config
        config = {
            'template_path': 'templates',
            'compiled_path': None,
            'force_compiled': False,
            'environment_args': {
                'loader': template_loader,
                'autoescape': True,
                'extensions': template_extensions,
            },
            'globals': None,
            'filters': filters,
        }
        # Returns a Jinja2 renderer cached in the app registry.
        return self.get_jinja2(app=self.app, config=config)

    def template_response(self, _template, **context):

        """
        Renders a template and writes the result to the response.
        """

        # render template with supplied context
        rv = self.jinja2.render_template(_template, **context)
        # write rendered template to response
        self.response.write(rv)

    def handle_exception(self, exception, debug):

        """
        Override handle_exception() to provide nicely rendered debug
        pages when in DEBUG mode.  Also logs any errors to a sentry
        server if configured to do so.
        """

        # collect our error data
        exc_info = sys.exc_info()

        # Log the exception
        logging.exception(exception)

        # log error to sentry
        sentry.capture_exception(self.request, exc_info)

        # If the exception is a HTTPException, use its error code.
        # Otherwise use a generic 500 error code.
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
            status_code = exception.code
        else:
            self.response.set_status(500)
            status_code = 500

        # Set a custom message.
        if settings.DEBUG:
            # render debug error page
            error.render_html(self)
        else:
            # render 404 page if not found
            if status_code == 404:
                self.template_response('404.html')
            # otherwise render the standard 500 page
            else:
                self.template_response('500.html')


class JSONMixins(object):

    """
    This class contains a collection of useful mixins for template related
    functions such as locating template directories and rendering templates
    """

    def json_response(self, response_object):

        """
        Accepts a JSON encoded string or object which can be serialised to
        JSON and outputs it to the response as a JSON encoded string.
        """

        # if object is a string just return as is
        if isinstance(response_object, basestring):
            self.response.write(response_object)
        # else attempt to serialise and return
        else:
            response_object = json.dumps(response_object)
            self.response.write(response_object)
        # set the right content-type header
        self.response.headers['Content-Type'] = 'application/json'

    def handle_exception(self, exception, debug):

        """
        Override handle_exception() to provide JSON encoded debug
        messages.  Also logs any errors to a sentry server if
        configured to do so.
        """

        # If the exception is a HTTPException, use its error code.
        # Otherwise use a generic 500 error code.
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
            status_code = exception.code
        else:
            self.response.set_status(500)
            status_code = 500

        # collect our error data
        exc_info = sys.exc_info()

        # Log the exception
        logging.exception(exception)

        # log error to sentry
        sentry.capture_exception(self.request, exc_info)

        # Set a custom message.
        if settings.DEBUG:
            # format exception as JSON object
            exc_info_str = {
                'exc_type': str(exc_info[0]),
                'exc_value': str(exc_info[1]),
            }
            response = {'exc_info': exc_info_str}
            self.json_response(response)
        else:
            # return simple error msg if 500
            if status_code == 500:
                self.json_response({'error': 'A server error has occurred'})
            # otherwise return the error message's value
            else:
                self.json_response({'error': exc_info[1]})
