"""
Models for the nacelle mailer app
"""
# stdlib imports
import logging

# third-party imports
from google.appengine.api.mail import EmailMessage
from google.appengine.ext import db

# local imports
from nacelle.models.base import JSONModel
from nacelle.models.validators import ValidationError
from nacelle.models.validators import validate_email


class Email(JSONModel):

    """
    Simple model that stores details of an email message and
    allows it to be sent via appengine's mail service
    """

    # auto fields
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    # address to send the email from (must be an admin of the appengine
    # app or the email address of the currently logged in user)
    sender = db.StringProperty(required=False)

    # lists of addresses (simple strings or RFC 2822 compliant addresses) for
    # to, cc and bcc
    to = db.StringListProperty()
    cc = db.StringListProperty()
    bcc = db.StringListProperty()

    # address for Reply To: field
    reply_to = db.StringProperty(required=False)

    # email subject
    subject = db.StringProperty(required=False)

    # plain text version of the email
    body_plain = db.TextProperty(required=False)
    # html version of the email for clients that support it
    body_html = db.TextProperty(required=False)

    # allow the email to be resent
    resend = db.BooleanProperty(default=False)

    def get_sender(self):

        """
        Override this method to provide custom sender logic
        for the email e.g. providing a single sending address
        in your settings file.
        """

        if not self.sender:
            raise ValidationError('Sender address required')

        return self.sender

    def send(self):

        """
        Build and send an email message from this model instance
        """

        # create new email message
        new_email = EmailMessage()

        # set sender address
        new_email.sender = self.get_sender()

        # set to addresses
        new_email.to = self.to

        # set cc addresses
        if self.cc:
            new_email.cc = self.cc

        # set bcc addresses
        if self.bcc:
            new_email.bcc = self.bcc

        # set reply to address
        if self.reply_to:
            new_email.reply_to = self.reply_to
        else:
            new_email.reply_to = self.get_sender()

        # set email subject
        new_email.subject = self.subject

        # set plaintext body
        if self.body_plain:
            new_email.body = self.body_plain

        # set html body
        if self.body_html:
            new_email.html = self.body_html

        # check that the email has been properly initialized and send
        new_email.check_initialized()
        new_email.send()

    def validate_mail(self):

        """
        Validate all fields in the Email model
        """

        # validate sender address, this isn't required as can
        # be generated at sending time if is blank
        if self.sender is not None:
            validate_email(self.sender)

        if not self.to:
            # raise ValidationError if no recipients specified
            raise ValidationError('At least one to: address must be specified')

        # check to: addresses are valid
        for to_address in self.to:
            validate_email(to_address)

        # check cc: addresses are valid
        for cc_address in self.cc:
            validate_email(cc_address)

        # check bcc: addresses are valid
        for bcc_address in self.bcc:
            validate_email(bcc_address)

        # validate reply_to address, this isn't required as can
        # be generated at sending time if is blank
        if self.reply_to is not None:
            validate_email(self.reply_to)

        if not self.subject:
            # raise ValidationError if subject is blank
            raise ValidationError('Email requires a subject')

        # all emails require at least one of a plain text body or a HTML body
        if not self.body_plain and not self.body_html:
            raise ValidationError('Email cannot have an empty body')

    def put(self, *args, **kwargs):

        """
        Override put to provide custom validation
        for this model and send the email
        """

        # validate email before saving
        self.validate_mail()

        if not self.is_saved() or self.resend:
            # attempt to send email
            self.send()

        super(Email, self).put(*args, **kwargs)


class ScheduledEmail(Email):

    """
    Model to store details of emails which are
    scheduled to be sent at a specific time
    """

    # don't send the email before this time
    time_scheduled = db.DateTimeProperty()

    # property to show if email has been sent
    sent = db.BooleanProperty(default=False)
    # set this when sending an email fails so
    # we don't constantly retry it
    failed = db.BooleanProperty(default=False)

    def send(self):

        try:
            # call Email's send method
            super(ScheduledEmail, self).send()
        except Exception, e:
            logging.exception(e)
            self.failed = True
        else:
            # mark the email as sent
            self.sent = True

        # save the model instance
        self.put()

    def put(self, *args, **kwargs):

        """
        Override put to provide custom validation for this model
        """

        if not self.is_saved() or self.resend:
            # validate email before saving
            self.validate_mail()

        super(JSONModel, self).put(*args, **kwargs)
