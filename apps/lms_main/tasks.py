import datetime

from itertools import chain
from celery.task import task
from courses.models import Course, Semester
from django.contrib.auth.models import User, Group


def get_yesterday_semester():
    return Semester.objects.get(end__lt = datetime.date.today(), end__gte = datetime.date.today() - datetime.timedelta(hours=24))

@task
def expire_course_visibility():
    '''
    Will run at the end of the semester.
    Courses set to private in the current semester will have their visibility reset.
    '''

    # Get the semester that ended yesterday
    try:
        current_semester = get_yesterday_semester()
    except Semester.DoesNotExist:
        return

    for course in current_semester.course_set.all():
        course.private = False
        course.save()

@task
def disable_faculty():
    '''
    Faculty or Adjunct Faculty who are not assigned a course next semester are disabled.
    '''

    try:
        current_semester = get_yesterday_semester()
    except Semester.DoesNotExist:
        return

    # Get set all Faculty
    try:
        all_faculty = set(Group.objects.get(name = 'Faculty').user_set.values_list('username', flat = True))
    except Group.DoesNotExist:
        return

    # Get set of all Faculty for the next semester
    next_faculty = set([instructor for instructor in chain([course.faculty.values_list('username', flat = True) for course in current_semester.get_next().course_set.all()])])

    # Subract next_faculty from the all_faculty set to get those faculty not teaching next semester
    faculty = all_faculty - next_faculty

    # Disable all the faculty left
    User.objects.filter(username__in = faculty).update(is_active = False)
        
        