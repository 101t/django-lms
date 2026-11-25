from django.contrib.auth.models import User
from django.utils import timezone

from apps.courses.models import Semester
from config.celery import app


def get_yesterday_semester():
	"""The semester whose last day was yesterday."""
	return Semester.objects.get(end=timezone.localdate() - timezone.timedelta(days=1))


@app.task
def expire_course_visibility():
	"""At the end of a semester, make its private courses public again."""
	try:
		semester = get_yesterday_semester()
	except Semester.DoesNotExist:
		return 0
	return semester.course_set.filter(private=True).update(private=False)


@app.task
def disable_faculty():
	"""At the end of a semester, disable Faculty accounts with no course next semester."""
	try:
		next_semester = get_yesterday_semester().get_next()
	except Semester.DoesNotExist:
		return 0
	idle = User.objects.filter(groups__name="Faculty", is_active=True, is_superuser=False).exclude(
		faculty__semester=next_semester  # `faculty` is the reverse name of Course.faculty
	)
	return User.objects.filter(pk__in=idle.values("pk")).update(is_active=False)
