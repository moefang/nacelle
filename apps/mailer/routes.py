"""
Necessary routes for the nacelle mailer app
"""
# third-party imports
from webapp2 import Route

# Define the required routes for the time app
ROUTES = [

    # time handler route
    Route(r'/mailer/send', 'mailer.handlers.EmailAPIHandler'),
    Route(r'/mailer/send_scheduled', 'mailer.handlers.ScheduledEmailAPIHandler'),

    Route(r'/_cron/mailer/send_scheduled', 'mailer.handlers.CronScheduledEmailHandler')
]
