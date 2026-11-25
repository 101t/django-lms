import datetime
from collections import defaultdict

import recurrence.fields
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField


class Semester(models.Model):
	name = models.CharField(max_length=200)
	year = models.IntegerField()
	start = models.DateField()
	end = models.DateField()

	class Meta:
		ordering = ["-start"]

	def __str__(self):
		return f"{self.name} {self.year}"

	@classmethod
	def get_current(cls):
		"""The semester running today, else the most recent one, else None."""
		today = datetime.date.today()
		return cls.objects.filter(start__lte=today, end__gte=today).first() or cls.objects.order_by("-end").first()

	def get_events(self, course_set=None):
		"""Map each date in the semester to a time-sorted list of (occurrence, CourseEvent)."""
		start = datetime.datetime.combine(self.start, datetime.time.min)
		end = datetime.datetime.combine(self.end, datetime.time.max)
		if course_set is None:
			course_set = self.course_set.all()

		events = defaultdict(list)
		for event in CourseEvent.objects.filter(course__in=course_set).select_related("course"):
			for occurrence in event.recurrences.occurrences(dtstart=start, dtend=end):
				events[occurrence.date()].append((occurrence, event))
		for day in events.values():
			day.sort(key=lambda pair: pair[1].start)
		return dict(events)

	def active(self):
		return self.start <= datetime.date.today() <= self.end

	def save(self, *args, **kwargs):
		if self.start > self.end:
			raise ValueError("Start date must be before end date.")
		return super().save(*args, **kwargs)

	@property
	def is_future(self):
		return self.start > datetime.date.today()

	def get_next(self):
		"""The semester that starts first after this one ends."""
		semester = Semester.objects.filter(start__gt=self.end).order_by("start").first()
		if semester is None:
			raise Semester.DoesNotExist
		return semester


class CourseQuerySet(models.QuerySet):
	def visible_to(self, user):
		if user.is_superuser:
			return self
		return self.filter(
			Q(private=False) | Q(faculty=user) | Q(members=user) | Q(teaching_assistants=user)
		).distinct()


class Course(models.Model):
	title = models.CharField(max_length=200)
	section = models.CharField(max_length=10)
	number = models.CharField(max_length=10)
	description = HTMLField()
	semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

	faculty = models.ManyToManyField(User, verbose_name=_("Faculty"), related_name="faculty")
	teaching_assistants = models.ManyToManyField(User, verbose_name=_("Teaching Assistants"))
	members = models.ManyToManyField(User, verbose_name=_("Members"), related_name="members")

	private = models.BooleanField(default=False, blank=True)

	credits = models.DecimalField(max_digits=3, decimal_places=1, default="3.0")
	campus = models.CharField(max_length=200, choices=getattr(settings, "CAMPUSES", [("main", "Main")]))
	location = models.CharField(max_length=200)

	objects = CourseQuerySet.as_manager()

	class Meta:
		ordering = ["number", "section"]

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("courses:overview", kwargs={"pk": self.pk})

	def full_title(self):
		return f"{self.number}-{self.section} {self.title}"

	def is_faculty(self, user):
		return user.is_superuser or self.faculty.filter(pk=user.pk).exists()

	def is_member(self, user):
		return self.members.filter(pk=user.pk).exists()

	def can_view(self, user):
		return not self.private or Course.objects.filter(pk=self.pk).visible_to(user).exists()


class CourseEvent(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="schedule")
	title = models.CharField(max_length=200, help_text=_("For example: Lecture, Meeting, Lab"))
	start = models.TimeField()
	end = models.TimeField()
	recurrences = recurrence.fields.RecurrenceField()

	def __str__(self):
		return f"{self.course} — {self.title}"

	@property
	def readable(self):
		lines = [r.to_text() for r in self.recurrences.rrules]
		lines += [f"Except {r.to_text()}" for r in self.recurrences.exrules]
		lines += [d.strftime("%a %b %d, %Y") for d in self.recurrences.rdates]
		lines += [f"Except {d.strftime('%a %b %d, %Y')}" for d in self.recurrences.exdates]
		return lines


class Assignment(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	title = models.CharField(max_length=200)
	description = HTMLField()
	due_date = models.DateField(null=True, blank=True)

	class Meta:
		ordering = ["due_date", "title"]

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("courses:assignment_overview", kwargs={"pk": self.pk})


class AssignmentSubmission(models.Model):
	users = models.ManyToManyField(User, related_name="submitters")

	assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
	link = models.URLField(blank=True)
	file = models.FileField(upload_to="submissions/%Y/%m/%d", blank=True)
	notes = models.TextField(blank=True)

	submitted = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-submitted"]

	def late(self):
		return bool(self.assignment.due_date) and self.submitted.date() > self.assignment.due_date

	def __str__(self):
		return self.link or (self.file and self.file.name) or f"Submission #{self.pk}"


class Resource(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	title = models.CharField(max_length=200)
	description = HTMLField()
	link = models.URLField(blank=True)
	file = models.FileField(upload_to="resources/%Y/%m/%d", blank=True)

	class Meta:
		ordering = ["title"]

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("courses:resource_details", kwargs={"pk": self.pk})
