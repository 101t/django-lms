import datetime

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.alerts.tasks import send_alert
from apps.courses.models import Assignment, Course, CourseEvent, Resource, Semester

PASSWORD = "demo12345"

COURSES = [
	(
		"CS101",
		"Introduction to Programming",
		"Variables, control flow, functions and a first taste of Python.",
		"MO,WE",
	),
	("CS201", "Data Structures", "Lists, trees, hash maps and graphs — and when to use which.", "TU,TH"),
	(
		"DES110",
		"Visual Communication",
		"Typography, colour and layout fundamentals through weekly studio work.",
		"WE,FR",
	),
	("MTH150", "Discrete Mathematics", "Logic, sets, combinatorics and proofs for computer science.", "MO,TH"),
]


class Command(BaseCommand):
	help = f"Fill an empty database with a demo semester, courses and users (password: {PASSWORD})."

	@transaction.atomic
	def handle(self, *args, **options):
		if Course.objects.exists():
			self.stdout.write(self.style.WARNING("Courses already exist; skipping demo data."))
			return

		today = datetime.date.today()
		semester = Semester.objects.create(
			name="Current",
			year=today.year,
			start=today - datetime.timedelta(days=30),
			end=today + datetime.timedelta(days=90),
		)
		faculty, _ = Group.objects.get_or_create(name="Faculty")
		students_group, _ = Group.objects.get_or_create(name="Students")

		teachers = [self.user("teacher", "Ada", "Lovelace", faculty), self.user("teacher2", "Alan", "Turing", faculty)]
		students = [self.user(f"student{i}", "Student", str(i), students_group) for i in range(1, 6)]

		for i, (number, title, description, days) in enumerate(COURSES):
			course = Course.objects.create(
				title=title,
				number=number,
				section="001",
				description=f"<p>{description}</p>",
				semester=semester,
				campus="main",
				location=f"Room {101 + i}",
			)
			course.faculty.add(teachers[i % 2])
			course.members.add(*(students if i % 2 == 0 else students[::2]))
			CourseEvent.objects.create(
				course=course,
				title="Lecture",
				start=datetime.time(9 + i, 0),
				end=datetime.time(10 + i, 15),
				recurrences=f"RRULE:FREQ=WEEKLY;BYDAY={days}",
			)
			for week in (1, 2, 4):
				Assignment.objects.create(
					course=course,
					title=f"Problem set {week}",
					description="<p>Complete the exercises from this week's reading.</p>",
					due_date=today + datetime.timedelta(days=7 * week - 3),
				)
			Resource.objects.create(
				course=course,
				title="Syllabus",
				description="<p>Course policies, grading and schedule.</p>",
				link="https://example.com/syllabus",
			)

		send_alert(
			User.objects.filter(is_active=True),
			title="Welcome to the demo LMS!",
			details="<p>Explore courses, the calendar and assignments.</p>",
			level="info",
			sent_by="Django LMS",
		)
		self.stdout.write(
			self.style.SUCCESS(f"Demo data created. Sign in as teacher / {PASSWORD} or student1 / {PASSWORD}.")
		)

	def user(self, username, first, last, group):
		user, created = User.objects.get_or_create(
			username=username, defaults={"first_name": first, "last_name": last, "email": f"{username}@example.com"}
		)
		if created:
			user.set_password(PASSWORD)
			user.save()
		user.groups.add(group)
		return user
