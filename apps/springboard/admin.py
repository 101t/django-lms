from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.admin.widgets import FilteredSelectMultiple
from springboard.models import IntranetApplication

class IntranetApplicationAdminForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(queryset = Group.objects.all(),
                                            required = False,
                                            widget = FilteredSelectMultiple("Groups", False))

    def __init__(self, *args, **kwargs):
        super(IntranetApplicationAdminForm, self).__init__(*args, **kwargs)

        try:
            self.fields['groups'].initial = self.instance.groups.all()
        except ValueError:
            self.fields['groups'].initial = list()


    class Meta:
        model = IntranetApplication
        exclude = ('groups',)

class IntranetApplicationAdmin(admin.ModelAdmin):
    form = IntranetApplicationAdminForm

    def save_model(self, request, obj, form, change):
        super(IntranetApplicationAdmin, self).save_model(request, obj, form, change)
        try:
            if len(form.cleaned_data["groups"]) > 0:
                obj.groups = list(form.cleaned_data["groups"])
                obj.save()
        except KeyError:
            pass

    

admin.site.register(IntranetApplication, IntranetApplicationAdmin)
