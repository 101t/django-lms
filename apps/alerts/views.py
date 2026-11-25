from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from .models import Alert


class AlertList(ListView):
	context_object_name = "alerts"
	template_name = "alerts/list.html"
	paginate_by = 25

	def get_queryset(self):
		return Alert.objects.filter(sent_to=self.request.user)


@login_required
@require_POST
def acknowledge(request, pk):
	get_object_or_404(Alert, pk=pk, sent_to=request.user, sticky=False).delete()
	next_url = request.POST.get("next", "/")
	if not url_has_allowed_host_and_scheme(next_url, {request.get_host()}, request.is_secure()):
		next_url = "/"
	return redirect(next_url)
