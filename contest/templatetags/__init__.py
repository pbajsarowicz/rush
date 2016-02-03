from django import template
from django.utils.safestring import mark_safe

from rest_framework.renderers import JSONRenderer

register = template.Library()


@register.filter
def json(value):
    """Renders data as JSON string."""
    return mark_safe(JSONRenderer().render(value))
