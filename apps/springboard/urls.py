from django.conf.urls.defaults import *
from springboard.views import SpringBoard
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('springboard.views',
                       url('', login_required(SpringBoard.as_view()), name = 'springboard'),
                       )
