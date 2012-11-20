"""
Handlers for the nacelle mailer app
"""
# stdlib import
import datetime

# third-party imports
import webapp2
from google.appengine.api import taskqueue
from iso8601 import parse_date

# local imports
from mailer.models import Email
from mailer.models import ScheduledEmail
from nacelle.handlers.mixins import JSONMixins


class EmailAPIHandler(JSONMixins, webapp2.RequestHandler):

    """
    AJAX Handler to allow immediate sending of emails
    """

    def post(self):

        # retrieve email details from post body
        sender = self.request.get('sender', default_value=None)
        to = self.request.get('to', default_value=[])
        reply_to = self.request.get('reply_to', default_value=None)
        subject = self.request.get('subject', default_value=None)
        body_plain = self.request.get('body_plain', default_value=None)
        body_html = self.request.get('body_html', default_value=None)

        # build email model and save/send
        new_email = Email(
            sender=sender,
            to=[to],
            reply_to=reply_to,
            subject=subject,
            body_plain=body_plain,
            body_html=body_html,
        )

        new_email.put()

        # build and return response object
        response = new_email.get_json(encode=False)
        return self.json_response(response)


class ScheduledEmailAPIHandler(JSONMixins, webapp2.RequestHandler):

    """
    AJAX Handler to allow scheduled sending of emails
    """

    def post(self):

        # get scheduled sending time
        time_scheduled = self.request.get('time_scheduled', default_value=None)
        if time_scheduled is None:
            self.response.set_status(400)
            return self.json_response({'error': 'time_scheduled is required'})
        time_scheduled = parse_date(time_scheduled)

        # retrieve email details from post body
        sender = self.request.get('sender', default_value=None)
        to = self.request.get('to', default_value=[])
        reply_to = self.request.get('reply_to', default_value=None)
        subject = self.request.get('subject', default_value=None)
        body_plain = self.request.get('body_plain', default_value=None)
        body_html = self.request.get('body_html', default_value=None)

        # build email model and save/send
        new_email = ScheduledEmail(
            time_scheduled=time_scheduled,
            sender=sender,
            to=[to],
            reply_to=reply_to,
            subject=subject,
            body_plain=body_plain,
            body_html=body_html,
        )

        new_email.put()

        # build and return response object
        response = new_email.get_json(encode=False)
        return self.json_response(response)


class CronScheduledEmailHandler(JSONMixins, webapp2.RequestHandler):

    """
    Cron handler to send any scheduled emails
    """

    def get(self):

        # run handler on a task queue
        taskqueue.add(url='/_cron/mailer/send_scheduled', queue_name='mail-queue')
        return self.json_response({'status': "Task queued"})

    def post(self):

        now = datetime.datetime.utcnow()
        query = ScheduledEmail.all().filter('time_scheduled <', now)
        query = query.filter('failed =', False)
        query = query.filter('sent =', False)
        query = query.order('time_scheduled')

        for email in query.run():
            email.send()

        response = {'status': 'Task complete'}
        return self.json_response(response)
