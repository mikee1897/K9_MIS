from django import forms
from django.forms import ModelForm, ValidationError, Form, widgets
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from datetime import date, datetime
from django.core.validators import validate_integer
from django.forms import fields

from deployment.models import Area, Location, Team_Assignment, Team_Dog_Deployed, Dog_Request, Incidents, Daily_Refresher, TempDeployment, Maritime
from planningandacquiring.models import K9
from profiles.models import Account, User
from django.contrib.sessions.models import Session

from django.contrib.gis import forms as geoforms

import datetime
import re
from six import string_types

from django.forms.widgets import Widget, Select
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe


class TransferRequestForm(forms.Form):
    ...

class TimeInput(forms.TimeInput):
    input_type = "time"

class DateInput(forms.DateInput):
    input_type = 'date'

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ('name',)


class LocationForm(forms.ModelForm):

    place = forms.CharField(widget = forms.Textarea(attrs={'rows':'3', 'style':'resize:none;'}))
    class Meta:
        model = Location
        fields = ('area', 'city', 'place')

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        self.fields['place'].widget.attrs['readonly'] = 'readonly'
        self.fields['place'].widget.attrs['placeholder'] = 'Please search for the location' 

class SelectLocationForm(forms.Form):
    location_list = []

    location = forms.ChoiceField(choices=location_list,
                                 widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):

        try:
            location_dict  = kwargs.pop("location_dict", None)
        except:
            pass

        super(SelectLocationForm, self).__init__(*args, **kwargs)
        if location_dict:
            self.fields['location'].choices = location_dict

class SelectUnitsForm(forms.Form):
    k9_list = []

    k9 = forms.ChoiceField(choices=k9_list,
                                 widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):

        try:
            k9_dict = kwargs.pop("k9_dict", None)
        except:
            pass

        try:
            check_true = kwargs.pop("check_true", None)
        except:
            pass

        super(SelectUnitsForm, self).__init__(*args, **kwargs)
        if k9_dict:
            self.fields['k9'].choices = k9_dict

        if check_true:
            self.fields['k9'].widget.attrs['checked'] = True

class ScheduleUnitsForm(forms.Form):
    schedule = forms.DateField(widget=DateInput())
    unit = forms.ModelChoiceField(TempDeployment.objects.all())

class AssignTeamForm(forms.ModelForm):
    location = forms.ModelChoiceField(queryset = Location.objects.filter(status='unassigned'))
    team_leader = forms.ModelChoiceField(queryset = User.objects.filter(position='Team Leader').filter(assigned=False))

    class Meta:
        model = Team_Assignment
        fields = ('location', 'team_leader', 'team', 'EDD_demand', 'NDD_demand', 'SAR_demand')
    
    def __init__(self, *args, **kwargs):
        super(AssignTeamForm, self).__init__(*args, **kwargs)
        self.fields['team_leader'].queryset = User.objects.filter(position='Team Leader').filter(assigned=False)

class EditTeamForm(forms.ModelForm):
    class Meta:
        model = Team_Assignment
        fields = ('team', 'EDD_demand', 'NDD_demand', 'SAR_demand')

class RequestForm(forms.ModelForm):
    remarks = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Dog_Request
        fields = ('requester', 'event_name', 'location', 'email_address', 'phone_number', 'area', 'city', 'k9s_needed', 'start_date', 'end_date', 'remarks')

        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput()
        }
    
    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        self.fields['location'].widget.attrs['readonly'] = 'readonly'
        self.fields['location'].widget.attrs['placeholder'] = 'Please search for the location' 
        self.fields['remarks'].required = False
        self.fields['phone_number'].required = False

    def validate_date(self):
        date_start = self.cleaned_data['start_date']
        date_end = self.cleaned_data['end_date']

        if date_start > date_end:
            raise forms.ValidationError("Start and End dates are invalid! (Start Date must be < the End Date)")

        if date_start < date.today():
            raise forms.ValidationError("Start Date must be a future date!")


    def clean_phone_number(self):
        cd = self.cleaned_data['phone_number']
        regex = re.compile('[^0-9]')
        # First parameter is the replacement, second parameter is your input string

        return regex.sub('', cd)


