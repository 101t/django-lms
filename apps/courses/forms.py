from django import forms
from django.contrib.auth.models import User

from .models import Assignment, AssignmentSubmission, Course, Resource


class CourseAdminForm(forms.ModelForm):
	private = forms.TypedChoiceField(
		label="Visibility",
		choices=((False, "Public — anyone signed in can view"), (True, "Private — only participants")),
		coerce=lambda value: value in (True, "True"),
		widget=forms.RadioSelect,
	)

	class Meta:
		model = Course
		fields = ("private",)


class AssignmentForm(forms.ModelForm):
	class Meta:
		model = Assignment
		fields = ("title", "description", "due_date")
		widgets = {"due_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}


class SubmitAssignmentForm(forms.ModelForm):
	class Meta:
		model = AssignmentSubmission
		fields = ("link", "file", "notes")

	def clean(self):
		data = super().clean()
		if not data.get("link") and not data.get("file"):
			raise forms.ValidationError("Add a link or upload a file.")
		return data


class TeamSubmitAssignmentForm(SubmitAssignmentForm):
	users = forms.ModelMultipleChoiceField(queryset=User.objects.none(), required=False, label="Team members")

	class Meta(SubmitAssignmentForm.Meta):
		fields = ("users", "link", "file", "notes")


class ResourceForm(forms.ModelForm):
	class Meta:
		model = Resource
		fields = ("title", "description", "link", "file")
