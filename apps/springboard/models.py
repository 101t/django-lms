from django.contrib.auth.models import Group
from django.db import models


class IntranetApplication(models.Model):
	title = models.CharField(max_length=255)
	url = models.CharField(max_length=255)
	icon = models.ImageField(upload_to="images", blank=True, help_text="Optional image. Overrides the icon name.")
	icon_name = models.CharField(
		max_length=50,
		default="grid",
		help_text='A <a href="https://icons.getbootstrap.com/" target="_blank">Bootstrap Icons</a> name, e.g. "journal-bookmark".',
	)
	order = models.PositiveSmallIntegerField(default=0)
	groups = models.ManyToManyField(Group, blank=True, help_text="Leave empty to show to everyone.")

	class Meta:
		verbose_name = "Intranet Application"
		ordering = ["order", "title"]

	def __str__(self):
		return self.title
