from django.conf.urls.defaults import *
from django.conf import settings
from libs.api import UserResource
from tastypie.api import Api
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

api = Api(api_name='api')
api.register(UserResource())

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', include('apps.springboard.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^courses/', include('apps.courses.urls', namespace="courses", app_name="courses")),
    (r'^profiles/', include('apps.profiles.urls', namespace="profiles", app_name="profiles")),
    (r'^alerts/', include('apps.alerts.urls', namespace="alerts", app_name="alerts")),
    (r'^tinymce/', include('tinymce.urls')),
    (r'^', include(api.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}, name="login"),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name="logout"),
    url(r'', include('social_auth.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

)

#If we're using zimbra


if settings.DEBUG:
    urlpatterns += patterns('',
                            (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                             {'document_root': settings.MEDIA_ROOT,
                              'show_indexes': True}),
    )
    urlpatterns += staticfiles_urlpatterns()

