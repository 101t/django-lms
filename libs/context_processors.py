from django.conf import settings as django_settings
from django.utils.functional import lazy
from django.contrib.auth.models import Group

def settings(request):
    return {'TYPEKIT_URL':django_settings.TYPEKIT_URL}

def user_groups(request):
    if not request.user.is_authenticated:
        return {}

    def get_groups():
        if request.user.is_superuser:
            return [group.name for group in Group.objects.all()]
            
        groups = [group.name for group in request.user.groups.all()]
        return groups
    
    return {'groups': lazy(get_groups, list)}