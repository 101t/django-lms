from django.views.generic import ListView
from django.shortcuts import redirect

from apps.alerts.models import Alert


class AlertList(ListView):
	context_object_name = "alerts"
	template_name = "alerts/list.html"

	def get_queryset(self):
		return Alert.objects.filter(sent_to=self.request.user)


def acknowledge(request):
	if request.method == 'POST':
		pk = request.POST['pk']
		obj = Alert.objects.get(pk=pk)
		obj.delete()
	return redirect('/')
