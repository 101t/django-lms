from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings

from django_extensions.db.models import TimeStampedModel
from tinymce import models as tinymce_models

from profiles.models import Profile

ALERT_LEVELS = (
    ('info','Information'),
    ('','Warning'),
    ('success','Success'),
    ('error','Error'),
    ('danger','Danger'),
    )

class Alert(TimeStampedModel):
    # This is char because there are a wide variety that can send
    sent_by = models.CharField(max_length = 200)
    sent_to = models.ForeignKey(User)
    title = models.CharField(max_length = 200)
    details = tinymce_models.HTMLField(blank = True)
    level = models.CharField(max_length = 200, choices = ALERT_LEVELS, blank = True)
    sticky = models.BooleanField(default = False)

def email_alert(sender, instance, **kwargs):
    if instance.sent_to.profile.preferences.get('email_alerts', False):
        # TODO: Make this a task
        send_mail(instance.title, instance.details, settings.ALERTS_FROM,
                  [instance.sent_to.email], fail_silently=False)

models.signals.post_save.connect(email_alert, sender=Alert, dispatch_uid = 'email_alerts')


