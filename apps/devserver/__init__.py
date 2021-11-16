# -*- coding: utf-8 -*-
default_app_config = 'apps.devserver.apps.DevServerConfig'
"""
django-devserver
~~~~~~

`django-devserver <http://www.github.com/dcramer/django-devserver>` is a package
that aims to replace the built-in runserver command by providing additional
functionality such as real-time SQL debugging.

:copyright: 2010 by David Cramer
"""

__all__ = ('__version__', '__build__', '__docformat__', 'get_revision')
__version__ = (0, 8, 0)
__docformat__ = 'restructuredtext en'

import os


def _get_git_revision(path):
	revision_file = os.path.join(path, 'refs', 'heads', 'master')
	if not os.path.exists(revision_file):
		return None
	fh = open(revision_file, 'r')
	try:
		return fh.read().strip()
	finally:
		fh.close()


def get_revision():
	"""
	:returns: Revision number of this branch/checkout, if available. None if
		no revision number can be determined.
	"""
	package_dir = os.path.dirname(__file__)
	checkout_dir = os.path.normpath(os.path.join(package_dir, '..'))
	path = os.path.join(checkout_dir, '.git')
	if os.path.exists(path):
		return _get_git_revision(path)
	return None


__build__ = get_revision()


def get_version():
	base = '.'.join(map(str, __version__))
	if __build__:
		base = '%s (%s)' % (base, __build__)
	return base
