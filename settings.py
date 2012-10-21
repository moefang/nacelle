# Project Settings
DEBUG = True

# Sentry settings
ENABLE_SENTRY = False
SENTRY_DSN = ''


TEMPLATE_EXTENSIONS = []

ROUTES = [[
    (r'/memorise', 'demoapp.handlers.DemoMemoHandler'),
    (r'/api', 'demoapp.handlers.DemoAPIHandler'),
    (r'/api/(.*)', 'demoapp.handlers.DemoAPIHandler'),
]]
