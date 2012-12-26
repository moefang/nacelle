"""
A simple collection of handlers that are used in a new project
"""
# local imports
from nacelle.handlers.base import JSONHandler
from nacelle.handlers.base import TemplateHandler


class NewProjectHandler(TemplateHandler):

    """
    Default index handler for all new nacelle projects
    """

    template = 'welcometonacelle.html'


class TemplateRaiseHandler(TemplateHandler):

    """
    Handler to demonstrate the template debug error page
    """

    def get_context(self):
        self.abort(500)


class JSONRaiseHandler(JSONHandler):

    """
    Handler to demonstrate the JSON debug messages
    """

    def get_context(self):
        self.abort(500)
