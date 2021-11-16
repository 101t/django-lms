from django.contrib import admin
from apps.profiles.models import Profile, Degree, UserDegree, Service

admin.site.register(Profile)
admin.site.register(Degree)
admin.site.register(UserDegree)
admin.site.register(Service)
