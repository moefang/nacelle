# stdlib imports
import datetime
import logging

# third-party imports
from google.appengine.ext import db
from google.appengine.api.mail import EmailMessage
from google.appengine.api.mail import InvalidEmailError
from google.appengine.api.mail import InvalidSenderError

# local imports
from nacelle.models.decorators import derived_property
from nacelle.models.mixins import JSONMixins


class Email(db.Model, JSONMixins):

    """
    Simple model that stores details of an email message and
    allows it to be sent via appengine's mail service
    """

    # address to send the email from (must be an admin of the appengine
    # app or the email address of the currently logged in user)
    sender = db.StringProperty()
    # lists of addresses (simple strings or RFC 2822 compliant addresses) for
    # to, cc and bcc
    to = db.StringListProperty()
    cc = db.StringListProperty()
    bcc = db.StringListProperty()
    # address for Reply To: field
    reply_to = db.StringProperty(required=False)
    # email subject
    subject = db.StringProperty()
    # plain text version of the email
    body = db.TextProperty()
    # html version of the email for clients that support it
    html = db.TextProperty(required=False)
    # don't send the email before this time
    time_scheduled = db.DateTimeProperty()
    # set when email is sent
    time_sent = db.DateTimeProperty(required=False)
    # set this when sending an email fails so we don't constantly retry it
    failed = db.BooleanProperty(default=False)

    # auto fields
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    @derived_property
    def sent(self):
        # if time_sent has been set the the email has been sent
        if self.time_sent is not None:
            return True
        else:
            return False

    def send(self):
        # check if email has already been sent
        if not self.sent:
            log_msg = 'Sending email: %s (%s)' % (' ,'.join(self.to), self.subject)
            logging.info(log_msg)
            try:
                # create new email object and set its fields to the values of the model
                new_email = EmailMessage()
                new_email.sender = self.sender
                new_email.to = self.to
                if self.cc:
                    new_email.cc = self.cc
                if self.bcc:
                    new_email.bcc = self.bcc
                if self.reply_to:
                    new_email.reply_to = self.reply_to
                new_email.subject = self.subject
                new_email.body = self.body
                if self.html:
                    new_email.html = self.html
                # check that the email has been properly initialized and send
                new_email.check_initialized()
                new_email.send()
                # set time sent to now and save model
                self.time_sent = datetime.datetime.utcnow()
                self.put()
            except (InvalidSenderError, InvalidEmailError), e:
                logging.error(e)
                self.failed = True
                self.put()
        else:
            log_msg = 'Email already sent, skipping: %s' % ' ,'.join(self.to)
            logging.info(log_msg)
