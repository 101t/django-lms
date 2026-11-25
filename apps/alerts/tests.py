from django.contrib.auth.models import Group, User
from django.core import mail
from django.urls import reverse

import libs.test_utils as test_utils

from .models import Alert
from .tasks import send_alert, send_alert_to_groups

FIELDS = {"sent_by": "Tester", "title": "Test title", "details": "No details", "level": "info"}


class AlertTest(test_utils.AuthenticatedTest):
	def test_acknowledge(self):
		alert = Alert.objects.create(sent_to=self.user, **FIELDS)
		self.c.post(reverse("alerts:acknowledge", args=[alert.id]))
		self.assertFalse(Alert.objects.filter(id=alert.id).exists())

	def test_cannot_acknowledge_others_alert(self):
		other = User.objects.create(username="other")
		alert = Alert.objects.create(sent_to=other, **FIELDS)
		self.assertEqual(self.c.post(reverse("alerts:acknowledge", args=[alert.id])).status_code, 404)
		self.assertTrue(Alert.objects.filter(id=alert.id).exists())

	def test_alert_all(self):
		for i in range(100):
			User.objects.create(username=f"user_{i}")
		send_alert(User.objects.all(), **FIELDS)
		self.assertEqual(Alert.objects.count(), User.objects.count())

	def test_alert_groups(self):
		group1 = Group.objects.create(name="test1")
		group2 = Group.objects.create(name="test2")
		for i in range(25):
			User.objects.create(username=f"user_{i}").groups.add(group1)
		for i in range(25, 50):
			User.objects.create(username=f"user_{i}").groups.add(group1, group2)
		for i in range(50, 100):
			User.objects.create(username=f"user_{i}")
		send_alert_to_groups([group1, group2], **FIELDS)
		self.assertEqual(Alert.objects.count(), 50)

	def test_alert_email(self):
		self.user.profile.preferences = {"email_alerts": True}
		self.user.profile.save()
		User.objects.create(username="quiet", email="quiet@example.com")
		with self.captureOnCommitCallbacks(execute=True):
			send_alert(User.objects.all(), **FIELDS)
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(mail.outbox[0].to, [self.user.email])

	def test_admin_broadcast(self):
		self.user.is_staff = self.user.is_superuser = True
		self.user.save()
		group = Group.objects.create(name="g")
		for i in range(3):
			User.objects.create(username=f"g{i}").groups.add(group)
		response = self.c.post(
			reverse("admin:alerts_alert_add"),
			{"audience": "groups", "groups": [group.pk], "title": "Hi", "details": "", "level": "info"},
		)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(Alert.objects.filter(title="Hi").count(), 3)
