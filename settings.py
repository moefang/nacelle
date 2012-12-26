"""
Nacelle Microframework
Copyright (c) Patrick Carey 2012

Project settings file for your nacelle project go in this file
"""
# stdlib imports
import os

# PROJECT SETTINGS
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# When debug is enabled, error pages will contain full tracebacks
DEBUG = True

# Sentry settings
ENABLE_SENTRY = True
SENTRY_DSN = ''

# Additional template extensions and filters to
# be applied to any Jinja instances
TEMPLATE_EXTENSIONS = []
TEMPLATE_FILTERS = []

# Dictionary that is passed to our WSGI app to provide extra webapp2 config
# set our super secret session key
WSGI_CONFIG = {}
WSGI_CONFIG['webapp2_extras.sessions'] = {
    'secret_key': '',
    'session_max_age': 3600 * 24,
}
