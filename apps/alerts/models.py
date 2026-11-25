from django.contrib.auth.models import User
from django.db import models
from tinymce.models import HTMLField

ALERT_LEVELS = (
	("info", "Information"),
	("", "Warning"),
	("success", "Success"),
	("error", "Error"),
	("danger", "Danger"),
)


class Alert(models.Model):
	created = models.DateTimeField(auto_now_add=True, verbose_name="created")
	modified = models.DateTimeField(auto_now=True, verbose_name="modified")
	# Free text because alerts can come from people or from the system.
	sent_by = models.CharField(max_length=200)
	sent_to = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=200)
	details = HTMLField(blank=True)
	level = models.CharField(max_length=200, choices=ALERT_LEVELS, blank=True)
	sticky = models.BooleanField(default=False)

	class Meta:
		ordering = ["-created"]
		get_latest_by = "modified"

	def __str__(self):
		return self.title

	@property
	def css_level(self):
		"""Bootstrap 5 contextual class for this level."""
		return {"": "warning", "error": "danger"}.get(self.level, self.level)
