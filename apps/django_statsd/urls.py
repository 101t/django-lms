from django.urls import path

from .views import record

urlpatterns = [
    path('record/', record, name='django_statsd.record'),
]
