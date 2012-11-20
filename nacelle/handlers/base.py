"""
    nacelle microframework

    These are our base handlers which all others should inherit from
"""
# third-party imports
from google.appengine.ext import ndb
import webapp2

# local imports
from nacelle.handlers.mixins import JSONMixins
from nacelle.handlers.mixins import TemplateMixins


class TemplateHandler(TemplateMixins, webapp2.RequestHandler):

    """
    Simple handler to provide a simple method of rendering a
    template with a specified context.
    """

    # name of the template to use for rendering
    template = None

    def get_messages(self, key='_messages'):
            try:
                return self.request.session.data.pop(key)
            except KeyError:
                return None

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

        session = self.request.session if self.request.session else None
        user = self.request.user if self.request.user else None
        profiles = None

        if user:
            profile_keys = [ndb.Key('UserProfile', p) for p in user.auth_ids]
            profiles = ndb.get_multi(profile_keys)

            # add user details to context if logged in
            context['user'] = user
            context['session'] = session
            context['profiles'] = profiles
            context['user_id'] = user.auth_ids[0].split(':', 1)[1]

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


class JSONHandler(JSONMixins, webapp2.RequestHandler):

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

    def get(self):

        """
        Handles all HTTP GET requests for TemplateHandler
        """

        # build dictionary to be serialised
        context = self.get_context()
        # serialise ad return dictionary as JSON object
        return self.json_response(context)
