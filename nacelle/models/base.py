"""
Collection of simple Base models which can
be used in any nacelle project
"""
# third-party imports
from google.appengine.ext import db

# local imports
from nacelle.models.mixins import JSONMixins


class JSONModel(db.Expando, JSONMixins):

    """
    A simple expando model with JSON mixins to
    support serialisation to/from JSON
    """

    pass
