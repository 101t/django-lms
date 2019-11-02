from django.db.models.signals import post_syncdb
from django.contrib.auth import models

def create_groups(sender, **kwargs):
    # Check if groups model was created
    if models.Group in kwargs['created_models']:
        # Add our groups
        models.Group.objects.get_or_create(name = "Students")
        models.Group.objects.get_or_create(name = "Faculty")
        models.Group.objects.get_or_create(name = "Admissions")


post_syncdb.connect(create_groups, sender = models)
