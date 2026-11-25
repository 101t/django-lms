from django.contrib import admin

from .models import IntranetApplication


@admin.register(IntranetApplication)
class IntranetApplicationAdmin(admin.ModelAdmin):
	list_display = ("title", "url", "icon_name", "order")
	list_editable = ("order",)
	filter_horizontal = ("groups",)
