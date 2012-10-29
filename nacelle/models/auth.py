from google.appengine.ext import db


class AdminUser(db.Model):
    email = db.EmailProperty()
