from django.conf.urls.defaults import *
from profiles.views import (ProfileEdit,
                            ProfileDetail,
                            PreferenceEdit,
)
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('profiles.views',
                       url('^(?P<username>[-\w]+)/edit/$', login_required(ProfileEdit.as_view()), name = 'edit'),
                       url('^(?P<username>[-\w]+)/edit/preferences/$', login_required(PreferenceEdit.as_view()), name = 'preference_edit'),

                       url('^(?P<username>[-\w]+)/$', login_required(ProfileDetail.as_view()), name = 'detail'),
                       )
