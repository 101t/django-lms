from django.urls import path

from .views import record

app_name = "django_statsd"

urlpatterns = [
    path('record/', record, name='django_statsd.record'),
]
