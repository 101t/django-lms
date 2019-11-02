from django.utils import unittest
import sys
import os

from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.files import File

from springboard.models import IntranetApplication
from alerts.models import Alert

import libs.test_utils as test_utils

class SpringboardTest(test_utils.AuthenticatedTest):
    def test_display_code(self):
        response = self.c.get(reverse('springboard'))
        self.failUnlessEqual(response.status_code, 200)
        
    def test_display_icon(self):
        here = os.path.dirname( os.path.abspath(__file__) )
        f = open(here + '/test_files/test_icon.png')
        application = IntranetApplication(url = '/test', title='Test')
        application.save()
        application.icon.save('test_icon.png', File(f))
        
        response = self.c.get(reverse('springboard'))
        self.assertContains(response, 'Test')


    def test_alerts(self):
        alert = Alert.objects.create(sent_by = 'Test',
                                     sent_to = self.user,
                                     title = 'Test alert',
                                     details = 'Stuff, stuff, stuff',
            )

        response = self.c.get(reverse('springboard'))

        assert(alert in response.context['alerts'])

    def test_defaults(self):
        response = self.c.get(reverse('springboard'))

        self.assertContains(response, "Admin")
        self.assertContains(response, "Courses")
