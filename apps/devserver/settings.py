from django.conf import settings

DEVSERVER_MODULES = getattr(settings, 'DEVSERVER_MODULES', (
	'apps.devserver.modules.sql.SQLRealTimeModule',
	# 'apps.devserver.modules.sql.SQLSummaryModule',
	# 'apps.devserver.modules.profile.ProfileSummaryModule',
	# 'apps.devserver.modules.request.SessionInfoModule',
	# 'apps.devserver.modules.profile.MemoryUseModule',
	# 'apps.devserver.modules.profile.LeftOversModule',
	# 'apps.devserver.modules.cache.CacheSummaryModule',
))

DEVSERVER_FILTER_SQL = getattr(settings, 'DEVSERVER_FILTER_SQL', False)
DEVSERVER_TRUNCATE_SQL = getattr(settings, 'DEVSERVER_TRUNCATE_SQL', True)

DEVSERVER_TRUNCATE_AGGREGATES = getattr(
	settings,
	'DEVSERVER_TRUNCATE_AGGREGATES',
	getattr(settings, 'DEVSERVER_TRUNCATE_AGGREGATES', False)
)

# This variable gets set to True when we're running the devserver
DEVSERVER_ACTIVE = False

DEVSERVER_AJAX_CONTENT_LENGTH = getattr(settings, 'DEVSERVER_AJAX_CONTENT_LENGTH', 300)
DEVSERVER_AJAX_PRETTY_PRINT = getattr(settings, 'DEVSERVER_AJAX_PRETTY_PRINT', False)

# Minimum time a query must execute to be shown, value is in MS
DEVSERVER_SQL_MIN_DURATION = getattr(settings, 'DEVSERVER_SQL_MIN_DURATION', None)

DEVSERVER_AUTO_PROFILE = getattr(settings, 'DEVSERVER_AUTO_PROFILE', False)
