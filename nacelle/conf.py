"""
    nacelle microframework

    Simple proxy class to provide access to project
    settings, whether from nacelle's default settings
    or overridden by values in the projects settings
"""
import logging
import sys
import os

# Try to import settings.py from the project root
try:
    import settings as user_settings
except ImportError:
    logging.info('No settings file found, using defaults')

# Import the default settings file
from nacelle import default_settings


class Settings(object):

    """
        Class used to get user configured settings and
        fall back to a default value if not found.
    """
    def __getattr__(self, name):
        try:
            return getattr(user_settings, name)
        except (NameError, AttributeError):
            return getattr(default_settings, name)

# Initialise the Settings class otherwise
# __getattr__ will never be called
settings = Settings()

# weird raven/sentry hack, can't remember why
# it's needed, need to ask Grieve
this_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(this_dir, 'lib'))
from raven import Client
if settings.ENABLE_SENTRY:
    sentry = Client(settings.SENTRY_DSN)
else:
    sentry = None
