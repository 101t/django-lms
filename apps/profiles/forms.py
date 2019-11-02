from django import forms

from tinymce.widgets import TinyMCE
from libs.widgets import ShortNameClearableFileInput

class ProfileForm(forms.Form):
    mugshot = forms.FileField(label = 'Profile image', required = False, widget=ShortNameClearableFileInput)
    resume = forms.FileField(label = 'Resume', required = False, widget=ShortNameClearableFileInput)
    biography = forms.CharField(widget=TinyMCE(attrs = {'cols': 150, 'rows': 30,}, mce_attrs = {'width': '561px'}))

    def save(self, profile):
        profile.mugshot = self.cleaned_data['mugshot']
        profile.resume = self.cleaned_data['resume']

        profile.data['biography'] = self.cleaned_data['biography']
        profile.save()

class PreferenceForm(forms.Form):
    email_alerts = forms.BooleanField(label = 'Email new notifications and alerts to me')

    def save(self, profile):
        profile.preferences['email_alerts'] = self.cleaned_data['email_alerts']
        profile.save()