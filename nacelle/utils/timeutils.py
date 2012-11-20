"""
Time related utils for nacelle
"""
# stdlib imports
import datetime

# third-party imports
from pytz.gae import pytz


def get_timezone(timezone):

    """
    Convert timezone string to a pytz tzinfo object
    """

    timezone = pytz.timezone(timezone)
    return timezone


def get_current_time(timezone):

    """
    Returns current time in the given timezone
    """

    # convert string to timezone if necessary
    if isinstance(timezone, basestring):
        timezone = get_timezone(timezone)

    # get current time
    response = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(timezone).isoformat()
    return response


def get_utcoffset_as_string(timezone):

    """
    Get current UTC offset as string
    """

    response = datetime.datetime.now(timezone).strftime('%z')
    return response
