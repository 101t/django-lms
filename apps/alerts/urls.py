from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import AlertList, acknowledge

app_name = "alerts"

urlpatterns = [
	path("", login_required(AlertList.as_view()), name="list"),
	path("<int:pk>/acknowledge/", acknowledge, name="acknowledge"),
]
