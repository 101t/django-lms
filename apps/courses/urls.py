from django.conf.urls.defaults import *
from courses.views import (CourseOverview,
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

urlpatterns = patterns('',
    url('^$', login_required(CourseDropPage.as_view()), name = 'drop_page'),
    url('^(?P<pk>\w+)/overview/$', login_required(CourseOverview.as_view()), name = 'overview'),
    url('^semester/browse/$', login_required(SemesterList.as_view()), name = 'semester_list'),
    url('^semester/(?P<pk>\w+)/$', login_required(BySemesterList.as_view()), name = 'by_semester'),

    url('^(?P<pk>\w+)/members/$', login_required(CourseMembers.as_view()), name = 'members'),
    url('^(?P<pk>\w+)/admin/$', login_required(CourseAdmin.as_view()), name = 'admin'),
    url('^(?P<pk>\w+)/toggle-membership/$', login_required(ToggleMembership.as_view()), name = 'toggle-membership'),

    # Resources
    url('^resources/(?P<pk>\w+)/details/$', login_required(ResourceDetails.as_view()), name = 'resource_details'),
    url('^resources/(?P<pk>\w+)/edit/$', login_required(EditResource.as_view()), name = 'edit_resource'),
    url('^(?P<pk>\w+)/resources/create/$', login_required(NewCourseResource.as_view()), name = 'resource_create'),
    url('^(?P<pk>\w+)/resources/$', login_required(ResourceList.as_view()), name = 'resources'),
    url('^resources/delete/$', login_required(DeleteResource.as_view()), name = 'delete_resource'),

    # Assignments
    url('^assignment/delete/$', login_required(DeleteAssignment.as_view()), name = 'delete_assignment'),
    url('^(?P<pk>\w+)/assignments/new/$', login_required(NewCourseAssignment.as_view()), name = 'new_assignment'),
    url('^(?P<pk>\w+)/assignments/$', login_required(AssignmentList.as_view()), name = 'assignments'), 
    url('^assignment/(?P<pk>\w+)/overview/$', login_required(AssignmentOverview.as_view()), name = 'assignment_overview'),
    url('^(?P<pk>\w+)/assignments/submit/$', login_required(SubmitAssignment.as_view()), name = 'submit_assignment'),
    url('^assignment/(?P<pk>\w+)/edit/$', login_required(EditAssignment.as_view()), name = 'edit_assignment'),
    url('^(?P<pk>\w+)/assignments/team_submit/$', login_required(TeamSubmitAssignment.as_view()), name = 'team_submit_assignment'),
    url('^assignment_submission/delete/$', login_required(DeleteSubmission.as_view()), name = 'delete_submission'),

    # Schedule
    url('^calendar/$', login_required(CourseCalendar.as_view()), name = 'calendar'),
    url('^calendar/(?P<semester>\d+)/$', login_required(CourseCalendar.as_view()), name = 'calendar'),
    url('^calendar/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', login_required(CourseCalendarDay.as_view()), name = 'calendar_day'),

    # Schedule
    url('^user_calendar/$', login_required(UserCourseCalendar.as_view()), name = 'user_calendar'),
    url('^user_calendar/(?P<semester>\d+)/$', login_required(UserCourseCalendar.as_view()), name = 'user_calendar'),
    url('^user_calendar/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', login_required(UserCourseCalendarDay.as_view()), name = 'user_calendar_day'),
)
