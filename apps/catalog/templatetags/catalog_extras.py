from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

@register.filter(name='replacespaces')
@stringfilter
def replacespaces(value, arg):
    "Removes all values of arg from the given string"
    return value.replace(' ', arg)

@register.filter(name='replaceunderscores')
@stringfilter
def replaceunderscores(value, arg):
	"Removes all values of arg from the given string"
	return value.replace('_', arg)