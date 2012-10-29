from demoapp import routes as demo_routes
from mailer import routes as mailer_routes

ROUTES = [
    [
        # Default routes
        (r'/', 'nacelle.handlers.default.NewProjectHandler'),
        (r'/raisetemplate', 'nacelle.handlers.default.TemplateRaiseHandler'),
        (r'/raisejson', 'nacelle.handlers.default.JSONRaiseHandler'),
    ],
    demo_routes,
    mailer_routes,
]

routes = ROUTES
