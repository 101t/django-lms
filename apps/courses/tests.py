import datetime

from django.contrib.auth.models import Group
from django.urls import reverse

import libs.test_utils as test_utils
from apps.courses.models import Assignment, AssignmentSubmission, Course, Resource, Semester

from .factories import EventFactory

one_week = datetime.timedelta(7)
one_day = datetime.timedelta(1)


class SemesterTest(test_utils.AuthenticatedTest):
	def test_create(self):
		semester = Semester(
			name="Spring",
			year="2012",
			start=datetime.date(2012, 1, 1),
			end=datetime.date(2012, 5, 15),
		)
		semester.save()
		self.assertEqual(semester.name, "Spring")
		self.assertEqual(semester.year, "2012")
		self.assertEqual(semester.start, datetime.date(2012, 1, 1))
		self.assertEqual(semester.end, datetime.date(2012, 5, 15))
		semester.delete()

		# Try invalid start and end date
		semester = Semester(name="Spring", year="2012", start=datetime.date(2012, 5, 15), end=datetime.date(2012, 1, 1))
		self.assertRaises(ValueError, semester.save, ())

	def test_listing(self):
		semester = Semester(name="Spring", year="2012", start=datetime.date(2012, 1, 1), end=datetime.date(2012, 5, 15))
		semester.save()

		course = Course(
			title="Test Course",
			number="101",
			section="001",
			description="Test description of a course",
			semester=semester,
		)
		course.save()
		course = Course(
			title="Test Course2",
			number="101",
			section="002",
			description="Test description of a course",
			semester=semester,
		)
		course.save()
		course = Course(
			title="Test Course3",
			number="102",
			section="001",
			description="Test description of a course",
			semester=semester,
		)
		course.save()

		response = self.c.get(reverse("courses:by_semester", args=[semester.id]))
		courses = Course.objects.filter(semester=semester)
		self.assertEqual([course.id for course in response.context["courses"]], [course.id for course in courses])

	def test_active(self):
		semester = Semester(
			name="Spring", year="2012", start=datetime.date.today() - one_day, end=datetime.date.today() + one_day
		)
		semester.save()

		self.assertEqual(semester.active(), True)

		semester.start = datetime.date.today() + one_day
		semester.end = datetime.date.today() + one_week
		semester.save()

		self.assertEqual(semester.active(), False)


class CoursesTest(test_utils.AuthenticatedTest):
	def setUp(self):
		super().setUp()
		self.semester = Semester(
			name="Spring", year="2012", start=datetime.date(2012, 1, 1), end=datetime.date(2012, 5, 1)
		)
		self.semester.save()
		self.course = Course(
			title="Test Course",
			number="101",
			section="001",
			description="Test description of a course",
			semester=self.semester,
			campus="main",
			location="Room 101",
			credits="3.0",
		)
		self.course.save()

	def tearDown(self):
		self.course.delete()
		self.semester.delete()

	def test_create(self):
		self.assertEqual(self.course.title, "Test Course")
		self.assertEqual(self.course.number, "101")
		self.assertEqual(self.course.section, "001")
		self.assertEqual(self.course.description, "Test description of a course")
		self.assertEqual(self.course.campus, "main")
		self.assertEqual(self.course.location, "Room 101")
		self.assertEqual(self.course.credits, "3.0")

	def test_view(self):
		response = self.c.get(reverse("courses:overview", args=[self.course.id]))

		self.assertEqual(response.context["course"].title, "Test Course")
		self.assertEqual(response.context["course"].number, "101")
		self.assertEqual(response.context["course"].section, "001")
		self.assertEqual(response.context["course"].description, "Test description of a course")

	def test_access(self):
		self.course.private = True
		self.course.save()

		response = self.c.get(reverse("courses:overview", args=[self.course.id]))
		self.assertEqual(response.status_code, 403)

		# Test membership
		self.course.members.add(self.user)
		self.course.save()
		response = self.c.get(reverse("courses:overview", args=[self.course.id]))
		self.assertEqual(response.status_code, 200)
		self.course.members.remove(self.user)
		self.course.save()

		# Test Faculty
		self.course.faculty.add(self.user)
		self.course.save()
		response = self.c.get(reverse("courses:overview", args=[self.course.id]))
		self.assertEqual(response.status_code, 200)
		self.course.faculty.remove(self.user)
		self.course.save()

		# Test TA
		self.course.teaching_assistants.add(self.user)
		self.course.save()
		response = self.c.get(reverse("courses:overview", args=[self.course.id]))
		self.assertEqual(response.status_code, 200)
		self.course.teaching_assistants.remove(self.user)
		self.course.save()

		self.course.private = False
		self.course.save()


