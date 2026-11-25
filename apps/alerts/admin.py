from django import forms
from django.contrib import admin, messages
from django.contrib.auth.models import Group, User

from .models import Alert
from .tasks import send_alert

AUDIENCES = (("user", "A single user"), ("groups", "Members of groups"), ("all", "All active users"))


class AlertAddForm(forms.ModelForm):
	audience = forms.ChoiceField(choices=AUDIENCES, initial="user", widget=forms.RadioSelect)
	groups = forms.ModelMultipleChoiceField(Group.objects.all(), required=False)

	class Meta:
		model = Alert
		fields = ("audience", "sent_to", "groups", "title", "details", "level", "sticky", "sent_by")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["sent_to"].required = False
		self.fields["sent_by"].required = False

	def clean(self):
		data = super().clean()
		audience = data.get("audience")
		if audience == "user":
			if not data.get("sent_to"):
				self.add_error("sent_to", "Choose a user.")
			self.recipients = [data.get("sent_to")]
		elif audience == "groups":
			self.recipients = list(User.objects.filter(groups__in=data.get("groups") or [], is_active=True).distinct())
		else:
			self.recipients = list(User.objects.filter(is_active=True))
		if not self.errors and not self.recipients:
			raise forms.ValidationError("That audience has no active users.")
		return data


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
	list_display = ("title", "sent_to", "level", "sticky", "created")
	list_filter = ("level", "sticky", "created")
	search_fields = ("title", "sent_to__username", "sent_to__email")
	raw_id_fields = ("sent_to",)

	def get_form(self, request, obj=None, **kwargs):
		if obj is None:
			kwargs["form"] = AlertAddForm
		return super().get_form(request, obj, **kwargs)

	def get_fields(self, request, obj=None):
		return AlertAddForm.Meta.fields if obj is None else super().get_fields(request, obj)

	def save_model(self, request, obj, form, change):
		if change:
			return super().save_model(request, obj, form, change)
		fields = {f: form.cleaned_data[f] for f in ("title", "details", "level", "sticky")}
		fields["sent_by"] = form.cleaned_data["sent_by"] or request.user.get_full_name() or request.user.username
		alerts = send_alert(form.recipients, **fields)
		obj.pk = alerts[0].pk  # the admin redirects to "the" new object; point it at the first one
		self.message_user(request, f"Alert sent to {len(alerts)} user(s).", messages.SUCCESS)
