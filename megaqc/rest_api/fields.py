from flask_restful import url_for
from sqlalchemy.orm.collections import InstrumentedList
import json
from megaqc.extensions import ma


class JsonString(ma.Field):
    """
    Serializes a JSON structure as JSON, but deserializes it as a string (for DB storage)
    """

    def _serialize(self, value, attr, obj):
        return json.loads(value)

    def _deserialize(self, value, attr, data):
        return json.dumps(value)
