import datetime
import itertools
from collections import defaultdict
from dateutil import rrule

from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from libs.django_utils import render_to_response
from libs.class_views import JSONResponseMixin
from django.views.generic import (DetailView,
                                  ListView,
                                  RedirectView,
                                  UpdateView,
                                  CreateView,
                                  View,
                                  DeleteView,
                                  TemplateView
)
from django.views.generic.detail import SingleObjectMixin
from django.core import exceptions
from django.http import HttpResponse
from django.contrib.auth.models import User
from django_statsd.clients import statsd

from courses.models import Course, Semester, Assignment, AssignmentSubmission, Resource
from courses.forms import CourseAdminForm, AssignmentForm, SubmitAssignmentForm, TeamSubmitAssignmentForm, ResourceForm

from courses.coursecalendar import HTMLCourseCalendar

class CourseOverview(DetailView):
    name = "Course overview"
    context_object_name = "course"
    template_name = "courses/overview.html"

    queryset = Course.objects.all()

    def get_context_data(self, **kwargs):
        context = super(CourseOverview, self).get_context_data(**kwargs)
    
        # Check if user is a member
        context['is_member'] = self.request.user in context['course'].members.all()
        
        return context

    # Overriding the dispatch to check visibility
    def dispatch(self, request, *args, **kwargs):
        # set the kwargs so we can get the object
        self.kwargs = kwargs
        course = self.get_object()

        if course.private:
            if request.user not in itertools.chain(course.faculty.all(), course.members.all(), course.teaching_assistants.all()) and not request.user.is_superuser:
                raise exceptions.PermissionDenied

        return super(CourseOverview, self).dispatch(request, *args, **kwargs)

class CourseMembers(CourseOverview):
    template_name = "courses/members.html"

    def dispatch(self, request, *args, **kwargs):
        self.kwargs = kwargs
        course = self.get_object()
        return super(CourseMembers, self).dispatch(request, *args, **kwargs)

# TODO: Check if user is faculty
class CourseAdmin(UpdateView):
    name = "Course admin"
    form_class = CourseAdminForm
    template_name = "courses/admin.html"

    queryset = Course.objects.all()

    def get_success_url(self):
        course = self.get_object()
        return reverse('courses:admin', kwargs={'pk':course.id})


class BySemesterList(ListView):
    name = "Courses by semester"
    context_object_name = "courses"
    template_name = "courses/by_semester.html"

    def get_queryset(self):
        self.semester = get_object_or_404(Semester, pk=self.kwargs['pk'])
        courses = Course.objects.filter(semester = self.semester)
        return courses

    def get_context_data(self, **kwargs):
        context = super(BySemesterList, self).get_context_data(**kwargs)
        context['semester'] = self.semester
        
        return context

class SemesterList(ListView):
    name = "Semester List"
    context_object_name = "semesters"
    template_name = "courses/semester_list.html"
    queryset = Semester.objects.all()

        
class CourseDropPage(RedirectView):
    '''
    Gets the current semester and redirects to its page
    '''
    url = None
    permanent = False

    def get_redirect_url(self, **kwargs):
        try:
            semester = Semester.get_current()
        except IndexError:
            # Get the latest semester and use that
            try:
                semester = Semester.objects.order_by('end')[0]
            except IndexError:
                messages.error(self.request, 'The system has no semesters')
                return ('/')

        return reverse('courses:by_semester', kwargs={'pk':semester.id})


class ToggleMembership(View, SingleObjectMixin, JSONResponseMixin):
    queryset = Course.objects.all()
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if request.user in self.object.members.all():
            self.object.members.remove(request.user)
            self.object.save()
            status = "removed"
        else:
            self.object.members.add(request.user)
            self.object.save()
            status = "added"
        context = {'status':status}
        return self.render_to_response(context)

