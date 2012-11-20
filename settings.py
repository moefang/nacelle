"""
Projects settings file for your nacelle project
"""
# stdlib imports
import os

# PROJECT SETTINGS
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
# When debug is enabled, error pages will contain full tracebacks
DEBUG = True

# Sentry settings
ENABLE_SENTRY = True
SENTRY_DSN = 'http://41f3eb61604f4bedbb24bfcce03b102b:4471a09a79bc4df2a25bf5434c4c7963@sentry.wackwack.co.uk/9'

# Additional template extensions and filters to
# be applied to any Jinja instances
TEMPLATE_EXTENSIONS = []
TEMPLATE_FILTERS = []

# Define engineauth config here if required engine auth
# is used to provide federated login for nacelle and allows
# login via various providers such as in the examples below

engineauth = {
    'secret_key': '24bfcce03b102b4471a09a79bc4df2a25bf5434c4c79',
    'user_model': 'engineauth.models.User',
}

engineauth['provider.auth'] = {
    'user_model': 'engineauth.models.User',
    'session_backend': 'datastore',
}

# Facebook Authentication
# engineauth['provider.facebook'] = {
#     'client_id': 'CHANGE_TO_FACEBOOK_APP_ID',
#     'client_secret': 'CHANGE_TO_FACEBOOK_CLIENT_SECRET',
#     'scope': 'email',
# }

# Google Plus Authentication
# engineauth['provider.google'] = {
#     'client_id': 'CHANGE_TO_GOOGLE_CLIENT_ID',
#     'client_secret': 'CHANGE_TO_GOOGLE_CLIENT_SECRET',
#     'api_key': 'CHANGE_TO_GOOGLE_API_KEY',
#     'scope': 'https://www.googleapis.com/auth/plus.me',
# }

# Twitter Authentication
engineauth['provider.twitter'] = {
    'client_id': 'npfrn1kMGlG2rFVfhwkDZQ',
    'client_secret': 'U3VUSElleb2QHRG37gvSftZVxNiQJnIR3RN54tRdk4',
}
