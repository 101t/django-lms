import datetime

from django.contrib.auth.models import User
from django.urls import reverse

import libs.test_utils as test_utils
from apps.profiles.models import Degree, Profile, UserDegree


class ProfilesTest(test_utils.AuthenticatedTest):
	"""
	Tests for our profiles application.
	"""

	def test_create(self):
		user = User(username="profiletest")
		user.save()

		# Test if we have a profile created. It should be created when a user is saved.
		profile = Profile.objects.get(user=user)
		assert profile

	def test_edit(self):
		response = self.c.get(reverse("profiles:edit", kwargs={"username": self.user.username}))
		self.assertEqual(response.status_code, 200)

		response = self.c.post(
			reverse("profiles:edit", kwargs={"username": self.user.username}),
			{
				"biography": "Some test <bold>text</bold>",
				"resume": open("apps/profiles/test_files/test.pdf", "rb"),
				"mugshot": open("apps/profiles/test_files/profile.gif", "rb"),
			},
		)

		self.assertEqual(response.status_code, 302)
		self.user.profile.refresh_from_db()
		self.assertEqual(self.user.profile.biography, "Some test <bold>text</bold>")
		self.assertTrue(self.user.profile.mugshot)

	def test_alum(self):
		from apps.courses.models import Semester

		# User shouldn't be a grad yet
		profile = Profile.objects.get(user=self.user)
		self.assertEqual(profile.is_alum, False)

		# Add an old degree
		last_year = datetime.datetime.now() - datetime.timedelta(days=365)
		semester = Semester.objects.create(
			name="Old",
			year=last_year.year,
			start=last_year,
			end=(last_year + datetime.timedelta(days=30)),
		)

		degree = Degree.objects.create(name="Bachelor or Science", abbreviation="B.S.")
		UserDegree.objects.create(
			user=self.user,
			degree=degree,
			graduation=semester,
		)

		self.assertEqual(profile.is_alum, True)

	def test_edit_preferences(self):
		response = self.c.get(reverse("profiles:preference_edit", kwargs={"username": self.user.username}))
		self.assertEqual(response.status_code, 200)

		response = self.c.post(
			reverse("profiles:preference_edit", kwargs={"username": self.user.username}),
			{
				"email_alerts": "1",
			},
		)

		self.assertEqual(response.status_code, 302)
		self.user.profile.refresh_from_db()
		self.assertEqual(self.user.profile.preferences["email_alerts"], True)

	def test_untick_preference(self):
		url = reverse("profiles:preference_edit", kwargs={"username": self.user.username})
		self.c.post(url, {"email_alerts": "1"})
		self.c.post(url, {})
		self.user.profile.refresh_from_db()
		self.assertFalse(self.user.profile.preferences["email_alerts"])
