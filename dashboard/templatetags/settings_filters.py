from django import template
import json

register = template.Library()


@register.filter
def jsonify(value):
    """Convert JSON string to Python object for template use."""
    if not value:
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []


@register.filter
def get_choices(setting):
    """Extract choices from a setting."""
    if not setting.choices_json:
        return []
    try:
        return json.loads(setting.choices_json)
    except (json.JSONDecodeError, TypeError):
        return []


@register.filter
def is_true(value):
    """Check if value is boolean true."""
    return str(value).lower() in ('true', '1', 'yes', 'on')
