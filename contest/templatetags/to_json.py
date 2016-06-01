from datetime import date, datetime
import json

from django import template
from django.forms.models import model_to_dict

register = template.Library()


class DatetimeEncoder(json.JSONEncoder):
    """
    Encodes not JSON serializable objects' types.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%d-%m-%Y %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%d-%m-%Y')
        return json.JSONEncoder.default(self, obj)


@register.filter
def to_json(value):
    """
    Renders data as JSON string.
    """
    return json.dumps(model_to_dict(value), cls=DatetimeEncoder)