class NewCourseAssignment(CreateView):
    name = "New Assignment"
    model = Assignment
    form_class = AssignmentForm
    template_name = "courses/new_assignment.html"

    def get_initial(self):
        '''
        Overriding this method to set the course id for the form
        '''
        return {'course': self.kwargs['pk']}

    def get_success_url(self):
        course = Course.objects.get(pk = self.kwargs['pk'])
        return reverse('courses:assignments', kwargs={'pk':course.id})

    def get_context_data(self, **kwargs):
        context = super(NewCourseAssignment, self).get_context_data(**kwargs)
        context['course'] = Course.objects.get(pk = self.kwargs['pk'])
        
        return context

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.course = Course.objects.get(pk = self.kwargs['pk'])
        self.object.save()
        return super(NewCourseAssignment, self).form_valid(form)

    # Overriding the dispatch to check permissions
    def dispatch(self, request, *args, **kwargs):
        # set the kwargs so we can get the object
        self.kwargs = kwargs
        course = Course.objects.get(pk = self.kwargs['pk'])

        if request.user not in course.faculty.all() and not request.user.is_superuser:
            raise exceptions.PermissionDenied

        return super(NewCourseAssignment, self).dispatch(request, *args, **kwargs)

class AssignmentList(ListView):
    name = "Assignment list"
    context_object_name = "assignments"
    template_name = "courses/assignement_list.html"

    def get_queryset(self):
        self.course = get_object_or_404(Course, pk=self.kwargs['pk'])
        return self.course.assignment_set.all()

    def get_context_data(self, **kwargs):
        context = super(AssignmentList, self).get_context_data(**kwargs)
        context['course'] = self.course

        return context

class AssignmentOverview(DetailView):
    name = "Assignment overview"
    context_object_name = "assignment"
    template_name = "courses/assignment_overview.html"

    queryset = Assignment.objects.all()

    def get_template_names(self):
        return self.template_name
    

    def get_context_data(self, **kwargs):
        context = super(AssignmentOverview, self).get_context_data(**kwargs)
        context['course'] = self.get_object().course

        
        # If the course faculty, return all submissions
        if self.request.user in self.get_object().course.faculty.all():
            context['submissions'] = AssignmentSubmission.objects.filter(assignment = self.get_object())
        else:
            # If course member get any submissions the member has submitted
            context['submissions'] = AssignmentSubmission.objects.filter(users = self.request.user, assignment = self.get_object())
    
        return context

    # Overriding the dispatch to check visibility
    def dispatch(self, request, *args, **kwargs):
        # set the kwargs so we can get the object
        self.kwargs = kwargs
        course = self.get_object().course

        if course.private:
            if request.user not in course.faculty and request.user not in course.members and not request.user.is_superuser:
                raise exceptions.PermissionDenied

        return super(AssignmentOverview, self).dispatch(request, *args, **kwargs)

class SubmitAssignment(CreateView):
    name = "Submit assignment"
    model = AssignmentSubmission
    form_class = SubmitAssignmentForm
    template_name = "courses/submit_assignment.html"

    def get_initial(self):
        '''
        Overriding this method to set the assignment id for the form
        '''
        return {'course': self.kwargs['pk']}

    def get_success_url(self):
        assignment = Assignment.objects.get(pk = self.kwargs['pk'])
        return reverse('courses:assignment_overview', kwargs={'pk':assignment.id})

    def get_context_data(self, **kwargs):
        context = super(SubmitAssignment, self).get_context_data(**kwargs)
        context['assignment'] = Assignment.objects.get(pk = self.kwargs['pk'])
        context['course'] = context['assignment'].course

        return context

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.assignment = Assignment.objects.get(pk = self.kwargs['pk'])
        self.object.save()
        self.object.users.add(self.request.user)

        if self.object.file:
            statsd.incr("courses.{}.{}.assignments.storage".format(self.object.assignment.course, self.object.assignment.course.semester, self.object.file.size))
        
        return super(SubmitAssignment, self).form_valid(form)

    # Overriding the dispatch to check permissions
    def dispatch(self, request, *args, **kwargs):
        # set the kwargs so we can get the object
        self.kwargs = kwargs
        self.assignment = Assignment.objects.get(pk = self.kwargs['pk'])

        course = self.assignment.course
        
        if request.user not in self.assignment.course.members.all() and not request.user.is_superuser:
                raise exceptions.PermissionDenied

        return super(SubmitAssignment, self).dispatch(request, *args, **kwargs)

