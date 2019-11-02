import re, datetime
from dateutil import relativedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group, User
from tinymce import models as tinymce_models
from django.db.models import permalink
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import PhoneNumberField

from libs.fields import JSONField
from courses.models import Semester

class Degree(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=100)

class Profile(models.Model):
    GENDER_CHOICES = (
        (1, 'Male'),
        (2, 'Female'),
    )

    user = models.OneToOneField(User, related_name = 'profile')
    mugshot = models.ImageField(_('mugshot'), upload_to='mugshots/', blank=True)
    resume = models.FileField(_('resume'), upload_to='resumes/', blank=True)
    data = JSONField(null = True, blank = True)
    preferences = JSONField(null = True, blank = True)

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
        db_table = 'user_profiles'

    def __unicode__(self):
        return u"%s" % self.user.get_full_name()

    @permalink
    def get_absolute_url(self):
        return ('profile_detail', None, { 'username': self.user.username })

    @property
    def sms_address(self):
        if (self.mobile and self.mobile_provider):
            return u"%s@%s" % (re.sub('-', '', self.mobile), self.mobile_provider.domain)

    @property
    def is_alum(self):
        degrees = UserDegree.objects.filter(user = self.user)
        if len(degrees) > 0:
            for degree in degrees:
                if degree.graduation.end < datetime.datetime.now().date():
                    return True
        return False

class UserDegree(models.Model):
    graduation = models.ForeignKey(Semester)
    degree = models.ForeignKey(Degree)
    user = models.ForeignKey(User)

    @property
    def is_expected(self):
        return self.graduation.end > datetime.date.today()

    def __unicode__(self):
        if not self.is_expected :
            return "{} {}".format(self.degree.name, self.graduation)
        else:
            return "{} {} (expected)".format(self.degree.name, self.graduation)

# We may use this later

# class MobileProvider(models.Model):
#     """MobileProvider model"""
#     title = models.CharField(_('title'), max_length=25)
#     domain = models.CharField(_('domain'), max_length=50, unique=True)

#     class Meta:
#         verbose_name = _('mobile provider')
#         verbose_name_plural = _('mobile providers')
#         db_table = 'user_mobile_providers'

#     def __unicode__(self):
#         return u"%s" % self.title


    
            
class ServiceType(models.Model):
    """Service type model"""
    title = models.CharField(_('title'), blank=True, max_length=100)
    url = models.URLField(_('url'), blank=True, help_text='URL with a single \'{user}\' placeholder to turn a username into a service URL.') # , verify_exists=False

    class Meta:
        verbose_name = _('service type')
        verbose_name_plural = _('service types')
        db_table = 'user_service_types'

    def __unicode__(self):
        return u"%s" % self.title


class Service(models.Model):
    """Service model"""
    service = models.ForeignKey(ServiceType)
    profile = models.ForeignKey(Profile)
    username = models.CharField(_('Name or ID'), max_length=100, help_text="Username or id to be inserted into the service url.")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('service')
        verbose_name_plural = _('services')
        db_table = 'user_services'

    def __unicode__(self):
        return u"%s" % self.username

    @property
    def service_url(self):
        return re.sub('{user}', self.username, self.service.url)

    @property
    def title(self):
        return u"%s" % self.service.title


def user_post_save(sender, instance, **kwargs):
    profile, new = Profile.objects.get_or_create(user=instance)
    if new:
        profile.data = {}
        profile.preferences = {}
        profile.save()

models.signals.post_save.connect(user_post_save, sender=User)
