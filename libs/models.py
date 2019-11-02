from django.conf import settings

if settings.NONREL:
    # Yay monkey patching
    from permission_backend_nonrel.models import UserPermissionList, GroupPermissionList
    from django.contrib.auth.models import Group

    def get_groups(self):
        try:
            user_perm_list = UserPermissionList.objects.get(user = self)
        
            groups = Group.objects.filter(id__in = user_perm_list.group_fk_list)
        except UserPermissionList.DoesNotExist:
            groups = []
        
        return groups

    from django.contrib.auth.models import User

    User.add_to_class('group_list', property(get_groups))
