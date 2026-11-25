import datetime
import re

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.courses.models import Semester


class Degree(models.Model):
	name = models.CharField(max_length=100)
	abbreviation = models.CharField(max_length=100)

	def __str__(self):
		return self.abbreviation or self.name


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
	mugshot = models.ImageField(_("mugshot"), upload_to="mugshots/", blank=True)
	resume = models.FileField(_("resume"), upload_to="resumes/", blank=True)
	data = models.JSONField(default=dict, null=True, blank=True)
	preferences = models.JSONField(default=dict, null=True, blank=True)

	class Meta:
		verbose_name = _("user profile")
		verbose_name_plural = _("user profiles")
		db_table = "user_profiles"

	def __str__(self):
		return self.user.get_full_name() or self.user.username

	def get_absolute_url(self):
		return reverse("profiles:detail", kwargs={"username": self.user.username})

	@property
	def biography(self):
		return (self.data or {}).get("biography", "")

	@property
	def is_alum(self):
		return UserDegree.objects.filter(user=self.user, graduation__end__lt=datetime.date.today()).exists()


class UserDegree(models.Model):
	graduation = models.ForeignKey(Semester, on_delete=models.CASCADE)
	degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	@property
	def is_expected(self):
		return self.graduation.end > datetime.date.today()

	def __str__(self):
		suffix = " (expected)" if self.is_expected else ""
		return f"{self.degree.name} {self.graduation}{suffix}"


class ServiceType(models.Model):
	title = models.CharField(_("title"), blank=True, max_length=100)
	url = models.URLField(
		_("url"), blank=True, help_text="URL with a single '{user}' placeholder to turn a username into a service URL."
	)

	class Meta:
		verbose_name = _("service type")
		verbose_name_plural = _("service types")
		db_table = "user_service_types"

	def __str__(self):
		return self.title


class Service(models.Model):
	service = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	username = models.CharField(
		_("Name or ID"), max_length=100, help_text="Username or id to be inserted into the service url."
	)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = _("service")
		verbose_name_plural = _("services")
		db_table = "user_services"

	def __str__(self):
		return self.username

	@property
	def service_url(self):
		return re.sub("{user}", self.username, self.service.url)

	@property
	def title(self):
		return self.service.title


def user_post_save(sender, instance, **kwargs):
	Profile.objects.get_or_create(user=instance)


models.signals.post_save.connect(user_post_save, sender=User, dispatch_uid="profiles_user_post_save")
