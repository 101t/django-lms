import sys
import os
import datetime

from django.utils import unittest
import libs.test_utils as test_utils
from django.test.client import Client
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

from profiles.models import Profile, Degree, UserDegree

class ProfilesTest(test_utils.AuthenticatedTest):
    '''
    Tests for our profiles application.
    '''
    def test_create(self):
        user = User(username = 'profiletest')
        user.save()

        # Test if we have a profile created. It should be created when a user is saved.
        profile = Profile.objects.get(user = user)
        assert profile

    def test_edit(self):
        response = self.c.get(reverse('profiles:edit', kwargs={'username':self.user.username}))
        self.assertEquals(response.status_code, 200)


        response = self.c.post(reverse('profiles:edit', kwargs={'username':self.user.username}),
                               {'biography':'Some test <bold>text</bold>',
                                'resume': open('apps/profiles/test_files/test.pdf'),
                                'mugshot': open('apps/profiles/test_files/profile.gif'),
                                })

        self.assertEquals(response.status_code, 302)
    def test_alum(self):
        from apps.courses.models import Semester
        # User shouldn't be a grad yet
        profile = Profile.objects.get(user = self.user)
        self.assertEquals(profile.is_alum, False)

        # Add an old degree
        last_year = datetime.datetime.now() - datetime.timedelta(days = 365)
        semester = Semester.objects.create(name = 'Old',
                                           year = last_year.year,
                                           start = last_year,
                                           end = (last_year + datetime.timedelta(days = 30)),
        )

        degree = Degree.objects.create(name = 'Bachelor or Science', abbreviation = 'B.S.')
        user_degree = UserDegree.objects.create(user = self.user,
                                                degree = degree,
                                                graduation = semester,
        )

        self.assertEquals(profile.is_alum, True)
        
    
    def test_edit_preferences(self):
        response = self.c.get(reverse('profiles:preference_edit', kwargs={'username':self.user.username}))
        self.assertEquals(response.status_code, 200)


        response = self.c.post(reverse('profiles:preference_edit', kwargs={'username':self.user.username}),
                               {'email_alerts':'1',})

        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.user.profile.preferences['email_alerts'], True)