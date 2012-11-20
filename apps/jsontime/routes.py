"""
Necessary routes for the jsontime nacelle app
"""
# third-party imports
from webapp2 import Route

# Define the required routes for the time app
ROUTES = [
    # time handler route
    Route(r'/json_time', 'jsontime.handlers.TimeAPIHandler'),
]
