from django import template

register = template.Library()


@register.filter
def group_by(value, arg):
    """
    Group items in a list by size arg
    Usage: {% for group in list|group_by:3 %}
    """
    try:
        arg = int(arg)
        return [value[i:i + arg] for i in range(0, len(value), arg)]
    except (ValueError, TypeError):
        return [value]
