import json

from django import template
from django.forms.models import model_to_dict

register = template.Library()


@register.filter
def to_json(value):
    """
    Renders data as JSON string.
    """
    return json.dumps(model_to_dict(value))
