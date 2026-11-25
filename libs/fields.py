from django.db import models


class JSONField(models.TextField):
	"""Kept only so historical migrations import. Use django.db.models.JSONField."""
