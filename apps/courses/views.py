import datetime

from dateutil import rrule
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import (
	CreateView,
	DeleteView,
	DetailView,
	ListView,
	RedirectView,
	TemplateView,
	UpdateView,
	View,
)

from .coursecalendar import HTMLCourseCalendar
from .forms import AssignmentForm, CourseAdminForm, ResourceForm, SubmitAssignmentForm, TeamSubmitAssignmentForm
from .models import Assignment, AssignmentSubmission, Course, Resource, Semester


class CourseAccessMixin:
	"""
	Loads `self.course` from the URL and enforces who may see the page.
	`require` is "view" (public course or participant), "member" (enrolled) or "faculty".
	`course_from` is the model whose pk is in the URL when it is not the Course itself.
	"""

	require = "view"
	course_from = None

	def get_course(self):
		if self.course_from is None:
			return get_object_or_404(Course, pk=self.kwargs["pk"])
		obj = get_object_or_404(self.course_from, pk=self.kwargs["pk"])
		return obj.assignment.course if isinstance(obj, AssignmentSubmission) else obj.course

	def dispatch(self, request, *args, **kwargs):
		self.course = self.get_course()
		checks = {
			"view": self.course.can_view,
			"member": lambda u: u.is_superuser or self.course.is_member(u),
			"faculty": self.course.is_faculty,
		}
		if not checks[self.require](request.user):
			raise PermissionDenied
		return super().dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user = self.request.user
		context.update(
			course=self.course,
			is_faculty=self.course.is_faculty(user),
			is_member=self.course.is_member(user),
			is_student=user.groups.filter(name="Students").exists(),
		)
		return context


# Courses


class CourseOverview(CourseAccessMixin, DetailView):
	template_name = "courses/overview.html"
	context_object_name = "course"

	def get_object(self, queryset=None):
		return self.course


class CourseMembers(CourseOverview):
	template_name = "courses/members.html"


class CourseAdmin(CourseAccessMixin, UpdateView):
	require = "faculty"
	form_class = CourseAdminForm
	template_name = "courses/admin.html"

	def get_object(self, queryset=None):
		return self.course

	def form_valid(self, form):
		messages.success(self.request, "Course settings saved.")
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("courses:admin", kwargs={"pk": self.course.pk})


class ToggleMembership(CourseAccessMixin, View):
	http_method_names = ["post"]

	def post(self, request, *args, **kwargs):
		if self.course.is_member(request.user):
			self.course.members.remove(request.user)
			messages.info(request, f"You left {self.course}.")
		elif request.user.is_superuser or request.user.groups.filter(name="Students").exists():
			self.course.members.add(request.user)
			messages.success(request, f"You joined {self.course}.")
		else:
			raise PermissionDenied
		return redirect(self.course)


class SemesterList(ListView):
	context_object_name = "semesters"
	template_name = "courses/semester_list.html"
	queryset = Semester.objects.all()


class BySemesterList(ListView):
	context_object_name = "courses"
	template_name = "courses/by_semester.html"

	def get_queryset(self):
		self.semester = get_object_or_404(Semester, pk=self.kwargs["pk"])
		return Course.objects.filter(semester=self.semester).visible_to(self.request.user).prefetch_related("faculty")

	def get_context_data(self, **kwargs):
		return super().get_context_data(semester=self.semester, semesters=Semester.objects.all(), **kwargs)


class CourseDropPage(RedirectView):
	"""Redirects to the current (or latest) semester's course list."""

	def get_redirect_url(self, *args, **kwargs):
		semester = Semester.get_current()
		if semester is None:
			messages.warning(self.request, "No semesters have been created yet.")
			return reverse("springboard:springboard")
		return reverse("courses:by_semester", kwargs={"pk": semester.pk})


# Assignments


class AssignmentList(CourseAccessMixin, ListView):
	context_object_name = "assignments"
	template_name = "courses/assignment_list.html"

	def get_queryset(self):
		return self.course.assignment_set.all()


class NewCourseAssignment(CourseAccessMixin, CreateView):
	require = "faculty"
	form_class = AssignmentForm
	template_name = "courses/new_assignment.html"

	def form_valid(self, form):
		form.instance.course = self.course
		messages.success(self.request, "Assignment created.")
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("courses:assignments", kwargs={"pk": self.course.pk})


class EditAssignment(CourseAccessMixin, UpdateView):
	require = "faculty"
	course_from = Assignment
	model = Assignment
	form_class = AssignmentForm
	template_name = "courses/new_assignment.html"

	def get_success_url(self):
		return self.object.get_absolute_url()


class DeleteAssignment(CourseAccessMixin, DeleteView):
	require = "faculty"
	course_from = Assignment
	model = Assignment
	template_name = "courses/confirm_delete.html"

	def get_success_url(self):
		return reverse("courses:assignments", kwargs={"pk": self.course.pk})


