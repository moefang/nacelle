"""
Nacelle microframework
Copyright (C) Patrick Carey 2012

These are our base handlers which all others should inherit from
"""
# stdlib imports
import uuid

# third-party imports
import webapp2
from webapp2_extras import sessions

# local imports
from nacelle.handlers.mixins import JSONMixins
from nacelle.handlers.mixins import TemplateMixins


class BaseHandler(webapp2.RequestHandler):

    def dispatch(self):

        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        # Set a CSRF token for this request if there is None
        csrf_token = self.session.get('csrf_token', None)
        if csrf_token is None:
            self.session['csrf_token'] = str(uuid.uuid4())

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):

        # Returns a session using the default cookie key.
        return self.session_store.get_session()


class TemplateHandler(TemplateMixins, BaseHandler):

    """
    Simple handler to provide a simple method of rendering a
    template with a specified context.
    """

    # name of the template to use for rendering
    template = None

    def get_messages(self):
        try:
            return self.session.pop('messages')
        except KeyError:
            return None

    def add_message(self, message):
        self.session['messages'].append(message)

    @property
    def default_context(self):

        """
        Builds a default context for all TemplateHandler
        requests that will be present in every subclass

        Returns:
            dict: dictionary of key/value pairs to render into all templates
        """

        # empty dictionary for context
        context = {}
        # add the request object to the template context
        context['request'] = self.request
        # add any messages to the context
        context['messages'] = self.get_messages()
        context['session'] = self.session

        # return the default context
        return context

    def get_context(self):

        """
        This method should be overridden to provide any additional
        context when rendering the specified template

        Returns:
            dict: dictionary of key/value pairs to render into template
        """

        # return empty dict unless overridden
        return {}

    def get(self):

        """
        Handles all HTTP GET requests for TemplateHandler
        """

        # build default context object
        context = self.default_context
        # update default context object with additional context
        context.update(self.get_context())
        # render the context into a Jinja2 template and return it
        return self.template_response(self.template, **context)


class JSONHandler(JSONMixins, BaseHandler):

    """
    Simple handler to build and return a JSON object
    """

    def get_context(self):

        """
        This method should be overridden to build a dictionary
        that can be serialised to JSON and returned.

        Returns:
            dict: dictionary of key/value pairs to serialise
        """

        # return empty dict unless overridden
        return {}

    def get(self, *args, **kwargs):

        """
        Handles all HTTP GET requests for TemplateHandler
        """

        # build dictionary to be serialised
        context = self.get_context(*args, **kwargs)
        # serialise ad return dictionary as JSON object
        return self.json_response(context)
