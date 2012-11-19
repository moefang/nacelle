import datetime
from pytz.gae import pytz


def get_timezone(timezone):

    timezone = pytz.timezone(timezone)
    return timezone


def get_current_time(timezone):

    if isinstance(timezone, basestring):
        timezone = get_timezone(timezone)

    response = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(timezone).isoformat()
    return response


def get_utcoffset_as_string(timezone):

    response = datetime.datetime.now(timezone).strftime('%z')
    return response
