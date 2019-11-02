from django.conf import settings
from django.contrib.auth.models import User, check_password
import ldap

'''
LDAP backend. You will need to set the below in your settings. (These are just examples
and WILL need to be changed!)

AUTH_LDAP_SERVER = "Your LDAP Server"
AUTH_LDAP_BASE_USER = "cn=Your, o=BaseUser"
AUTH_LDAP_BASE_PASS = "Your Base Password"
AUTH_LDAP_BASE = "dc=edu"
AUTH_LDAP_FILTER = "(&(objectclass=zimbraAccount) (cn=%s))"
AUTH_LDAP_BIND = "uid=%s, ou=people, dc=subdomain, dc=subdomain, dc=subdomain, dc=edu"
'''

class ZimbraLDAPBackend:
    def authenticate(self, username=None, password=None):
        print "ldap auth"
        scope = ldap.SCOPE_SUBTREE
        ret = ['cn', 'givenName', 'sn', 'mail', 'uid']

        # Authenticate the base user so we can search
        try:
            l = ldap.open(settings.AUTH_LDAP_SERVER)
            l.protocol_version = ldap.VERSION3
            l.simple_bind_s(settings.AUTH_LDAP_BASE_USER,settings.AUTH_LDAP_BASE_PASS)
        except ldap.LDAPError:
            print "No Bind"
            return None

        try:
            result_id = l.search(settings.AUTH_LDAP_BASE, scope, settings.AUTH_LDAP_FILTER.replace('%s', username), ret)
            result_type, result_data = l.result(result_id, 0)
            # If the user does not exist in LDAP, Fail.
            if (len(result_data) == 0):
                print "No Data Returned"
                return None

            result = result_data[0][1]
            
            # Attempt to bind to the user's DN
      
            
            l.simple_bind_s(settings.AUTH_LDAP_BIND.replace('%s', result['uid'][0]) , password)

            # The user existed and authenticated. Get the user
            # record or create one with no privileges.
            try:
                user = User.objects.get(username__exact=username)
            except:
                if not getattr(settings, 'LDAP_CREATE_USERS', True):
                    print "No User"
                    return None
                
                # Theoretical backdoor could be input right here. We don't
                # want that, so input an unused random password here.
                # The reason this is a backdoor is because we create a
                # User object for LDAP users so we can get permissions,
                # however we -don't- want them able to login without
                # going through LDAP with this user. So we effectively
                # disable their non-LDAP login ability by setting it to a
                # random password that is not given to them. In this way,
                # static users that don't go through ldap can still login
                # properly, and LDAP users still have a User object.
                from random import choice
                import string
                temp_pass = ""
                for i in range(8):
                    temp_pass = temp_pass + choice(string.letters)
                user = User.objects.create_user(username, result['mail'][0] ,temp_pass)
                user.first_name = result['givenName'][0]
                user.last_name = result['sn'][0]
                user.is_staff = False
                user.save()
            # Success.
            print "success"
            return user
           
        except ldap.INVALID_CREDENTIALS:
            print "Bad Credentials"
            # Name or password were bad. Fail.
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
