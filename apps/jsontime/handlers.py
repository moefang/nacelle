"""
Simple nacelle app to provide a JSON time server

Accepts simple GET requests with one parameter (tz) and
returns the current time along with some metadata as a
JSON encoded response
"""
# third-party imports
from pytz.gae import pytz

# local imports
from nacelle.handlers.base import JSONHandler
from nacelle.utils.timeutils import get_current_time
from nacelle.utils.timeutils import get_timezone
from nacelle.utils.timeutils import get_utcoffset_as_string


class TimeAPIHandler(JSONHandler):

    def get_context(self):

        # get the timezone from the GET params (default to UTC)
        tz = self.request.get('tz', default_value='UTC')

        # attempt to parse timezone
        try:
            timezone = get_timezone(tz)
        # return error if invalid timezone
        except pytz.UnknownTimeZoneError:
            # set HTTP status and return error msg
            self.response.set_status(400)
            return {'error': 'Unknown timezone "%s"' % tz}

        # add timezone name to response
        response = {'tz_name': timezone.zone}
        # add utc offset to response
        response['tz_offset'] = get_utcoffset_as_string(timezone)
        # add current time to response
        response['datetime'] = get_current_time(tz)
        return response
