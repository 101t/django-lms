import os

from django.core.files import File
from django.urls import reverse

import libs.test_utils as test_utils
from apps.alerts.models import Alert
from apps.springboard.models import IntranetApplication


class SpringboardTest(test_utils.AuthenticatedTest):
	def test_display_code(self):
		response = self.c.get(reverse("springboard:springboard"))
		self.assertEqual(response.status_code, 200)

	def test_display_icon(self):
		here = os.path.dirname(os.path.abspath(__file__))
		f = open(here + "/test_files/test_icon.png", "rb")
		application = IntranetApplication(url="/test", title="Test")
		application.save()
		application.icon.save("test_icon.png", File(f))

		response = self.c.get(reverse("springboard:springboard"))
		self.assertContains(response, "Test")

	def test_alerts(self):
		alert = Alert.objects.create(
			sent_by="Test",
			sent_to=self.user,
			title="Test alert",
			details="Stuff, stuff, stuff",
		)

		response = self.c.get(reverse("springboard:springboard"))

		assert alert in response.context["alerts"]

	def test_defaults(self):
		response = self.c.get(reverse("springboard:springboard"))

		self.assertContains(response, "Courses")
		self.assertContains(response, "My calendar")
		self.assertNotContains(response, "API docs")  # Faculty-only tile