class DeleteSubmission(DeleteView):
    name = "Delete assignment submission"
    template_name = "courses/delete_submission.html"

    queryset = AssignmentSubmission.objects.all()

    def get_success_url(self):
        return reverse('courses:assignment_overview', kwargs={'pk':self.assignment.id})

    def get_context_data(self, **kwargs):
        context = super(DeleteSubmission, self).get_context_data(**kwargs)
        return context

    # Here we set the pk into the kwargs because we're calling this by ajax. We can't reverse the url on the client side because we don't have the id until it's clicked
    def get_object(self, queryset=None):
        self.kwargs['pk'] = self.request.POST.get('id', None)

        # Set the old assignment here so I know where to redirect to
        return super(DeleteSubmission, self).get_object(queryset)

    # Override delete so we save the old object. Return the url to redirect to
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.assignment = self.object.assignment
        self.object.delete()

        return HttpResponse(self.get_success_url())

class TeamSubmitAssignment(SubmitAssignment):
    name = "Submit assignment for team"
    form_class = TeamSubmitAssignmentForm

    def get_form(self, form_class):
        form = super(TeamSubmitAssignment, self).get_form(form_class)

        form.fields['users'].queryset =  User.objects.filter(id__in = [user.id for user in self.assignment.course.members.all()])

        return form

class NewCourseResource(CreateView):
    name = "New course resource"
    model = Resource
    form_class = ResourceForm
    template_name = "courses/new_resource.html"

    def get_initial(self):
        '''
        Overriding this method to set the course id for the form
        '''
        return {'course': self.kwargs['pk']}

    def get_success_url(self):
        course = Course.objects.get(pk = self.kwargs['pk'])
        return reverse('courses:resources', kwargs={'pk':course.id})

    def get_context_data(self, **kwargs):
        context = super(NewCourseResource, self).get_context_data(**kwargs)
        context['course'] = Course.objects.get(pk = self.kwargs['pk'])
        
        return context

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.course = Course.objects.get(pk = self.kwargs['pk'])
        self.object.save()
        return super(NewCourseResource, self).form_valid(form)

    # Overriding the dispatch to check permissions
    def dispatch(self, request, *args, **kwargs):
        # set the kwargs so we can get the object
        self.kwargs = kwargs
        course = Course.objects.get(pk = self.kwargs['pk'])

        if request.user not in course.faculty.all() and not request.user.is_superuser:
                raise exceptions.PermissionDenied

        return super(NewCourseResource, self).dispatch(request, *args, **kwargs)

class ResourceList(ListView):
    name = "Resource list"
    context_object_name = "resources"
    template_name = "courses/resource_list.html"

    def get_queryset(self):
        self.course = get_object_or_404(Course, pk=self.kwargs['pk'])
        return self.course.resource_set.all()

    def get_context_data(self, **kwargs):
        context = super(ResourceList, self).get_context_data(**kwargs)
        context['course'] = self.course

        return context

class ResourceDetails(DetailView):
    name = "Resource details"
    context_object_name = "resource"
    template_name = "courses/resource_details.html"

    queryset = Resource.objects.all()

    def get_template_names(self):
        return self.template_name
    

    def get_context_data(self, **kwargs):
        context = super(ResourceDetails, self).get_context_data(**kwargs)
        context['course'] = self.get_object().course
    
        return context

    # Overriding the dispatch to check visibility
    def dispatch(self, request, *args, **kwargs):
        # set the kwargs so we can get the object
        self.kwargs = kwargs
        course = self.get_object().course

        if course.private:
            if request.user not in course.faculty.all() and request.user not in course.members.all() and not request.user.is_superuser:
                raise exceptions.PermissionDenied

        return super(ResourceDetails, self).dispatch(request, *args, **kwargs)

class DeleteResource(DeleteView):
    name = "Delete resource"
    template_name = "courses/delete_resource.html"

    queryset = Resource.objects.all()

    def get_success_url(self):
        return reverse('courses:resources', kwargs={'pk':self.course.id})

    def get_context_data(self, **kwargs):
        context = super(DeleteResource, self).get_context_data(**kwargs)
        return context

    # Here we set the pk into the kwargs because we're calling this by ajax. We can't reverse the url on the client side because we don't have the id until it's clicked
    def get_object(self, queryset=None):
        self.kwargs['pk'] = self.request.POST.get('id', None)

        # Set the old assignment here so I know where to redirect to
        return super(DeleteResource, self).get_object(queryset)

    # Override delete so we save the old object. Return the url to redirect to
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.course = self.object.course
        self.object.delete()

        return HttpResponse(self.get_success_url())

