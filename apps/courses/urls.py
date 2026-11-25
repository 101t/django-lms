from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = "courses"


def route(pattern, view, name):
	return path(pattern, login_required(view.as_view()), name=name)


urlpatterns = [
	route("", views.CourseDropPage, "drop_page"),
	route("semester/browse/", views.SemesterList, "semester_list"),
	route("semester/<int:pk>/", views.BySemesterList, "by_semester"),
	# Course
	route("<int:pk>/overview/", views.CourseOverview, "overview"),
	route("<int:pk>/members/", views.CourseMembers, "members"),
	route("<int:pk>/admin/", views.CourseAdmin, "admin"),
	route("<int:pk>/toggle-membership/", views.ToggleMembership, "toggle-membership"),
	# Resources
	route("<int:pk>/resources/", views.ResourceList, "resources"),
	route("<int:pk>/resources/create/", views.NewCourseResource, "resource_create"),
	route("resources/<int:pk>/details/", views.ResourceDetails, "resource_details"),
	route("resources/<int:pk>/edit/", views.EditResource, "edit_resource"),
	route("resources/<int:pk>/delete/", views.DeleteResource, "delete_resource"),
	# Assignments
	route("<int:pk>/assignments/", views.AssignmentList, "assignments"),
	route("<int:pk>/assignments/new/", views.NewCourseAssignment, "new_assignment"),
	route("assignment/<int:pk>/overview/", views.AssignmentOverview, "assignment_overview"),
	route("assignment/<int:pk>/edit/", views.EditAssignment, "edit_assignment"),
	route("assignment/<int:pk>/delete/", views.DeleteAssignment, "delete_assignment"),
	route("assignment/<int:pk>/submit/", views.SubmitAssignment, "submit_assignment"),
	route("assignment/<int:pk>/team_submit/", views.TeamSubmitAssignment, "team_submit_assignment"),
	route("assignment_submission/<int:pk>/delete/", views.DeleteSubmission, "delete_submission"),
	# Calendars
	route("calendar/", views.CourseCalendar, "calendar"),
	route("calendar/<int:semester>/", views.CourseCalendar, "calendar"),
	route("calendar/<int:year>/<int:month>/<int:day>/", views.CourseCalendarDay, "calendar_day"),
	route("user_calendar/", views.UserCourseCalendar, "user_calendar"),
	route("user_calendar/<int:semester>/", views.UserCourseCalendar, "user_calendar"),
	route("user_calendar/<int:year>/<int:month>/<int:day>/", views.UserCourseCalendarDay, "user_calendar_day"),
]
