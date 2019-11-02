from django.core.management.base import BaseCommand, CommandError
from courses.factories import CourseFactory, AssignmentFactory, FacultyFactory
from courses.models import Semester

class Command(BaseCommand):
    help = 'Populates the database with test data'

    def handle(self, *args, **options):
        # Check if we have a semester
        try:
            semester = Semester.get_current()
            course = CourseFactory.create(semester = semester)
        except IndexError:
            course = CourseFactory.create()

        self.stdout.write('Created Course {}.\n'.format(course))

        assignment = AssignmentFactory.create(course = course)
        self.stdout.write('Created Assignment {}.\n'.format(assignment))

        faculty = FacultyFactory.create()
        course.faculty.add(faculty)
        self.stdout.write('Created Faculty {} and assigned to course.\n'.format(faculty))
        
        self.stdout.write('Successfully populated DB.\n')