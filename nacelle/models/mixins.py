# stdlib imports
import json

# third-party imports
from google.appengine.ext import db

# local imports
from nacelle.utils.serialize import property_to_json
from nacelle.utils.serialize import json_to_property


class JSONMixins(object):

    """
    Adding these Mixins to your model class will allow
    serialisation/deserialisation of your model instances.
    """

    def get_json(self, encode=True):

        """Build and return a JSON representation of our model"""

        instance_dict = db.to_dict(self)
        for key, val in instance_dict.items():
            instance_dict[key] = property_to_json(val)
        instance_dict['key'] = 'key:' + str(self.key())

        if encode:
            # dump to JSON and return
            return json.dumps(instance_dict)
        else:
            return instance_dict

    def set_json(self, value):

        """Convert a dictionary or JSON encoded string to appengine model properties"""

        # Handle JSON object whether as string or dict
        if isinstance(value, basestring):
            json_dict = json.loads(value)
        else:
            json_dict = value

        # loop over all vals in JSON object
        for key, val in json_dict.items():
            if key == 'key':
                continue
            processed_val = json_to_property(val)
            # set value as model property
            setattr(self, key, processed_val)

    # Property via which all JSON access is made
    json = property(get_json, set_json)
