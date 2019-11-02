from django.conf import settings
from django.db.models import Q
from libs.django_utils import render_to_response
from django.views.generic import ListView
from springboard.models import IntranetApplication
from django.contrib.auth.decorators import login_required
from alerts.models import Alert


class SpringBoard(ListView):

    context_object_name = "applications"
    template_name = "springboard/springboard.html"

    def get_queryset(self):
        # Check the groups the user is allowed to see

        return IntranetApplication.objects.filter(Q(groups__in = self.request.user.groups.all()) | Q(groups__isnull=True)).distinct()

    def get_context_data(self, **kwargs):
        # Temporary message for testing
        from django.contrib import messages

        # Call the base implementation first to get a context
        context = super(SpringBoard, self).get_context_data(**kwargs)

        # Get all the alerts for the user
        context['alerts'] = Alert.objects.filter(sent_to = self.request.user)
        
        return context
