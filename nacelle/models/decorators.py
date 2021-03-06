"""
Collection of model decorators for the nacelle microframework
"""
# local imports
from nacelle.models.properties import DerivedProperty


def derived_property(derive_func=None, *args, **kwargs):

    """
    Use this function as a function decorator to store
    calculated properties in your models
    """

    if derive_func:
        # Regular invocation
        return DerivedProperty(derive_func, *args, **kwargs)
    else:
        # Decorator function
        def decorate(decorated_func):
            return DerivedProperty(decorated_func, *args, **kwargs)
        return decorate