class AssignmentOverview(CourseAccessMixin, DetailView):
	course_from = Assignment
	model = Assignment
	context_object_name = "assignment"
	template_name = "courses/assignment_overview.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		submissions = self.object.assignmentsubmission_set.prefetch_related("users")
		if not context["is_faculty"]:
			submissions = submissions.filter(users=self.request.user)
		context["submissions"] = submissions
		return context


class SubmitAssignment(CourseAccessMixin, CreateView):
	require = "member"
	course_from = Assignment
	form_class = SubmitAssignmentForm
	template_name = "courses/submit_assignment.html"

	def dispatch(self, request, *args, **kwargs):
		self.assignment = get_object_or_404(Assignment, pk=kwargs["pk"])
		return super().dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		return super().get_context_data(assignment=self.assignment, **kwargs)

	def form_valid(self, form):
		form.instance.assignment = self.assignment
		response = super().form_valid(form)
		self.object.users.add(self.request.user, *form.cleaned_data.get("users", []))
		messages.success(self.request, "Submission received.")
		return response

	def get_success_url(self):
		return self.assignment.get_absolute_url()


class TeamSubmitAssignment(SubmitAssignment):
	form_class = TeamSubmitAssignmentForm

	def get_form(self, form_class=None):
		form = super().get_form(form_class)
		form.fields["users"].queryset = self.course.members.exclude(pk=self.request.user.pk)
		return form


class DeleteSubmission(CourseAccessMixin, DeleteView):
	course_from = AssignmentSubmission
	template_name = "courses/confirm_delete.html"

	def get_queryset(self):
		submissions = AssignmentSubmission.objects.filter(assignment__course=self.course)
		if self.course.is_faculty(self.request.user):
			return submissions
		return submissions.filter(users=self.request.user)

	def get_success_url(self):
		return self.object.assignment.get_absolute_url()


# Resources


class ResourceList(CourseAccessMixin, ListView):
	context_object_name = "resources"
	template_name = "courses/resource_list.html"

	def get_queryset(self):
		return self.course.resource_set.all()


class NewCourseResource(CourseAccessMixin, CreateView):
	require = "faculty"
	form_class = ResourceForm
	template_name = "courses/new_resource.html"

	def form_valid(self, form):
		form.instance.course = self.course
		messages.success(self.request, "Resource added.")
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("courses:resources", kwargs={"pk": self.course.pk})


class ResourceDetails(CourseAccessMixin, DetailView):
	course_from = Resource
	model = Resource
	context_object_name = "resource"
	template_name = "courses/resource_details.html"


class EditResource(CourseAccessMixin, UpdateView):
	require = "faculty"
	course_from = Resource
	model = Resource
	form_class = ResourceForm
	template_name = "courses/new_resource.html"

	def get_success_url(self):
		return self.object.get_absolute_url()


class DeleteResource(CourseAccessMixin, DeleteView):
	require = "faculty"
	course_from = Resource
	model = Resource
	template_name = "courses/confirm_delete.html"

	def get_success_url(self):
		return reverse("courses:resources", kwargs={"pk": self.course.pk})


# Calendars


def visible_courses(view, semester):
	return semester.course_set.visible_to(view.request.user)


def my_courses(view, semester):
	user = view.request.user
	return semester.course_set.filter(Q(members=user) | Q(faculty=user) | Q(teaching_assistants=user)).distinct()


class CourseCalendar(TemplateView):
	template_name = "courses/calendar.html"
	user_cal = False
	course_set = staticmethod(visible_courses)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		if "semester" in kwargs:
			semester = get_object_or_404(Semester, pk=kwargs["semester"])
		else:
			semester = Semester.get_current()
		context.update(semester=semester, semesters=Semester.objects.all(), user_cal=self.user_cal)
		if semester is None:
			return context

		renderer = HTMLCourseCalendar(semester.get_events(self.course_set(self, semester)), user_cal=self.user_cal)
		first_month = semester.start.replace(day=1)
		context["calendars"] = [
			mark_safe(renderer.formatmonth(dt.year, dt.month))
			for dt in rrule.rrule(rrule.MONTHLY, dtstart=first_month, until=semester.end)
		]
		return context


class UserCourseCalendar(CourseCalendar):
	user_cal = True
	course_set = staticmethod(my_courses)


class CourseCalendarDay(TemplateView):
	template_name = "courses/calendar_day.html"
	user_cal = False
	course_set = staticmethod(visible_courses)

	def get_context_data(self, year, month, day, **kwargs):
		context = super().get_context_data(**kwargs)
		try:
			day = datetime.date(year, month, day)
		except ValueError as exc:
			raise Http404("Invalid date") from exc
		semester = get_object_or_404(Semester, start__lte=day, end__gte=day)
		context.update(
			day=day,
			semester=semester,
			user_cal=self.user_cal,
			events=semester.get_events(self.course_set(self, semester)).get(day, []),
		)
		return context


class UserCourseCalendarDay(CourseCalendarDay):
	user_cal = True
	course_set = staticmethod(my_courses)
