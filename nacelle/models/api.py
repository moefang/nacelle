from google.appengine.ext import db


class CacheKey(db.Model):
    par_key = db.StringProperty()
    cache_keys = db.StringListProperty()
