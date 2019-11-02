from tastypie.resources import ModelResource
from django.contrib.auth.models import User
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        excludes = ['password',]
