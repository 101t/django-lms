from django.conf import settings


def site(request):
	context = {"SITE_NAME": settings.SITE_NAME}
	if request.user.is_authenticated:
		context["alert_count"] = request.user.alert_set.count()
	return context


def user_groups(request):
	if not request.user.is_authenticated:
		return {}
	return {"groups": [group.name for group in request.user.groups.all()]}
