from django.urls import path, re_path
from apps.profiles.views import (
    ProfileEdit,
    ProfileDetail,
    PreferenceEdit,
)
from django.contrib.auth.decorators import login_required

app_name = "profiles"

urlpatterns = [
    re_path(r'^(?P<username>[-\w]+)/edit/$', login_required(ProfileEdit.as_view()), name='edit'),
    re_path(r'^(?P<username>[-\w]+)/edit/preferences/$', login_required(PreferenceEdit.as_view()),
            name='preference_edit'),
    re_path(r'^(?P<username>[-\w]+)/$', login_required(ProfileDetail.as_view()), name='detail'),
]
