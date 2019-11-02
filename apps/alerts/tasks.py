from django.conf import settings
from django.contrib.auth.models import User

if settings.NONREL:
    from permission_backend_nonrel.models import UserPermissionList

from celery.task import task

@task()
def alert_userlist(alert, userlist):
    """
    This takes a mostly complete alert (minus the sent_to) and applies it to all the users in the list
    """

    for user in userlist:
        # Set the id to None to create a new alert
        alert.id = None
        alert.sent_to = user
        alert.save()

def alert_groups(alert, groups):
    """
    Takes a group or list of groups and send the alert to them
    """
    
    # TODO find a better way to see if groups is iterable and not a string
    if not getattr(groups, '__iter__', False):
        groups = [groups]

    for group in groups:
        if settings.NONREL:
            userperm_list = UserPermissionList.objects.filter(group_fk_list = group.id)
            alert_userlist(alert, [u.user for u in userperm_list])
        else:
            users = User.objects.filter(groups = group)
            alert_userlist(alert, users)

