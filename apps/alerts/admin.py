from django.urls import re_path as url
from django.contrib import admin
# from functools import update_wrapper
from .models import Alert
from .forms import AlertCreationWizard


class AlertAdmin(admin.ModelAdmin):
	def get_urls(self):
		# def wrap(view):
		#     def wrapper(*args, **kwds):
		#         kwds['admin'] = self   # Use a closure to pass this admin instance to our wizard
		#         return self.admin_site.admin_view(view)(*args, **kwds)
		#     return update_wrapper(wrapper, view)

		urlpatterns = [
			url(r'^add/$', AlertCreationWizard.as_view(), name='alert_add'),
		]
		urlpatterns += super(AlertAdmin, self).get_urls()
		return urlpatterns


admin.site.register(Alert, AlertAdmin)
