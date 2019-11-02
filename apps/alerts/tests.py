from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group

import libs.test_utils as test_utils
from alerts.models import Alert
from alerts.tasks import alert_userlist, alert_groups

if settings.NONREL:
    from permission_backend_nonrel.utils import update_user_groups

class AlertTest(test_utils.AuthenticatedTest):
    def test_acknowlege(self):
        """
        Tests the user acknowledgeing and deleteing an alert
        """

        # Create the alert
        alert = Alert.objects.create(sent_by = 'Tester',
                                     sent_to = self.user,
                                     title = 'Test title',
                                     details = 'No details',
                                     level = 'Notice',)
        
        self.c.post(reverse('alerts:acknowledge'), {'pk':alert.id})

        with self.assertRaises(Alert.DoesNotExist):
            Alert.objects.get(id = alert.id)
        
    def test_alert_all(self):
        """
        Tests the ability of the system to alert all users
        """

        # Create a load of users
        for i in range(0, 100):
            User.objects.create(username = 'user_%s' %(i))

        users = User.objects.all()

        # Create the alert
        alert = Alert(sent_by = 'Tester',
                      title = 'Test title',
                      details = 'No details',
                      level = 'Notice',)

        alert_userlist(alert, users)

        self.assertEquals(len(Alert.objects.all()), len(User.objects.all()))
        

    def test_alert_group(self):
        """
        Tests the ability of the system to alert a group of users
        """

        # Create groups
        group = Group.objects.create(name = 'test1')

        # Create a load of users
        for i in range(50):
            user = User.objects.create(username = 'user_%s' %(i))
            if settings.NONREL:
                update_user_groups(user, [group])
            else:
                group.user_set.add(user)
                
        for i in range(50, 100):
            user = User.objects.create(username = 'user_%s' %(i))


        alert = Alert(sent_by = 'Tester',
                      title = 'Test title',
                      details = 'No details',
                      level = 'Notice',)

        alert_groups(alert, group)

        self.assertEquals(len(Alert.objects.all()), 50)


    def test_alert_groups(self):
        """
        Tests the ability of the system to alert groups of users
        """

        # Create groups
        group1 = Group.objects.create(name = 'test1')
        group2 = Group.objects.create(name = 'test2')
        
        # Create a load of users
        for i in range(25):
            user = User.objects.create(username = 'user_%s' %(i))
            if settings.NONREL:
                update_user_groups(user, [group1])
            else:
                group1.user_set.add(user)

        for i in range(25, 50):
            user = User.objects.create(username = 'user_%s' %(i))
            
            if settings.NONREL:
                update_user_groups(user, [group2])
            else:
                group2.user_set.add(user)


        for i in range(50, 100):
            user = User.objects.create(username = 'user_%s' %(i))


        alert = Alert(sent_by = 'Tester',
                      title = 'Test title',
                      details = 'No details',
                      level = 'Notice',)

        alert_groups(alert, [group1, group2])
        
        self.assertEquals(len(Alert.objects.all()), 50)

    def test_alert_email(self):
        """
        Tests the ability of the system to send alert emails
        """
        from django.core import mail
        from profiles.models import Profile
        
        self.user.profile.preferences['email_alerts'] = True
        self.user.profile.save()

        self.assertEquals(len(mail.outbox), 0)
        
        alert = Alert.objects.create(sent_by = 'Tester',
                                     title = 'Test title',
                                     details = 'No details',
                                     level = 'Notice',
                                     sent_to = self.user,
                                 )
        
        self.assertEquals(len(mail.outbox), 1)


