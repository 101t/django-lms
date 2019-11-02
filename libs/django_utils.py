from django.shortcuts import render_to_response as render
from django.template import RequestContext
from django.conf import settings


def render_to_response(*args, **kwargs):
    kwargs['context_instance'] = RequestContext(args[1]['request'])
    kwargs['context_instance'].update({'TITLE': getattr(settings, 'TITLE', '')})
    return render(*args, **kwargs)
