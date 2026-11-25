from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import PreferenceEdit, ProfileDetail, ProfileEdit

app_name = "profiles"

urlpatterns = [
	path("<str:username>/edit/", login_required(ProfileEdit.as_view()), name="edit"),
	path("<str:username>/edit/preferences/", login_required(PreferenceEdit.as_view()), name="preference_edit"),
	path("<str:username>/", login_required(ProfileDetail.as_view()), name="detail"),
]
