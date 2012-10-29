from google.appengine.api import users
from nacelle.models.auth import AdminUser
from nacelle.decorators.well_behaved import well_behaved


@well_behaved
def login_required(func):
    def wrap(self, *args, **kwargs):
        user = users.get_current_user()
        if user:
            return func(self, *args, **kwargs)
        else:
            self.redirect(users.create_login_url(self.request.uri))
    return wrap


@well_behaved
def admin_required(func):
    def wrap(self, *args, **kwargs):
        if 'X-AppEngine-TaskName' in self.request.headers:
            return func(self, *args, **kwargs)
        user = users.get_current_user()
        admin_emails = [u.email for u in AdminUser.all()]
        if user:
            if users.is_current_user_admin():
                return func(self, *args, **kwargs)
            elif user.email() in admin_emails:
                return func(self, *args, **kwargs)
            else:
                self.redirect('/admin/denied')
        else:
            self.redirect(users.create_login_url(self.request.uri))
    return wrap


@well_behaved
def auth_control(func):
    def wrap(self, *args, **kwargs):
        allowed_auth = self.auth[self.request.method]
        if allowed_auth is None:
            self.abort(403)
        elif allowed_auth == 'all':
            return func(self, *args, **kwargs)
        elif allowed_auth == 'login':
            user = users.get_current_user()
            if user:
                return func(self, *args, **kwargs)
            else:
                self.redirect(users.create_login_url(self.request.uri))
        elif allowed_auth == 'admin':
            if 'X-AppEngine-TaskName' in self.request.headers:
                return func(self, *args, **kwargs)
            user = users.get_current_user()
            admin_emails = [u.email for u in AdminUser.all()]
            if user:
                if users.is_current_user_admin():
                    return func(self, *args, **kwargs)
                elif user.email() in admin_emails:
                    return func(self, *args, **kwargs)
                else:
                    self.abort(403)
            else:
                self.redirect(users.create_login_url(self.request.uri))
        else:
            self.abort(403)
    return wrap