class AssignmentTest(test_utils.AuthenticatedTest):
	def setUp(self):
		super().setUp()
		self.semester = Semester(
			name="Spring", year="2012", start=datetime.date(2012, 1, 1), end=datetime.date(2012, 5, 1)
		)
		self.semester.save()
		self.course = Course(
			title="Test Course",
			number="101",
			section="001",
			description="Test description of a course",
			semester=self.semester,
		)
		self.course.save()

	def tearDown(self):
		super().tearDown()
		self.course.delete()
		self.semester.delete()

	def test_create(self):
		# Add client user as faculty member
		self.course.faculty.add(self.user)
		self.course.save()

		# Test we get the form
		response = self.c.get(reverse("courses:new_assignment", kwargs={"pk": self.course.id}))
		self.assertEqual(response.status_code, 200)

		response = self.c.post(
			reverse("courses:new_assignment", kwargs={"pk": self.course.id}),
			{
				"course": self.course.id,
				"title": "Test Assignment",
				"description": "Test of the description <b>HERE</b>",
				"due_date": (datetime.date.today() + one_week).isoformat(),
			},
		)

		self.assertEqual(response.status_code, 302)

		# Remove user
		self.course.faculty.remove(self.user)

	def test_list(self):
		assignment = Assignment(
			course=self.course,
			title="Test Assignment",
			description="Test of the description <b>HERE</b>",
			due_date=(datetime.date.today() + one_week).isoformat(),
		)
		assignment.save()

		# Add client user as faculty member
		self.course.faculty.add(self.user)
		self.course.save()

		response = self.c.get(reverse("courses:assignments", kwargs={"pk": self.course.id}))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["assignments"][0], assignment)

		# Remove user
		self.course.faculty.remove(self.user)

	def test_submit(self):
		# Add client user as faculty member
		self.course.faculty.add(self.user)
		self.course.save()
		response = self.c.post(
			reverse("courses:new_assignment", kwargs={"pk": self.course.id}),
			{
				"course": self.course.id,
				"title": "Test Assignment",
				"description": "Test of the description <b>HERE</b>",
				"due_date": (datetime.date.today() + one_week).isoformat(),
			},
		)

		# Remove user
		self.course.faculty.remove(self.user)

		self.course.members.add(self.user)
		self.course.save()

		assignment = Assignment.objects.get(course=self.course, title="Test Assignment")

		# Test submitting solution
		response = self.c.post(
			reverse("courses:submit_assignment", kwargs={"pk": assignment.id}),
			{
				"link": "http://www.example.com",
				"notes": "Test notes.",
			},
		)
		self.assertEqual(response.status_code, 302)

		self.course.members.remove(self.user)

	def test_faculty_see_submissions(self):
		if not self.users:
			self.extra_users()

		# Create an assignment
		self.assignment = Assignment(
			course=self.course,
			title="Test Assignment",
			description="Test",
			due_date=(datetime.date.today() - one_week).isoformat(),
		)

		self.assignment.save()

		# Submit it

		self.submission = AssignmentSubmission(
			assignment=self.assignment,
			link="http://example.com",
		)
		self.submission.save()
		self.submission.users.add(self.users[0])

		# Set myself as the faculty for the course.
		self.course.faculty.add(self.user)
		self.course.save()

		response = self.c.get(reverse("courses:assignment_overview", args=[self.assignment.id]))

		self.assertEqual(len(response.context["submissions"]), 1)

		self.course.faculty.remove(self.user)
		self.course.save()

	def test_late(self):
		self.assignment = Assignment(
			course=self.course,
			title="Test Assignment",
			description="Test",
			due_date=(datetime.date.today() - one_week).isoformat(),
		)

		self.assignment.save()

		self.submission = AssignmentSubmission(assignment=self.assignment, link="http://example.com")
		self.submission.save()

	def test_delete_submission(self):
		# We overrode the delete, so we should be testing it
		self.course.members.add(self.user)
		self.course.save()

		assignment = Assignment(
			course=self.course,
			title="Test Assignment",
			description="Test of the description <b>HERE</b>",
			due_date=(datetime.date.today() + one_week).isoformat(),
		)
		assignment.save()

		submission = AssignmentSubmission(assignment=assignment, link="http://www.example.com", notes="Test notes.")
		submission.save()
		submission.users.add(self.user)
		submission.save()

		s_id = submission.id

		response = self.c.post(reverse("courses:delete_submission", args=[submission.id]))

		self.assertRedirects(response, reverse("courses:assignment_overview", kwargs={"pk": assignment.id}))

		self.assertRaises(AssignmentSubmission.DoesNotExist, AssignmentSubmission.objects.get, pk=s_id)

	def test_team_submit(self):
		if not self.users:
			self.extra_users()

		# Add client user as faculty member
		self.course.faculty.add(self.user)
		self.course.save()
		response = self.c.post(
			reverse("courses:new_assignment", kwargs={"pk": self.course.id}),
			{
				"course": self.course.id,
				"title": "Test Assignment",
				"description": "Test of the description <b>HERE</b>",
				"due_date": (datetime.date.today() + one_week).isoformat(),
			},
		)

		# Remove user
		self.course.faculty.remove(self.user)
		self.course.members.add(self.user)
		self.course.save()

		for user in self.users:
			self.course.members.add(user)

		self.course.save()

		assignment = Assignment.objects.get(course=self.course, title="Test Assignment")

		# Test submitting solution
		response = self.c.post(
			reverse("courses:team_submit_assignment", kwargs={"pk": assignment.id}),
			{"link": "http://www.example.com", "notes": "Test notes.", "users": [user.id for user in self.users]},
		)
		self.assertEqual(response.status_code, 302)

		self.course.members.remove(self.user)

		for user in self.users:
			self.course.members.remove(user)


