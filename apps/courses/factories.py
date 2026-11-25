from datetime import date, time, timedelta

import factory
from django.contrib.auth.models import Group, User

from .models import Assignment, Course, CourseEvent, Semester


class SemesterFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = Semester

	name = "Fall"
	year = factory.LazyFunction(lambda: date.today().year)
	start = factory.LazyFunction(lambda: date.today() - timedelta(days=30))
	end = factory.LazyFunction(lambda: date.today() + timedelta(days=30))


class CourseFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = Course

	title = "Test Title"
	section = "001"
	number = "101"
	description = "Test Course<br>It is a test."
	semester = factory.SubFactory(SemesterFactory)
	campus = "main"
	location = "543"


class EventFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = CourseEvent

	course = factory.SubFactory(CourseFactory)
	title = "Lecture"
	start = time(9, 0)
	end = time(11, 0)
	recurrences = "RRULE:FREQ=WEEKLY;BYDAY=TU,TH"


class AssignmentFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = Assignment

	course = factory.SubFactory(CourseFactory)
	title = factory.Sequence(lambda n: f"Assignment {n}")
	description = "<strong>Bold</strong> Assignment."
	due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=7))


class FacultyFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = User

	username = factory.Sequence(lambda n: f"faculty{n}")
	email = factory.Sequence(lambda n: f"faculty{n}@example.com")
	first_name = factory.Sequence(lambda n: f"faculty{n}")
	last_name = "smith"

	@factory.post_generation
	def faculty_group(self, create, extracted, **kwargs):
		if create:
			self.groups.add(Group.objects.get_or_create(name="Faculty")[0])
