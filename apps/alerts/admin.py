from django.conf.urls.defaults import url, patterns
from django.contrib import admin
from django.utils.encoding import force_unicode
from django.utils.functional import update_wrapper
from alerts.models import Alert
from alerts.forms import alert_form

class AlertAdmin(admin.ModelAdmin):
    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwds):
                kwds['admin'] = self   # Use a closure to pass this admin instance to our wizard
                return self.admin_site.admin_view(view)(*args, **kwds)
            return update_wrapper(wrapper, view)

        urlpatterns = patterns('',
            url(r'^add/$',
                wrap(alert_form),
                name='alert_add')
        )
        urlpatterns += super(AlertAdmin, self).get_urls()
        return urlpatterns

admin.site.register(Alert, AlertAdmin)
