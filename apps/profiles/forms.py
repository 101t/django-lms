from django import forms
from tinymce.widgets import TinyMCE

from .models import Profile


class ProfileForm(forms.ModelForm):
	first_name = forms.CharField(max_length=150, required=False)
	last_name = forms.CharField(max_length=150, required=False)
	email = forms.EmailField(required=False)
	biography = forms.CharField(widget=TinyMCE(), required=False)

	class Meta:
		model = Profile
		fields = ("first_name", "last_name", "email", "mugshot", "resume", "biography")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		user = self.instance.user
		self.initial.update(
			first_name=user.first_name, last_name=user.last_name, email=user.email, biography=self.instance.biography
		)

	def save(self, commit=True):
		user = self.instance.user
		for field in ("first_name", "last_name", "email"):
			setattr(user, field, self.cleaned_data[field])
		user.save()
		self.instance.data = {**(self.instance.data or {}), "biography": self.cleaned_data["biography"]}
		return super().save(commit)


class PreferenceForm(forms.Form):
	email_alerts = forms.BooleanField(label="Email new notifications and alerts to me", required=False)

	def save(self, profile):
		profile.preferences = {**(profile.preferences or {}), "email_alerts": self.cleaned_data["email_alerts"]}
		profile.save(update_fields=["preferences"])
