from django import forms
from django.forms import fields, models, widgets
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.formtools.wizard import FormWizard
from django.utils.encoding import force_unicode
from alerts.tasks import alert_groups, alert_userlist
from alerts.models import Alert

ALERT_CHOICES = (
    ('all', 'All'),
    ('user', 'User'),
    ('group', 'Group')
    )

class AlertForm1(forms.ModelForm):
    class Meta:
        exclude = ('sent_to',)
        model = Alert

class AlertForm2(forms.Form):
    send_to = forms.ChoiceField(widget = forms.RadioSelect, choices = ALERT_CHOICES)

class UserForm(forms.Form):
    # TODO setup a filter select 
    sent_to = forms.ModelChoiceField(queryset = User.objects.all())

class GroupForm(forms.Form):
    # TODO setup a filter select 
    sent_to = forms.ModelChoiceField(queryset = Group.objects.all())


class AlertCreationWizard(FormWizard):
    """
    FormWizard
    """
    @property
    def __name__(self):
        # Python instances don't define __name__ (though functions and classes do).
        # We need to define this, otherwise the call to "update_wrapper" fails:
        return self.__class__.__name__

    def process_step(self, request, form, step):
        if step == 1:
            if form.cleaned_data['send_to'] == 'user':
                self.form_list.pop()
                self.form_list.append(UserForm)
            if form.cleaned_data['send_to'] == 'group':
                self.form_list.pop()
                self.form_list.append(GroupForm)
            if form.cleaned_data['send_to'] == 'all':
                self.form_list.pop()



    def get_template(self, step):
        # Optional: return the template used in rendering this wizard:
        return 'admin/alert_form.html'

    def parse_params(self, request, admin=None, *args, **kwargs):
        # Save the ModelAdmin instance so it's available to other methods:
        self._model_admin = admin
        # The following context variables are expected by the admin
        # "change_form.html" template; Setting them enables stuff like
        # the breadcrumbs to "just work":
        opts = admin.model._meta
        self.extra_context.update({
            'title': 'Add %s' % force_unicode(opts.verbose_name),
            # See http://docs.djangoproject.com/en/dev/ref/contrib/admin/#adding-views-to-admin-sites
            # for why we define this variable.
            'current_app': admin.admin_site.name,
            'has_change_permission': admin.has_change_permission(request),
            'add': True,
            'opts': opts,
            'root_path': admin.admin_site.root_path,
            'app_label': opts.app_label,
        })

    def render_template(self, request, form, previous_fields, step, context=None):
        from django.contrib.admin.helpers import AdminForm
        # Wrap this form in an AdminForm so we get the fieldset stuff:
        form = AdminForm(form, [(
            'Step %d of %d' % (step + 1, self.num_steps()),
            {'fields': form.base_fields.keys()}
            )], {})
        context = context or {}
        context.update({
            'media': self._model_admin.media + form.media
        })
        return super(AlertCreationWizard, self).render_template(request, form, previous_fields, step, context)

    def done(self, request, form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)

        # Send alert

        alert = Alert(sent_by = data['sent_by'],
                      title = data['title'],
                      details = data['details'],
                      level = data['level'],
            )

        if data['send_to'] == 'all':
            alert_userlist(alert, User.objects.all())

        if data['send_to'] == 'group':
            alert_groups(alert, data['sent_to'])

        if data['send_to'] == 'user':
            alert.sent_to = data['sent_to']
            alert.save()

        
        # Display success message and redirect to changelist:
        return self._model_admin.response_add(request, alert)

alert_form = AlertCreationWizard([AlertForm1, AlertForm2, UserForm])
