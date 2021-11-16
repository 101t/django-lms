from django.urls import re_path as url
from django.contrib.auth.decorators import login_required

from .views import AlertList, acknowledge

urlpatterns = [
	url('^$', login_required(AlertList.as_view()), name='list'),
	url('^acknowledge/$', acknowledge, name='acknowledge'),
]
