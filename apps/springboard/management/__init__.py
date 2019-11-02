import os

from django.db.models.signals import post_syncdb
from apps.springboard import models
from django.core.files import File

def create_springboard_items(sender, **kwargs):
    # Check if IntranetApplication model was created

    if models.IntranetApplication in kwargs['created_models']:
        # Add our models
        here = os.path.dirname( os.path.abspath(__file__) )

        # The admin
        f = open(here + '/gear.png')
        application, created = models.IntranetApplication.objects.get_or_create(url = '/admin', title='Admin')
        if created:
            application.save()
            application.icon.save('gear.png', File(f))

        # Courses
        f = open(here + '/chalkboard.png')
        application, created = models.IntranetApplication.objects.get_or_create(url = '/courses', title='Courses')
        if created:
            application.save()
            application.icon.save('chalkboard.png', File(f))


post_syncdb.connect(create_springboard_items, sender = models)
