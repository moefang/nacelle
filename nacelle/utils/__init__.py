"""
    nacelle microframework

    random utils
"""

# stdlib imports
import datetime
import logging
import math
import re
import time
from xml.sax.saxutils import escape


def inverse_microsecond_str():
    t = datetime.datetime.now()
    inv_us = int(1e16 - (time.mktime(t.timetuple()) * 1e6 + t.microsecond))
    base_100_chars = []
    while inv_us:
        digit, inv_us = inv_us % 100, inv_us / 100
        base_100_chars = [chr(23 + digit)] + base_100_chars
    return "".join(base_100_chars)


def uniqify(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]


def tag_weight(x):
    return 2.5 * math.log(x, math.e)


def prettify_string(string):
    pretty_string = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    pretty_string = re.sub('([a-z0-9])([A-Z])', r'\1_\2', pretty_string).lower()
    pretty_string = pretty_string.replace('_', ' ')
    pretty_string = pretty_string.title()
    logging.debug(pretty_string)
    return pretty_string


def make_xmlsafe(string):
    return escape(string)
