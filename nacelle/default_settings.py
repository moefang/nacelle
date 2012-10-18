import os

# PROJECT SETTINGS
PROJECT_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)
DEBUG = True

# Sentry settings
ENABLE_SENTRY = False

# Add a default route to show the nacelle welcome page
ROUTES = [[
    (r'/', 'nacelle.handlers.default.NewProjectHandler'),
    (r'/raisetemplate', 'nacelle.handlers.default.TemplateRaiseHandler'),
    (r'/raisejson', 'nacelle.handlers.default.JSONRaiseHandler'),
]]
