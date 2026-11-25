import os

from django import forms, template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name="basename")
@stringfilter
def basename(value):
	return os.path.basename(value)


@register.filter
def widget_kind(field):
	"""'check', 'radio', 'select' or 'input' — picks the Bootstrap 5 markup for a bound field."""
	widget = field.field.widget
	if isinstance(widget, forms.CheckboxInput):
		return "check"
	if isinstance(widget, forms.RadioSelect | forms.CheckboxSelectMultiple):
		return "radio"
	if isinstance(widget, forms.Select):
		return "select"
	return "input"


@register.filter
def bs(field):
	"""Render a bound field's widget with the Bootstrap 5 class it needs."""
	css = {"check": "form-check-input", "radio": "form-check-input", "select": "form-select"}.get(
		widget_kind(field), "form-control"
	)
	if field.errors:
		css += " is-invalid"
	return field.as_widget(attrs={"class": css})
