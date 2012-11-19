"""
A collection of decorators used for applying access
control to a handler method
"""
# third-party imports
from google.appengine.api import users

# local imports
from nacelle.models.auth import AdminUser
from nacelle.decorators.well_behaved import well_behaved


@well_behaved
def login_required(func):

    """
    Handler methods decorated with this function will
    be restricted to logged in users only
    """

    def wrap(self, *args, **kwargs):

        # get current user object
        user = users.get_current_user()
        if user:
            # return method as normal if user logged in
            return func(self, *args, **kwargs)
        else:
            # redirect user to login page if not logged in
            self.redirect(users.create_login_url(self.request.uri))

    return wrap


@well_behaved
def admin_required(func):

    """
    Handler methods decorated with this function will
    be restricted to logged in admin users only
    """

    def wrap(self, *args, **kwargs):

        # check if handler has been invoked by a task queue
        if 'X-AppEngine-TaskName' in self.request.headers:
            # allow access to handler
            return func(self, *args, **kwargs)

        # get current user object
        user = users.get_current_user()
        # get any configured AdminUser emails
        admin_emails = [u.email for u in AdminUser.all()]

        # check if user is logged in
        if user:
            # check if user is registered appengine admin
            if users.is_current_user_admin():
                return func(self, *args, **kwargs)
            # check if user is registered AdminUser
            elif user.email() in admin_emails:
                return func(self, *args, **kwargs)
            # otherwise abort with 403
            else:
                self.abort(403)
        else:
            # redirect user to login page
            self.redirect(users.create_login_url(self.request.uri))

    return wrap
