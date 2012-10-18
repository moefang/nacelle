from nacelle.handlers.base import BaseHandler
from nacelle.handlers.mixins import TemplateMixins
from nacelle.handlers.mixins import JSONMixins


class NewProjectHandler(BaseHandler, TemplateMixins):

    def get(self):
        return self.template_response('welcometonacelle.html', **{})


class TemplateRaiseHandler(BaseHandler, TemplateMixins):

    def get(self):
        self.abort(500)


class JSONRaiseHandler(BaseHandler, JSONMixins):

    def get(self):
        self.abort(500)
