# stdlib imports
import re

# third-party imports
from google.appengine.api import mail

# shamelessly stolen from django.core.validators
# this works but SublimeLinter seems to think there's
# a string encapsulation issue (which there isn't)
# AAAAAARRRGGGGHHHHHHHHHHH!!11111!!!!!!11!!!!!
email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
    r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)$)'  # domain
    r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)  # literal form, ipv4 address (SMTP 4.1.3)


class ValidationError(Exception):
    pass


def validate_email(value):

    # check that we've actually been passed a value here
    if value is not None:
        # validate against the Django email_re above
        if not email_re.search(value):
            raise ValidationError('email invalid: %s' % value)
        # use appengine's own mail validation just to be sure (yes
        # it's almost useless but worth a check... just to be sure)
        mail.check_email_valid(value, 'email')
    else:
        raise ValidationError('email required')
