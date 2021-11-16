from django import template
from django.template import loader, Node, Variable
from django.template.defaulttags import url
from django.template import VariableDoesNotExist

register = template.Library()


def render_title(title, context):
	# Strip any outer quotes
	if title[0] in ('"', "'") and title[-1] in ('"', "'"):
		title = title[1:-1]

	t = template.Template(title)
	return t.render(context)


@register.tag
def breadcrumb(parser, token):
	"""
	Renders the breadcrumb.
	Examples:
		{% breadcrumb "Title of breadcrumb" url_var %}
		{% breadcrumb context_var  url_var %}
		{% breadcrumb "Just the title" %}
		{% breadcrumb just_context_var %}

	Parameters:
	-First parameter is the title of the crumb,
	-Second (optional) parameter is the url variable to link to, produced by url tag, i.e.:
		{% url person_detail object.id as person_url %}
		then:
		{% breadcrumb person.name person_url %}

	@author Andriy Drozdyuk
	"""
	return BreadcrumbNode(token.split_contents()[1:])


@register.tag
def breadcrumb_url(parser, token):
	"""
	Same as breadcrumb
	but instead of url context variable takes in all the
	arguments URL tag takes.
		{% breadcrumb "Title of breadcrumb" person_detail person.id %}
		{% breadcrumb person.name person_detail person.id %}
	"""

	bits = token.split_contents()
	if len(bits) == 2:
		return breadcrumb(parser, token)

	# Extract our extra title parameter
	title = bits.pop(1)
	token.contents = ' '.join(bits)

	url_node = url(parser, token)

	return UrlBreadcrumbNode(title, url_node)


class BreadcrumbNode(Node):
	def __init__(self, vars):
		"""
		First var is title, second var is url context variable
		"""
		self.vars = map(Variable, vars)

	def render(self, context):
		title = self.vars[0].var
		title = render_title(title, context)

		url = None

		if len(self.vars) > 1:
			val = self.vars[1]
			try:
				url = val.resolve(context)
			except VariableDoesNotExist:
				print('URL does not exist', val)
				url = None

		return create_crumb(title, url)


class UrlBreadcrumbNode(Node):
	def __init__(self, title, url_node):
		self.title = Variable(title)
		self.url_node = url_node

	def render(self, context):
		title = self.title.var
		title = render_title(title, context)

		url = self.url_node.render(context)
		return create_crumb(title, url)


def create_crumb(title, url=None):
	"""
	Helper function
	"""
	if url:
		crumb = "> <li><a href='{}'>{}</a></li>".format(url, title)
	else:
		crumb = '> <li class="active">{}</a>'.format(title)

	return crumb
