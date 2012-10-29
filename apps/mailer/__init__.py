from webapp2 import Route

routes = [
    Route('/mailer', 'mailer.handlers.FormEmailHandler', 'send-email'),
    Route('/api/mailer', 'mailer.handlers.JSONEmailHandler', 'api-send-email'),
    Route('/_cron/mailer', 'mailer.handlers.CronEmailHandler', 'cron-send-email'),
]
