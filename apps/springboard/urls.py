from django.urls import path
from .views import SpringBoard
from django.contrib.auth.decorators import login_required

urlpatterns = [
	path('', login_required(SpringBoard.as_view()), name='springboard'),
]
