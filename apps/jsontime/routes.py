"""
Necessary routes for the jsontime nacelle app
"""
# third-party imports
from webapp2_extras.routes import RedirectRoute

# Define the required routes for the time app
ROUTES = [
    # time handler route
    RedirectRoute(r'/json_time', 'jsontime.handlers.TimeAPIHandler', strict_slash=True, name='jsontime'),
]
