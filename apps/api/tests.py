from django.contrib.auth.models import User
from django.urls import reverse

import libs.test_utils as test_utils
from apps.alerts.models import Alert
from apps.courses.factories import AssignmentFactory, CourseFactory


class ApiTest(test_utils.AuthenticatedTest):
	def test_requires_auth(self):
		self.c.logout()
		self.assertEqual(self.c.get("/api/v1/courses/").status_code, 403)

	def test_private_courses_hidden(self):
		public = CourseFactory(title="Public")
		private = CourseFactory(title="Private", private=True)
		AssignmentFactory(course=private)
		titles = [c["title"] for c in self.c.get("/api/v1/courses/").json()["results"]]
		self.assertEqual(titles, [public.title])
		self.assertEqual(self.c.get("/api/v1/assignments/").json()["count"], 0)
		private.members.add(self.user)
		self.assertEqual(self.c.get("/api/v1/assignments/").json()["count"], 1)

	def test_alerts_are_personal(self):
		other = User.objects.create(username="other")
		mine = Alert.objects.create(sent_to=self.user, title="mine")
		theirs = Alert.objects.create(sent_to=other, title="theirs")
		self.assertEqual([a["title"] for a in self.c.get("/api/v1/alerts/").json()["results"]], ["mine"])
		self.assertEqual(self.c.delete(f"/api/v1/alerts/{theirs.pk}/").status_code, 404)
		self.assertEqual(self.c.delete(f"/api/v1/alerts/{mine.pk}/").status_code, 204)

	def test_me_and_docs(self):
		self.assertEqual(self.c.get("/api/v1/me/").json()["username"], self.user.username)
		self.assertEqual(self.c.get(reverse("api-schema")).status_code, 200)
		self.assertEqual(self.c.get(reverse("api-docs")).status_code, 200)
