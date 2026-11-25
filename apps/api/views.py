from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.alerts.models import Alert
from apps.courses.models import Assignment, Course, Resource, Semester

from . import serializers


@extend_schema(responses=serializers.UserSerializer)
@api_view(["GET"])
def me(request):
	"""The signed-in user."""
	return Response(serializers.UserSerializer(request.user).data)


class SemesterViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Semester.objects.all()
	serializer_class = serializers.SemesterSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
	"""Courses the user may see. Filter with `?semester=<id>` or `?mine=1`."""

	serializer_class = serializers.CourseSerializer

	def get_queryset(self):
		courses = Course.objects.visible_to(self.request.user).prefetch_related("faculty")
		if semester := self.request.query_params.get("semester"):
			courses = courses.filter(semester_id=semester)
		if self.request.query_params.get("mine"):
			courses = courses.filter(members=self.request.user)
		return courses


class CourseChildViewSet(viewsets.ReadOnlyModelViewSet):
	"""Shared filtering for objects that belong to a course. Filter with `?course=<id>`."""

	model = None

	def get_queryset(self):
		visible = Course.objects.visible_to(self.request.user)
		items = self.model.objects.filter(course__in=visible)
		if course := self.request.query_params.get("course"):
			items = items.filter(course_id=course)
		return items


class AssignmentViewSet(CourseChildViewSet):
	model = Assignment
	serializer_class = serializers.AssignmentSerializer


class ResourceViewSet(CourseChildViewSet):
	model = Resource
	serializer_class = serializers.ResourceSerializer


class AlertViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
	"""Your alerts. DELETE acknowledges one."""

	serializer_class = serializers.AlertSerializer

	def get_queryset(self):
		return Alert.objects.filter(sent_to=self.request.user)

	def perform_destroy(self, instance):
		if instance.sticky:
			raise PermissionDenied("Sticky alerts cannot be dismissed.")
		instance.delete()
