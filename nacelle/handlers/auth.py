# local imports
from nacelle.handlers.base import TemplateHandler


class LoginHandler(TemplateHandler):

    template = 'login.html'

    def get_context(self):

        if 'next' in self.request.GET:
            context = {'next': self.request.GET['next']}
        else:
            context = {}

        return context

    def post(self):
        # call get method when POST
        self.get()


class LogoutHandler(TemplateHandler):

    def get(self):

        # delete the cookie to log the user out
        self.response.delete_cookie('_eauth')

        # get redirect
        next = self.request.get('next', default_value=None)

        # redirect the user after logging out
        if next is not None:
            self.redirect(next)
        else:
            self.redirect('/')
