from django.urls import re_path as url
from apps.courses.views import (CourseOverview,
                                CourseCalendar,
                                CourseCalendarDay,
                                UserCourseCalendar,
                                UserCourseCalendarDay,
                                BySemesterList,
                                SemesterList,
                                CourseDropPage,
                                CourseAdmin,
                                ToggleMembership,
                                NewCourseAssignment,
                                AssignmentList,
                                AssignmentOverview,
                                SubmitAssignment,
                                TeamSubmitAssignment,
                                DeleteSubmission,
                                CourseMembers,
                                ResourceList,
                                ResourceDetails,
                                NewCourseResource,
                                EditResource,
                                EditAssignment,
                                DeleteResource,
                                DeleteAssignment)
from django.contrib.auth.decorators import login_required

app_name = "courses"

urlpatterns = [
	url(r'^$', login_required(CourseDropPage.as_view()), name='drop_page'),
	url(r'^(?P<pk>\w+)/overview/$', login_required(CourseOverview.as_view()), name='overview'),
	url(r'^semester/browse/$', login_required(SemesterList.as_view()), name='semester_list'),
	url(r'^semester/(?P<pk>\w+)/$', login_required(BySemesterList.as_view()), name='by_semester'),

	url(r'^(?P<pk>\w+)/members/$', login_required(CourseMembers.as_view()), name='members'),
	url(r'^(?P<pk>\w+)/admin/$', login_required(CourseAdmin.as_view()), name='admin'),
	url(r'^(?P<pk>\w+)/toggle-membership/$', login_required(ToggleMembership.as_view()), name='toggle-membership'),

	# Resources
	url(r'^resources/(?P<pk>\w+)/details/$', login_required(ResourceDetails.as_view()), name='resource_details'),
	url(r'^resources/(?P<pk>\w+)/edit/$', login_required(EditResource.as_view()), name='edit_resource'),
	url(r'^(?P<pk>\w+)/resources/create/$', login_required(NewCourseResource.as_view()), name='resource_create'),
	url(r'^(?P<pk>\w+)/resources/$', login_required(ResourceList.as_view()), name='resources'),
	url(r'^resources/delete/$', login_required(DeleteResource.as_view()), name='delete_resource'),

	# Assignments
	url(r'^assignment/delete/$', login_required(DeleteAssignment.as_view()), name='delete_assignment'),
	url(r'^(?P<pk>\w+)/assignments/new/$', login_required(NewCourseAssignment.as_view()), name='new_assignment'),
	url(r'^(?P<pk>\w+)/assignments/$', login_required(AssignmentList.as_view()), name='assignments'),
	url(r'^assignment/(?P<pk>\w+)/overview/$', login_required(AssignmentOverview.as_view()), name='assignment_overview'),
	url(r'^(?P<pk>\w+)/assignments/submit/$', login_required(SubmitAssignment.as_view()), name='submit_assignment'),
	url(r'^assignment/(?P<pk>\w+)/edit/$', login_required(EditAssignment.as_view()), name='edit_assignment'),
	url(r'^(?P<pk>\w+)/assignments/team_submit/$', login_required(TeamSubmitAssignment.as_view()),
	    name='team_submit_assignment'),
	url(r'^assignment_submission/delete/$', login_required(DeleteSubmission.as_view()), name='delete_submission'),

	# Schedule
	url(r'^calendar/$', login_required(CourseCalendar.as_view()), name='calendar'),
	url(r'^calendar/(?P<semester>\d+)/$', login_required(CourseCalendar.as_view()), name='calendar'),
	url(r'^calendar/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', login_required(CourseCalendarDay.as_view()),
	    name='calendar_day'),

	# Schedule
	url(r'^user_calendar/$', login_required(UserCourseCalendar.as_view()), name='user_calendar'),
	url(r'^user_calendar/(?P<semester>\d+)/$', login_required(UserCourseCalendar.as_view()), name='user_calendar'),
	url(r'^user_calendar/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', login_required(UserCourseCalendarDay.as_view()),
	    name='user_calendar_day'),
]
