import django
import socketserver as SocketServer
import os.path

from django.conf import settings
# from django.views.debug import linebreak_iter

# Figure out some paths
django_path = os.path.realpath(os.path.dirname(django.__file__))
socketserver_path = os.path.realpath(os.path.dirname(SocketServer.__file__))


def tidy_stacktrace(strace):
	"""
	Clean up stacktrace and remove all entries that:
	1. Are part of Django (except contrib apps)
	2. Are part of SocketServer (used by Django's dev server)
	3. Are the last entry (which is part of our stacktracing code)
	"""
	trace = []
	for s in strace[:-1]:
		s_path = os.path.realpath(s[0])
		if getattr(settings, 'DEVSERVER_CONFIG', {}).get('HIDE_DJANGO_SQL', True) \
				and django_path in s_path and not 'django/contrib' in s_path:
			continue
		if socketserver_path in s_path:
			continue
		trace.append((s[0], s[1], s[2], s[3]))
	return trace


def get_template_info(source, context_lines=3):
	line = 0
	upto = 0
	source_lines = []
	before = during = after = ""

	origin, (start, end) = source
	template_source = origin.reload()

	for num, _next in enumerate(iter(template_source)):
		if start >= upto and end <= _next:
			line = num
			before = template_source[upto:start]
			during = template_source[start:end]
			after = template_source[end:_next]
		source_lines.append((num, template_source[upto:_next]))
		upto = _next

	top = max(1, line - context_lines)
	bottom = min(len(source_lines), line + 1 + context_lines)

	context = []
	for num, content in source_lines[top:bottom]:
		context.append({
			'num': num,
			'content': content,
			'highlight': (num == line),
		})

	return {
		'name': origin.name,
		'context': context,
	}
