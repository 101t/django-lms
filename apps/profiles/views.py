from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, FormView, UpdateView

from apps.courses.models import Course

from .forms import PreferenceForm, ProfileForm
from .models import Profile


class ProfileEdit(UpdateView):
	"""Always edits the signed-in user's own profile, whatever username is in the URL."""

	form_class = ProfileForm
	template_name = "profiles/edit.html"

	def get_object(self, queryset=None):
		return self.request.user.profile

	def form_valid(self, form):
		messages.success(self.request, "Profile updated.")
		return super().form_valid(form)


class ProfileDetail(DetailView):
	template_name = "profiles/detail.html"
	context_object_name = "profile"

	def get_object(self, queryset=None):
		return get_object_or_404(Profile.objects.select_related("user"), user__username=self.kwargs["username"])

	def get_context_data(self, **kwargs):
		user = self.object.user
		courses = Course.objects.visible_to(self.request.user).select_related("semester")
		return super().get_context_data(
			teaching=courses.filter(Q(faculty=user) | Q(teaching_assistants=user)).distinct(),
			enrolled=courses.filter(members=user),
			degrees=user.userdegree_set.select_related("degree", "graduation"),
			**kwargs,
		)


class PreferenceEdit(FormView):
	form_class = PreferenceForm
	template_name = "profiles/edit_preferences.html"

	def get_initial(self):
		return {"email_alerts": (self.request.user.profile.preferences or {}).get("email_alerts", False)}

	def form_valid(self, form):
		form.save(self.request.user.profile)
		messages.success(self.request, "Preferences saved.")
		return super().form_valid(form)

	def get_success_url(self):
		return self.request.user.profile.get_absolute_url()
