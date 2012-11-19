"""
This module contains useful decorators for wrapping handler methods
"""


class conditional_decorator(object):

    """
    Decorate a decorator with this function to make it
    execute only when condition is True
    """

    def __init__(self, dec, condition):
        self.decorator = dec
        self.condition = condition

    def __call__(self, func):
        # check if condition is met
        if not self.condition:
            # Return the function unchanged, not decorated.
            return func
        return self.decorator(func)
