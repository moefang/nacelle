"""
Auth related models for nacelle
"""
# third-party imports
from google.appengine.ext import db

# local imports
from nacelle.models.validators import validate_email


class AdminUser(db.Model):

    """
    Stores email addresses of additional users who should
    be allowed to access any admin only areas of the site.
    """

    # email address
    email = db.EmailProperty(validator=validate_email)
