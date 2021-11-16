# -*- coding: utf-8 -*-
default_app_config = 'apps.django_statsd.apps.DjangoStatsdConfig'

from . import clients
from . import patches
from .plugins import NoseStatsd
