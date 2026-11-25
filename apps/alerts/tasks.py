from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.db import transaction
from django.utils.html import strip_tags

from config.celery import app

from .models import Alert


def send_alert(users, *, title, details="", level="", sent_by="", sticky=False):
	"""Create one alert per user and queue emails for users who opted in. Returns the alerts."""
	alerts = Alert.objects.bulk_create(
		Alert(sent_to=user, title=title, details=details, level=level, sent_by=sent_by, sticky=sticky) for user in users
	)
	ids = [alert.pk for alert in alerts]
	transaction.on_commit(lambda: email_alerts.delay(ids))
	return alerts


def send_alert_to_groups(groups, **fields):
	return send_alert(User.objects.filter(groups__in=groups, is_active=True).distinct(), **fields)


@app.task
def email_alerts(alert_ids):
	alerts = (
		Alert.objects.filter(pk__in=alert_ids, sent_to__profile__preferences__email_alerts=True)
		.exclude(sent_to__email="")
		.select_related("sent_to")
	)
	messages = [(a.title, strip_tags(a.details), settings.ALERTS_FROM, [a.sent_to.email]) for a in alerts]
	return send_mass_mail(messages, fail_silently=False) if messages else 0
