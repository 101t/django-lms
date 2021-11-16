from django.urls import path, include
from django.conf import settings
from django.contrib.auth.views import auth_login, logout_then_login
from libs.api import UserResource
from tastypie.api import Api
from django.conf.urls.static import static

api = Api(api_name='api')
api.register(UserResource())

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

# admin.autodiscover()

urlpatterns = [
	path('i18n/', include('django.conf.urls.i18n')),
	path('admin/', admin.site.urls),
	path('courses/', include('apps.courses.urls'), ),  # "courses"
	path('profiles/', include('apps.profiles.urls'), ),  # "profiles"
	path('alerts/', include('apps.alerts.urls'), ),  # "alerts"
	path('alerts/', include('apps.django_statsd.urls'), ),  # "django_statsd"
	path('tinymce/', include('tinymce.urls')),
	# path('api/', include(api.urls)),
	path('accounts/login/', auth_login, {'template_name': 'accounts/login.html'}, name="login"),
	path('accounts/logout/', logout_then_login, name="logout"),
	# url(r'', include('social_auth.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	path('', include('apps.springboard.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
	                                                                       document_root=settings.MEDIA_ROOT)  # noqa