class DeleteAssignment(DeleteView):
    name = "Delete assignment"
    template_name = "courses/delete_assignment.html"

    queryset = Assignment.objects.all()

    def get_success_url(self):
        return reverse('courses:assignments', kwargs={'pk':self.course.id})

    def get_context_data(self, **kwargs):
        context = super(DeleteAssignment, self).get_context_data(**kwargs)
        return context

    # Here we set the pk into the kwargs because we're calling this by ajax. We can't reverse the url on the client side because we don't have the id until it's clicked
    def get_object(self, queryset=None):
        self.kwargs['pk'] = self.request.POST.get('id', None)

        # Set the old assignment here so I know where to redirect to
        return super(DeleteAssignment, self).get_object(queryset)

    # Override delete so we save the old object. Return the url to redirect to
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.course = self.object.course
        self.object.delete()

        return HttpResponse(self.get_success_url())



class EditAssignment(UpdateView):
    name = "Edit assignment"
    template_name = 'courses/new_assignment.html'
    form_class = AssignmentForm
    queryset = Assignment.objects.all()

    def get_success_url(self):
        course = Course.objects.get(pk = self.kwargs['pk'])
        return reverse('courses:assignments', kwargs={'pk':course.id})

    def get_context_data(self, **kwargs):
        context = super(EditAssignment, self).get_context_data(**kwargs)
        context['course'] = self.get_object().course
        
        return context

    # Overriding the dispatch to check permissions
    def dispatch(self, request, *args, **kwargs):
        # set the kwargs so we can get the object
        self.kwargs = kwargs
        course = self.get_object().course

        if request.user not in course.faculty.all() and not request.user.is_superuser:
                raise exceptions.PermissionDenied

        return super(EditAssignment, self).dispatch(request, *args, **kwargs)


class EditResource(UpdateView):
    name = "Edit resource"
    template_name = 'courses/new_resource.html'
    form_class = ResourceForm
    queryset = Resource.objects.all()

    def get_success_url(self):
        
        return reverse('courses:resources', kwargs={'pk':self.object.course.id})

    def get_context_data(self, **kwargs):
        context = super(EditResource, self).get_context_data(**kwargs)
        context['course'] = self.get_object().course
        
        return context

    # Overriding the dispatch to check permissions
    def dispatch(self, request, *args, **kwargs):
        # set the kwargs so we can get the object
        self.kwargs = kwargs
        course = self.get_object().course

        if request.user not in course.faculty.all() and not request.user.is_superuser:
                raise exceptions.PermissionDenied

        return super(EditResource, self).dispatch(request, *args, **kwargs)

class CourseCalendar(TemplateView):
    template_name = 'courses/calendar.html'

    def get_events(self, semester):
        return semester.get_events()
    
    def get_context_data(self, **kwargs):
        context = super(CourseCalendar, self).get_context_data(**kwargs)
        if kwargs.get('semester', False):
            semester = Semester.objects.get(pk = kwargs['semester'])
        else:
            semester = Semester.get_current()
            
        events = self.get_events(semester)

        # Generate a calendar for every month in the semester
        calendars = []
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=semester.start, until=semester.end):
            calendars.append(HTMLCourseCalendar(events, user_cal = kwargs.get('user_cal', False)).formatmonth(dt.year, dt.month))

        context.update(locals())
        return context

class CourseCalendarDay(TemplateView):
    template_name = 'courses/calendar_day.html'

    def get_events(self, semester, month, day):
        return semester.get_events()[int(month)][int(day)]
    
    def get_context_data(self, year, month, day, **kwargs):
        context = super(CourseCalendarDay, self).get_context_data(**kwargs)
        date_object = datetime.datetime(int(year), int(month), int(day))

        semester = get_object_or_404(Semester, start__lte = date_object, end__gte = date_object)

        # TODO: This is very inefficient
        context['events'] = self.get_events(semester, month, day)
        context.update(locals())
        return context

class UserCourseCalendar(CourseCalendar):
    def get_events(self, semester):
        return semester.get_events(course_set = self.request.user.Members.all())

    def get_context_data(self, *args, **kwargs):
        kwargs.update({'user_cal': True})
        context = super(UserCourseCalendar, self).get_context_data(*args, **kwargs)
        context.update({'user_cal': True})
        return context
        
class UserCourseCalendarDay(CourseCalendarDay):
    def get_events(self, semester, month, day):
        return semester.get_events(course_set = self.request.user.Members.all())[int(month)][int(day)]
