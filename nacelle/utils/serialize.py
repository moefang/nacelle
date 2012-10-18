"""
    A couple of simple functions to provide support for
    serialising/deserialising entities to/from JSON

    Property/JSON mapping:

        No Conversion (returned as is):
            IntegerProperty <-> int
            FloatProperty <-> float
            BooleanProperty <-> bool
            StringProperty <-> str
            ByteStringProperty <-> str
            ListProperty <-> list
            StringListProperty <-> list

        Conversion (converted so as to be serializable):
            TextProperty <-> str (with prefix: 'text:')
            DateProperty <-> str (iso8601 format date)
            DateTimeProperty <-> str (iso8601 format date with time)
            GeoPtProperty <-> dict ({'lat': float, 'lon': float})
            ReferenceProperty <-> str (with prefix: 'key:')
            SelfReferenceProperty <-> str (with prefix: 'key:')
"""
import datetime
import iso8601
from google.appengine.ext import db


def property_to_json(val):

    # Recursively process values in a list
    if isinstance(val, list):
        prop_list = []
        for list_val in val:
            list_prop = property_to_json(list_val)
            prop_list.append(list_prop)
        if prop_list:
            return prop_list
        else:
            return None

    # output dates/times in iso8601 format
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.isoformat()

    # convert GeoPt values to a simple dict
    if isinstance(val, db.GeoPt):
        return {'lat': val.lat, 'lon': val.lon}

    # convert db keys to urlsafe strings
    if isinstance(val, db.Key):
        return 'key:' + str(val)

    # serialise TextProperty
    if isinstance(val, db.Text):
        return 'text:' + str(val)

    # return
    return val


def json_to_property(val):

    # Recursively process values in a list
    if isinstance(val, list):
        prop_list = []
        for list_val in val:
            list_prop = json_to_property(list_val)
            prop_list.append(list_prop)
        if prop_list:
            return prop_list
        else:
            return None

    # We have no real way to tell if a particular string is a
    # date so try and parse it as an iso8601 format date
    try:
        date_object = iso8601.parse_date(val)
    except:
        pass
    else:
        return date_object

    # Check if we're dealing with a GeoPt value
    if isinstance(val, dict) and (len(val) == 2) and ('lat' in val):
        if 'lon' in val:
            return db.GeoPt(val['lat'], val['lon'])
        else:
            return db.GeoPt(val['lat'])

    # Check if val represents a datastore key
    if isinstance(val, (str, unicode)) and val.startswith('key:'):
        return db.Key(encoded=val.replace('key:', ''))

    # Check if val represents a text property
    if isinstance(val, (str, unicode)) and val.startswith('text:'):
        return db.Text(val.replace('text:', ''))

    return val
