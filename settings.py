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
