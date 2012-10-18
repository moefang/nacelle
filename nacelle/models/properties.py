"""
    nacelle microframework
"""
from google.appengine.ext import db


class DerivedProperty(db.Property):

    """
    Custom property to store calculated properties in your db models
    """

    def __init__(self, derive_func, *args, **kwargs):
        super(DerivedProperty, self).__init__(*args, **kwargs)
        self.derive_func = derive_func

    def __get__(self, model_instance, model_class):
        if model_instance is None:
            return self
        return self.derive_func(model_instance)

    def __set__(self, model_instance, value):
        raise db.DerivedPropertyError("Cannot assign to a DerivedProperty")
