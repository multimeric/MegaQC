from flask_restful import url_for
from sqlalchemy.orm.collections import InstrumentedList
import json
from megaqc.extensions import ma

class ResourceHyperlink(ma.Field):
    """
    Serializes as a hyperlink to a flask_restful Resource. This is basically a hack to work around the bug:
    https://github.com/marshmallow-code/flask-marshmallow/issues/144
    """

    def __init__(self, endpoint, url_args=None, *args, **kwargs):
        super(ResourceHyperlink, self).__init__(*args, **kwargs)

        # If the user passes in a list of args, we assume a field with the exact same name appears on the relation
        if isinstance(url_args, list):
            self.url_args = {key: None for key in url_args}
        else:
            self.url_args = url_args

        self.endpoint = endpoint

    def convert_url(self, object):
        args = {}
        for key, value in self.url_args.items():
            if value is None:
                args[key] = getattr(object, key)
            else:
                args[key] = getattr(object, value)

        return url_for(self.endpoint, **args)

    def _serialize(self, value, attr, obj):
        """
        :param value: The current value of this attribute (the SQLAlchemy model)
        :param attr: The name of the attribute
        :param obj: The current object we're serializing
        """
        if isinstance(value, InstrumentedList):
            return [self.convert_url(relation) for relation in value]
        else:
            return self.convert_url(value)

    def _deserialize(self, value, attr, data):
        return None
        # raise NotImplementedError()


class JsonString(ma.Field):
    """
    Serializes a JSON structure as JSON, but deserializes it as a string (for DB storage)
    """

    def _serialize(self, value, attr, obj):
        return json.loads(value)

    def _deserialize(self, value, attr, data):
        return json.dumps(value)
