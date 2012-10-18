from google.appengine.ext import db
from nacelle.models.mixins import JSONMixins


class JSONModel(db.Expando, JSONMixins):

    pass
