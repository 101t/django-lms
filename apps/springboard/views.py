import datetime

from django.db.models import Q
from django.views.generic import ListView

from apps.alerts.models import Alert
from apps.courses.models import Assignment, Course

from .models import IntranetApplication


class SpringBoard(ListView):
	context_object_name = "applications"
	template_name = "springboard/springboard.html"

	def get_queryset(self):
		user = self.request.user
		if user.is_superuser:
			return IntranetApplication.objects.all()
		return IntranetApplication.objects.filter(Q(groups__in=user.groups.all()) | Q(groups__isnull=True)).distinct()

	def get_context_data(self, **kwargs):
		user = self.request.user
		my_courses = Course.objects.filter(Q(members=user) | Q(faculty=user) | Q(teaching_assistants=user)).distinct()
		return super().get_context_data(
			alerts=Alert.objects.filter(sent_to=user)[:5],
			my_courses=my_courses.select_related("semester")[:6],
			upcoming=Assignment.objects.filter(course__in=my_courses, due_date__gte=datetime.date.today())
			.select_related("course")
			.order_by("due_date")[:5],
			**kwargs,
		)