class ResourceTest(test_utils.AuthenticatedTest):
	def setUp(self):
		super().setUp()
		self.semester = Semester(
			name="Spring", year="2012", start=datetime.date(2012, 1, 1), end=datetime.date(2012, 5, 1)
		)
		self.semester.save()
		self.course = Course(
			title="Test Course",
			number="101",
			section="001",
			description="Test description of a course",
			semester=self.semester,
		)
		self.course.save()

	def tearDown(self):
		super().tearDown()
		self.course.delete()
		self.semester.delete()

	def test_create(self):
		# Add client user as faculty member
		self.course.faculty.add(self.user)
		self.course.save()

		# Test we get the form
		response = self.c.get(reverse("courses:resource_create", kwargs={"pk": self.course.id}))
		self.assertEqual(response.status_code, 200)

		response = self.c.post(
			reverse("courses:resource_create", kwargs={"pk": self.course.id}),
			{
				"course": self.course.id,
				"title": "Test Resource",
				"description": "Test of the description <b>HERE</b>",
				"due_date": (datetime.date.today() + one_week).isoformat(),
			},
		)

		self.assertEqual(response.status_code, 302)

		# Remove user
		self.course.faculty.remove(self.user)

	def test_list(self):
		resource = Resource(
			course=self.course,
			title="Test Resource",
			description="Test of the description <b>HERE</b>",
			link="http://example.com",
		)
		resource.save()

		# Add client user as faculty member
		self.course.faculty.add(self.user)

		self.course.save()

		response = self.c.get(reverse("courses:resources", kwargs={"pk": self.course.id}))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["resources"][0], resource)

		# Remove user
		self.course.faculty.remove(self.user)

	def test_delete_resource(self):
		# We overrode the delete, so we should be testing it
		self.course.faculty.add(self.user)

		resource = Resource(
			course=self.course,
			title="Test Resource",
			description="Test of the description <b>HERE</b>",
			link="http://example.com",
		)
		resource.save()
		resource_id = resource.id

		response = self.c.post(reverse("courses:delete_resource", args=[resource.id]))
		self.assertEqual(response.status_code, 302)

		self.assertRaises(Resource.DoesNotExist, Resource.objects.get, pk=resource_id)


