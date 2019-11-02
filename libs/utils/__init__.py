import datetime
from django import forms
from django.utils.hashcompat import sha_constructor
from django.conf import settings

class DateDropdownWidget(forms.MultiWidget):
    def __init__(self,attrs=None,year_range=None,month_range=None,day_range=None):
        YEARS = year_range or range(2000,2021)
        MONTHES = month_range or range(1,13)
        DAYS = day_range or range(1,32)

        years = map( lambda x: (x,x), YEARS )
        months = map(lambda x:(x,x), MONTHES )
        days = map( lambda x: (x,x), DAYS )

        widgets = (
                forms.Select(choices=years),
                forms.Select(choices=months),
                forms.Select(choices=days),
                )
        super(DateDropdownWidget, self).__init__(widgets, attrs)
    
    def format_output(self,widgets):
        format = "Year %s&nbsp;Month %s&nbsp;Day %s".decode('utf-8')
        return format%(widgets[0],widgets[1],widgets[2])

    def decompress(self,value):
        if value:
            return [value.year, value.month,value.day]
        return [None,None,None]

class DateField(forms.MultiValueField):
    widget = DateDropdownWidget
    def __init__(self,*args,**kwargs):
        fields = (
                forms.IntegerField( required=True),
                forms.IntegerField( required=True),
                forms.IntegerField( required=True ),
                )
        super(DateField, self).__init__(fields, *args,**kwargs )

    def compress(self,data_list):
        EMPTY_VALUES = [None, '']
        ERROR_EMPTY = "Fill the fields."
        ERROR_INVALID = "Enter a valid date."
        if data_list:
            if filter(lambda x: x in EMPTY_VALUES, data_list):
                raise forms.ValidationError(ERROR_EMPTY)
            
            try:
                return datetime.datetime(*map(lambda x:int(x),data_list))
            except ValueError:
                raise forms.ValidationError(ERROR_INVALID)
        return None
class MonthYearDropdownWidget(forms.MultiWidget):
    def __init__(self,attrs=None,year_range=None,month_range=None):
        YEARS = year_range or range(2000,2021)
        MONTHES = month_range or range(1,13)

        years = map( lambda x: (x,x), YEARS )
        months = map(lambda x:(x,x), MONTHES )

        widgets = (
                forms.Select(choices=years),
                forms.Select(choices=months),
                )
        super(MonthYearDropdownWidget, self).__init__(widgets, attrs)
    
    def format_output(self,widgets):
        format = "Year %s&nbsp;Month %s".decode('utf-8')
        return format%(widgets[0],widgets[1])

    def decompress(self,value):
        if value:
            return [value.year, value.month]
        return [None,None,None]

class MonthYearField(forms.MultiValueField):
    widget = MonthYearDropdownWidget
    def __init__(self,*args,**kwargs):
        fields = (
                forms.IntegerField( required=True),
                forms.IntegerField( required=True),
                )
        super(MonthYearField, self).__init__(fields, *args,**kwargs )

    def compress(self,data_list):
        EMPTY_VALUES = [None, '']
        ERROR_EMPTY = "Fill the fields."
        ERROR_INVALID = "Enter a valid date."
        if data_list:
            if filter(lambda x: x in EMPTY_VALUES, data_list):
                raise forms.ValidationError(ERROR_EMPTY)
            try:
                data_list.append(1)
                return datetime.datetime(*map(lambda x:int(x),data_list))
            except ValueError:
                raise forms.ValidationError(ERROR_INVALID)
        return None


def make_token(user, email):
        hash = sha_constructor(settings.SECRET_KEY + unicode(user.id) +
                               user.password + user.last_login.strftime('%Y-%m-%d %H:%M:%S') +
                               unicode(email)).hexdigest()[::2]
        return "%s" % (hash)


def short_time(t):
    t = t.strftime('%I:%M%p')
    if t[0] == '0':
        t = t[1:]
    return t.replace(':00', '').replace('M','').lower()