class IncidentForm(forms.ModelForm):
    location = forms.ModelChoiceField(queryset = Location.objects.none(), empty_label=None)
    class Meta:
        model = Incidents
        fields = '__all__'

        widgets = {
            'date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super(IncidentForm, self).__init__(*args, **kwargs)

        #self.fields['user'].intial = current_user

class DateForm(forms.Form):
    from_date = forms.DateField( widget=DateInput())
    to_date = forms.DateField(widget=DateInput())

        #self.fields['user'].intial = current_user

class DeploymentDateForm(forms.Form):
    deployment_date = forms.DateField( widget=DateInput())

    def __init__(self, *args, **kwargs):

        try:
            init_date = kwargs.pop("init_date", None)
        except:
            pass

        super(DeploymentDateForm, self).__init__(*args, **kwargs)
        self.fields['deployment_date'].required = True
        self.fields['deployment_date'].initial = init_date

class GeoSearch(forms.Form):
    search = forms.CharField()

class GeoForm(geoforms.Form):
    point = geoforms.PointField(widget= geoforms.OSMWidget(attrs={'default_lon' : 120.993173,'default_lat' : 14.564752,
                                                            'default_zoom': 18, 'display_raw': False, 'map_width': 470, 'map_height': 500}))
    # 'map_srid': 900913 Gmaps srid (geographic) current is projected
    # 120.993173 lon, 14.564752 lat,  DLSU default coordinates
    # 13468861.763567935675383 lon, 1639088.708640566794202 lat,  DLSU default coordinates
    # 13476918.53413876 lon, 1632299.5848436863 lat, PCGK9 Taguig Coordinates (2D Plane)

    def __init__(self, *args, **kwargs):

        try:
            lat  = kwargs.pop("lat", None)
            lng = kwargs.pop("lng", None)
        except:
            pass

        try:
            width = kwargs.pop("width", None)
        except:
            pass

        super(GeoForm, self).__init__(*args, **kwargs)
        if lat and lng:
            self.fields['point'].widget.attrs['default_lat'] = lat
            self.fields['point'].widget.attrs['default_lon'] = lng
        if width:
            self.fields['point'].widget.attrs['map_width'] = width


class MonthYearWidget(Widget):
    """
    A Widget that splits date input into two <select> boxes for month and year,
    with 'day' defaulting to the first of the month.

    Based on SelectDateWidget, in

    django/trunk/django/forms/extras/widgets.py


    """
    none_value = (0, '---')
    month_field = '%s_month'
    year_field = '%s_year'

    def __init__(self, attrs=None, years=None, required=True):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        self.required = required
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year, this_year+10)

    def render(self, name, value, attrs=None, renderer = None):
        try:
            year_val, month_val = value.year, value.month
        except AttributeError:
            year_val = month_val = None
            if isinstance(value, string_types):
                match = RE_DATE.match(value)
                if match:
                    year_val, month_val, day_val = [int(v) for v in match.groups()]

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        month_choices = list(MONTHS.items())
        if not (self.required and value):
            month_choices.append(self.none_value)
        month_choices.sort()
        local_attrs = self.build_attrs(base_attrs=self.attrs)
        s = Select(choices=month_choices)
        select_html = s.render(self.month_field % name, month_val, local_attrs)
        output.append(select_html)

        year_choices = [(i, i) for i in self.years]
        if not (self.required and value):
            year_choices.insert(0, self.none_value)
        local_attrs['id'] = self.year_field % id_
        s = Select(choices=year_choices)
        select_html = s.render(self.year_field % name, year_val, local_attrs)
        output.append(select_html)

        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        if y == m == "0":
            return None
        if y and m:
            return '%s-%s-%s' % (y, m, 1)
        return data.get(name, None)

class MonthYearForm(forms.Form):

    date = forms.DateField(
        required=False,
        widget=MonthYearWidget(years=range(2017,2041))
    )

class MaritimeForm(forms.ModelForm):

    class Meta:
        model = Maritime
        # fields = '__all__'
        exclude = ('location', )

    def __init__(self, *args, **kwargs):
        super(MaritimeForm, self).__init__(*args, **kwargs)
        self.fields["date"].widget = DateInput()
        self.fields["time"].widget = TimeInput()

class DailyRefresherForm(forms.ModelForm):

    class Meta:
        model = Daily_Refresher
        fields = '__all__'

        widgets = {
            # 'port_time': forms.TimeInput(format='%M:%S'),
            # 'building_time': forms.TimeInput(format='%M:%S'),
            # 'vehicle_time': forms.TimeInput(format='%M:%S'),
            # 'baggage_time': forms.TimeInput(format='%M:%S'),
            # 'others_time': forms.TimeInput(format='%M:%S'),
            'mar': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super(DailyRefresherForm, self).__init__(*args, **kwargs)
        self.fields['rating'].required = False
        self.fields['mar'].required = False
        self.fields['on_leash'].required = False
        self.fields['off_leash'].required = False
        self.fields['obstacle_course'].required = False
        self.fields['panelling'].required = False
        self.fields['k9'].required = False
        self.fields['handler'].required = False
        self.fields["port_time"].widget = TimeInput()
        self.fields["building_time"].widget = TimeInput()
        self.fields["vehicle_time"].widget = TimeInput()
        self.fields["baggage_time"].widget = TimeInput()
        self.fields["others_time"].widget = TimeInput()