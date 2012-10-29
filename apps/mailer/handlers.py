# stdlib imports
import datetime
import logging

# third-party imports
from google.appengine.api import taskqueue
from wtforms.ext.appengine.db import model_form

# local imports
from mailer.models import Email
from nacelle.decorators.auth import auth_control
from nacelle.handlers.api import APIHandler
from nacelle.handlers.base import BaseHandler
from nacelle.handlers.mixins import TemplateMixins


class FormEmailHandler(BaseHandler, TemplateMixins):

    """
    Simple handler to allow sending emails via a form interface
    """

    auth = {
        'GET': 'login',
        'POST': 'login'
    }

    excludes = ['time_sent', 'failed']

    @auth_control
    def get(self):
        form = model_form(Email, exclude=self.excludes)()
        self.template_response('email/send.html', **{'form': form})

    @auth_control
    def post(self):
        form = model_form(Email, exclude=self.excludes)()
        form.process(self.request.POST)
        if form.validate():
            record = Email()
            form.populate_obj(record)
            record.put()
            logging.info(str(record.json))
            self.redirect('/')
        else:
            self.template_response('email/send.html', **{'form': form})


class JSONEmailHandler(APIHandler):

    """
    Simple API handler to allow sending emails with a JSON POST request
    """

    model = Email
    auth = {
        'GET': None,
        'POST': 'admin'
    }


class CronEmailHandler(BaseHandler):

    """
    Cronjob which sends all pending emails at a scheduled time
    """

    auth = {
        'GET': 'admin',
        'POST': None,
        'DELETE': None
    }

    @auth_control
    def get(self):

        if 'deferred' in self.request.GET:
            taskqueue.add(url='/_cron/mailer', method='GET', queue_name='mail-queue')
            return self.response.write("Task queued")

        # retrieve all unsent emails from the datastore
        now = datetime.datetime.utcnow()
        unsent_emails = Email.all().filter('sent =', False)
        unsent_emails = unsent_emails.filter('failed =', False)
        unsent_emails = unsent_emails.filter('time_scheduled <', now)
        unsent_emails = unsent_emails.order('time_scheduled').order('created')
        for email in unsent_emails:
            email.send()
        return self.response.write('Task completed')