class CalendarTest(test_utils.AuthenticatedTest):
	def setUp(self):
		super().setUp()
		self.course_event = EventFactory.create()

	def test_exists(self):
		response = self.c.get(reverse("courses:calendar"))
		self.assertEqual(response.status_code, 200)


class PermissionTest(test_utils.AuthenticatedTest):
	"""Regression tests: these actions used to be open to any signed-in user."""

	def setUp(self):
		super().setUp()
		semester = Semester.objects.create(
			name="Spring", year=2012, start=datetime.date(2012, 1, 1), end=datetime.date(2012, 5, 1)
		)
		self.course = Course.objects.create(title="C", number="1", section="1", description="d", semester=semester)
		self.resource = Resource.objects.create(course=self.course, title="R", description="d")
		self.assignment = Assignment.objects.create(course=self.course, title="A", description="d")

	def test_non_faculty_cannot_delete_or_edit(self):
		for name, pk in [
			("delete_resource", self.resource.pk),
			("delete_assignment", self.assignment.pk),
			("edit_assignment", self.assignment.pk),
			("admin", self.course.pk),
		]:
			self.assertEqual(self.c.post(reverse(f"courses:{name}", args=[pk])).status_code, 403, name)
		self.assertTrue(Resource.objects.filter(pk=self.resource.pk).exists())
		self.assertTrue(Assignment.objects.filter(pk=self.assignment.pk).exists())

	def test_cannot_delete_someone_elses_submission(self):
		self.extra_users()
		submission = AssignmentSubmission.objects.create(assignment=self.assignment, link="http://example.com")
		submission.users.add(self.users[0])
		self.assertEqual(self.c.post(reverse("courses:delete_submission", args=[submission.pk])).status_code, 404)

	def test_non_member_cannot_submit(self):
		response = self.c.post(
			reverse("courses:submit_assignment", args=[self.assignment.pk]), {"link": "http://example.com"}
		)
		self.assertEqual(response.status_code, 403)

	def test_only_students_can_join(self):
		url = reverse("courses:toggle-membership", args=[self.course.pk])
		self.assertEqual(self.c.post(url).status_code, 403)
		self.user.groups.add(Group.objects.get(name="Students"))
		self.assertRedirects(self.c.post(url), self.course.get_absolute_url())
		self.assertTrue(self.course.is_member(self.user))


class SemesterEventsTest(test_utils.AuthenticatedTest):
	def test_events_span_year_boundary(self):
		semester = Semester.objects.create(
			name="Fall", year=2023, start=datetime.date(2023, 12, 1), end=datetime.date(2024, 1, 31)
		)
		course = Course.objects.create(title="C", number="1", section="1", description="d", semester=semester)
		EventFactory.create(course=course)
		events = semester.get_events()
		self.assertIn(datetime.date(2023, 12, 5), events)  # a Tuesday
		self.assertIn(datetime.date(2024, 1, 4), events)  # a Thursday
		self.assertEqual(self.c.get(reverse("courses:calendar", args=[semester.pk])).status_code, 200)
		self.assertEqual(self.c.get(reverse("courses:calendar_day", args=[2024, 1, 4])).status_code, 200)
