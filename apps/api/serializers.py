from django.contrib.auth.models import User
from rest_framework import serializers

from apps.alerts.models import Alert
from apps.courses.models import Assignment, Course, Resource, Semester


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ("id", "username", "first_name", "last_name", "email")


class SemesterSerializer(serializers.ModelSerializer):
	class Meta:
		model = Semester
		fields = ("id", "name", "year", "start", "end")


class CourseSerializer(serializers.ModelSerializer):
	faculty = UserSerializer(many=True, read_only=True)

	class Meta:
		model = Course
		fields = (
			"id",
			"title",
			"number",
			"section",
			"description",
			"semester",
			"faculty",
			"private",
			"credits",
			"campus",
			"location",
		)


class AssignmentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Assignment
		fields = ("id", "course", "title", "description", "due_date")


class ResourceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Resource
		fields = ("id", "course", "title", "description", "link", "file")


class AlertSerializer(serializers.ModelSerializer):
	class Meta:
		model = Alert
		fields = ("id", "title", "details", "level", "sticky", "sent_by", "created")
