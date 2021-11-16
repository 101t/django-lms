from django.db import models
from django.contrib.auth.models import Group


class IntranetApplication(models.Model):
    icon = models.ImageField(upload_to='images')
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    groups = models.ManyToManyField(Group, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Intranet Application"
