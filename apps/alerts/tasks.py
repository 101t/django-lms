from django.contrib.auth.models import User

from config.celery import app


@app.task()
def alert_userlist(alert, userlist):
	"""
	This takes a mostly complete alert (minus the sent_to) and applies it to all the users in the list
	"""

	for user in userlist:
		# Set the id to None to create a new alert
		alert.id = None
		alert.sent_to = user
		alert.save()


def alert_groups(alert, groups):
	"""
	Takes a group or list of groups and send the alert to them
	"""

	# TODO find a better way to see if groups is iterable and not a string
	if not getattr(groups, '__iter__', False):
		groups = [groups]

	for group in groups:
		users = User.objects.filter(groups=group)
		alert_userlist(alert, users)
