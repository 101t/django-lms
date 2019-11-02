import factory
from datetime import datetime, timedelta, time
from django.contrib.auth.models import User, Group
from models import Course, CourseEvent, Semester, Assignment

class SemesterFactory(factory.Factory):
    FACTORY_FOR = Semester

    name = 'Fall'
    year = unicode(datetime.now().year)
    start = datetime.now().date() - timedelta(days = 30)
    end = datetime.now().date() + timedelta(days = 30)
    
class CourseFactory(factory.Factory):
    FACTORY_FOR = Course

    title = 'Test Title'
    section = '001'
    number = '101'
    description = 'Test Course<br>It is a test.'
    semester = factory.LazyAttribute(lambda a: SemesterFactory())
    campus = 'main'
    location = '543'

class EventFactory(factory.Factory):
    FACTORY_FOR = CourseEvent

    course = factory.LazyAttribute(lambda a: CourseFactory())
    title = 'Lecture'
    start = time(9,0)
    end = time(11,0)
    recurrences = "RRULE:FREQ=WEEKLY;BYDAY=TU,TH"
    

class AssignmentFactory(factory.Factory):
    FACTORY_FOR = Assignment
    
    title = factory.Sequence(lambda n: 'Assignment {0}'.format(n))
    description = '<strong>Bold</strong> Assignment.'
    due_date = datetime.now().date() + timedelta(days = 7)

    
class FacultyFactory(factory.Factory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'faculty{0}'.format(n))
    email = factory.Sequence(lambda n: 'faculty{0}@example.com'.format(n))
    first_name = factory.Sequence(lambda n: 'faculty{0}'.format(n))
    last_name = 'smith'

    @classmethod
    def _prepare(cls, create, **kwargs):
        user = super(FacultyFactory, cls)._prepare(create, **kwargs)

        if create:
            group, created = Group.objects.get_or_create(name = 'Faculty')
            user.groups.add(group)

        return user
