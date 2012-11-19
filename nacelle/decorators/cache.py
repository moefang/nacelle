"""
A collection of cache related decorators for nacelle
"""
# stdlib imports
import inspect
import itertools
from functools import wraps
from hashlib import md5

# third-party imports
from google.appengine.api import memcache


class memorise(object):

        """
        Decorate any function or class method/staticmethod with a memcache
        enabled caching wrapper. An MD5 hash of values, such as attributes
        on the parent instance/class, and arguments, is used as a unique
        key in memcache.

        parent_keys (list): A list of attributes in the parent instance or
                            class to use for key hashing.
                 ttl (int): Tells memcached the time which this value should
                            expire. We default to 0 == cache forever. None is
                            turn off caching.
             update (bool): Force cache update.
        """

        def __init__(self, parent_keys=[], ttl=0, update=False):
                # Instantiate some default values, and customisations
                self.parent_keys = parent_keys
                self.ttl = ttl
                self.update = update
                self.mc = memcache

        def __call__(self, fn):
                @wraps(fn)
                def wrapper(*args, **kwargs):
                        # Get a list of arguement names from the func_code
                        # attribute on the function/method instance, so we can
                        # test for the presence of self or cls, as decorator
                        # wrapped instances lose frame and no longer contain a
                        # reference to their parent instance/class within this
                        # frame
                        argnames = fn.func_code.co_varnames[:fn.func_code.co_argcount]
                        method = False
                        static = False
                        if len(argnames) > 0:
                                if argnames[0] == 'self' or argnames[0] == 'cls':
                                        method = True
                                        if argnames[0] == 'cls':
                                                static = True

                        arg_values_hash = []
                        # Grab all the keyworded and non-keyworded arguements so
                        # that we can use them in the hashed memcache key
                        for i, v in sorted(itertools.chain(itertools.izip(argnames, args), kwargs.iteritems())):
                                if i != 'self':
                                        if i != 'cls':
                                                arg_values_hash.append("%s=%s" % (i, v))

                        class_name = None
                        if method:
                                keys = []
                                if len(self.parent_keys) > 0:
                                        for key in self.parent_keys:
                                                keys.append("%s=%s" % (key, getattr(args[0], key)))
                                keys = ','.join(keys)
                                if static:
                                # Get the class name from the cls argument
                                        class_name = args[0].__name__
                                else:
                                # Get the class name from the self argument
                                        class_name = args[0].__class__.__name__
                                module_name = inspect.getmodule(args[0]).__name__
                                parent_name = "%s.%s[%s]::" % (module_name, class_name, keys)
                        else:
                                # Function passed in, use the module name as the
                                # parent
                                parent_name = inspect.getmodule(fn).__name__
                        # Create a unique hash of the function/method call
                        key = "%s%s(%s)" % (parent_name, fn.__name__, ",".join(arg_values_hash))
                        key = md5(key).hexdigest()

                        # Try and get the value from memcache
                        output = self.mc.get(key)
                        exist = True
                        if not output:
                                exist = False
                                # Otherwise get the value from
                                # the function/method
                                output = fn(*args, **kwargs)
                        if self.update or not exist:
                                if output is None:
                                        set_value = memcache_none()
                                else:
                                        set_value = output
                                # And push it into memcache
                                if self.ttl is not None:
                                        self.mc.set(key, set_value, time=self.ttl)
                        if output.__class__ is memcache_none:
                                # Because not-found keys return
                                # a None value, we use the
                                # memcache_none stub class to
                                # detect these, and make a
                                # distinction between them and
                                # actual None values
                                output = None
                        return output
                return wrapper


class memcache_none:

        """
        Stub class for storing None values in memcache,
        so we can distinguish between None values and not-found
        entries.
        """

        pass
