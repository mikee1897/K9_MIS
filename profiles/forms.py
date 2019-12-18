from django import forms
from django.forms import ModelForm, ValidationError, Form, widgets
from django.contrib.admin.widgets import AdminDateWidget
from datetime import date, datetime
from .models import User, Personal_Info, Education, Account
from deployment.models import Location
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as Auth_User

class DateInput(forms.DateInput):
    input_type = 'date'

class add_User_form(forms.ModelForm):
    class Meta:
        model = User
        fields = ('image','firstname', 'lastname', 'nickname', 'position', 'rank', 'extensionname', 'middlename',
                  'gender', 'birthdate', 'birthplace', 'civilstatus', 'citizenship', 'religion', 'bloodtype',
                  'distinct_feature', 'haircolor', 'eyecolor', 'skincolor', 'height', 'weight',
                  'headsize', 'footsize', 'bodybuild')
        widgets = {
            'birthdate': DateInput()
        }

        def __init__(self, *args, **kwargs):
            super(add_User_form, self).__init__(*args, **kwargs)
            self.fields['extensionname'].required = False
            self.fields['distinct_feature'].required = False
            self.fields['image'].required = False

class add_personal_form(forms.ModelForm):
    class Meta:
        model = Personal_Info
        fields = ('mobile_number', 'tel_number', 'street',
                  'barangay', 'city', 'province', 'mother_name', 'mother_birthdate',
                  'father_name', 'father_birthdate', 'tin', 'philhealth')
        widgets = {
            'father_birthdate': DateInput(),
            'mother_birthdate': DateInput()
        }

class add_education_form(forms.ModelForm):
    class Meta:
        model = Education
        fields = ('primary_education', 'secondary_education', 'tertiary_education', 'pe_schoolyear', 'se_schoolyear',
                  'te_schoolyear', 'pe_degree', 'se_degree', 'te_degree')

class add_user_account_form(forms.ModelForm):
   
    class Meta:
        model = Account
        fields = ('email_address', 'password')

        widgets = {
            'password': forms.PasswordInput(),
        }

        #model = Auth_User
        #fields = ('email', 'password1')

class DateForm(forms.Form):
    from_date = forms.DateField(widget=DateInput())
    to_date = forms.DateField(widget=DateInput())


class CheckArrivalForm(forms.Form):
    team_member_list = []

    team_member = forms.MultipleChoiceField(choices=team_member_list,
                                    widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):

        try:
            for_arrival = kwargs.pop("for_arrival", None)
        except:
            pass

        super(CheckArrivalForm, self).__init__(*args, **kwargs)
        if for_arrival:
            for_arrival_list = []
            for item in for_arrival:
                account = Account.objects.get(UserID = item.handler.id)
                for_arrival_list.append((item.handler.id , str(item.handler) + " - " + str(item.handler.rank) + " - " + str(account.serial_number)))

            print(for_arrival_list)

            self.fields['team_member'].choices = for_arrival_list






