from django.contrib import admin

from .models import Degree, Profile, Service, ServiceType, UserDegree


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("__str__", "user")
	search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")
	raw_id_fields = ("user",)


admin.site.register(Degree)
admin.site.register(UserDegree)
admin.site.register(ServiceType)
admin.site.register(Service)
