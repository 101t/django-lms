from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group

if settings.NONREL:
    from djangotoolbox.fields import ListField
    from libs.utils.fields import ForeignKey

class IntranetApplication(models.Model):
    icon = models.ImageField(upload_to = 'images')
    url = models.CharField(max_length = '255')
    title = models.CharField(max_length = '255')

    if settings.NONREL:
        groups = ListField(ForeignKey(Group, related_name="test"), blank=True)
    else:
        groups = models.ManyToManyField(Group, blank=True)

    #group = models.ForeignKey(Group)
    # groups = ListField(models.CharField(max_length="24"), blank=True)

    def __unicode__(self):
        return self.title
