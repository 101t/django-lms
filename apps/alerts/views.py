from django.views.generic import ListView
from django.views.generic.create_update import delete_object


from alerts.models import Alert

class AlertList(ListView):
    context_object_name = "alerts"
    template_name = "alerts/list.html"

    def get_queryset(self):
        return Alert.objects.filter(sent_to = self.request.user)

def acknowledge(request):
    if request.method == 'POST':
        pk = request.POST['pk']
    else:
        pk = '0'
        
    return delete_object(request, Alert, '/', object_id = pk)
    
