from django.contrib import admin
from django.contrib.auth.models import User

from .models import Assignment, AssignmentSubmission, Course, CourseEvent, Resource, Semester

# Limit the people pickers to the matching group, as the original LMS did.
ROLE_GROUPS = {"faculty": "Faculty", "members": "Students"}


class ScheduleInline(admin.StackedInline):
	model = CourseEvent
	extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
	inlines = [ScheduleInline]
	list_display = ("full_title", "semester", "campus", "location", "private")
	list_filter = ("semester", "campus", "private")
	search_fields = ("title", "number", "section")
	filter_horizontal = ("faculty", "teaching_assistants", "members")

	def formfield_for_manytomany(self, db_field, request, **kwargs):
		if db_field.name in ROLE_GROUPS:
			kwargs["queryset"] = User.objects.filter(groups__name=ROLE_GROUPS[db_field.name])
		return super().formfield_for_manytomany(db_field, request, **kwargs)

	def get_changeform_initial_data(self, request):
		initial = super().get_changeform_initial_data(request)
		current = Semester.get_current()
		if current:
			initial.setdefault("semester", current.pk)
		return initial

	def save_related(self, request, form, formsets, change):
		super().save_related(request, form, formsets, change)
		# Faculty disabled at the end of a semester come back when they get a new course.
		form.instance.faculty.filter(is_active=False).update(is_active=True)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
	list_display = ("__str__", "start", "end")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
	list_display = ("title", "course", "due_date")
	list_filter = ("course__semester",)
	search_fields = ("title", "course__title")


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
	list_display = ("__str__", "assignment", "submitted")
	filter_horizontal = ("users",)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
	list_display = ("title", "course")
	search_fields = ("title", "course__title")
