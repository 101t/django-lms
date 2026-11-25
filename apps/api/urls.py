from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("semesters", views.SemesterViewSet)
router.register("courses", views.CourseViewSet, basename="course")
router.register("assignments", views.AssignmentViewSet, basename="assignment")
router.register("resources", views.ResourceViewSet, basename="resource")
router.register("alerts", views.AlertViewSet, basename="alert")

urlpatterns = [
	path("v1/", include(router.urls)),
	path("v1/me/", views.me, name="api-me"),
	path("schema/", SpectacularAPIView.as_view(), name="api-schema"),
	path("docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"),
]
