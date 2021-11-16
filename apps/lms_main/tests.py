from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from apps.courses.factories import CourseFactory, FacultyFactory, SemesterFactory
from apps.lms_main.tasks import disable_faculty, get_yesterday_semester


class TasksTest(TestCase):
	def test_yesterday_semester(self):
		"""
		Tests that out utility function returns yesterday's semester
		"""

		current_semester = SemesterFactory.create(end=timezone.now().date() - timezone.timedelta(days=1))

		self.assertEquals(current_semester, get_yesterday_semester())

	def test_disable_faculty(self):
		"""
		Tests if our tasks will disable inactive faculty
		"""

		faculty = FacultyFactory.create()
		current_semester = SemesterFactory.create(end=timezone.now().date() - timezone.timedelta(days=1))
		next_semester = SemesterFactory.create(
			start=timezone.now().date() + timezone.timedelta(days=60),
			end=timezone.now().date() + timezone.timedelta(days=90))

		current_course = CourseFactory.create(semester=current_semester)
		next_course = CourseFactory.create(semester=next_semester)

		current_course.faculty.add(faculty)

		disable_faculty()

		faculty = User.objects.get(username=faculty.username)
		self.assertEquals(faculty.is_active, False)
