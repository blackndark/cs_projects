from django import template

register = template.Library()

@register.filter
def usd(value):
    return f"${value:,.2f}"
