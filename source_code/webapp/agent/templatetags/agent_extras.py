import html

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="problem_content")
def problem_content(value):
    """
    Convert HTML entities back to their original characters while preserving sup/sub tags.
    """
    if not value:
        return ""

    # Convert HTML entities back to their original characters
    decoded = html.unescape(value)

    # Mark the result as safe HTML
    return mark_safe(decoded)


@register.filter
def make_range(value, arg):
    """Return a range from value to arg (inclusive)."""
    return range(int(value), int(arg) + 1)
