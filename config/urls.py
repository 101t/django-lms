from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.urls import include, path


def health(request):
	return JsonResponse({"status": "ok"})


admin.site.site_header = admin.site.site_title = settings.SITE_NAME

urlpatterns = [
	path("health/", health, name="health"),
	path("admin/", admin.site.urls),
	path("accounts/login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
	path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
	path("accounts/", include("django.contrib.auth.urls")),
	path("api/", include("apps.api.urls")),
	path("courses/", include("apps.courses.urls")),
	path("profiles/", include("apps.profiles.urls")),
	path("alerts/", include("apps.alerts.urls")),
	path("tinymce/", include("tinymce.urls")),
	path("", include("apps.springboard.urls")),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
