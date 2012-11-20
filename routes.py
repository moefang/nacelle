"""
This file should contain all of the routes for your nacelle project

ROUTES should be a list of lists.  This allows nacelle apps to
specify their own list of routes which can be imported here
"""
# third-party imports
from webapp2_extras.routes import PathPrefixRoute

# import demo routes.  You should probably remove these when you
# have added your own routes
from demoapp.demoapp import ROUTES as demoapp_routes
from jsontime.routes import ROUTES as jsontime_routes
from mailer.routes import ROUTES as mailer_routes

# define all of our project's routes
ROUTES = [
    [
        # Default route to display a welcome page on a new project build
        (r'/', 'nacelle.handlers.default.NewProjectHandler'),
        # Default auth routes for engineauth
        (r'/login', 'nacelle.handlers.auth.LoginHandler'),
        (r'/logout', 'nacelle.handlers.auth.LogoutHandler'),
    ],
    # routes for our demo app
    [PathPrefixRoute('/demo', demoapp_routes)],
    # json time routes module
    jsontime_routes,
    # mailer routes module
    mailer_routes,
]
