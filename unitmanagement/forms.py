from django import forms
from django.forms import ModelForm, ValidationError, Form, widgets
from django.contrib.admin.widgets import AdminDateWidget
from datetime import date, datetime
from django.forms import formset_factory, inlineformset_factory, modelformset_factory
from django.contrib.sessions.models import Session

from deployment.models import Team_Assignment
from unitmanagement.models import PhysicalExam , Health, HealthMedicine, VaccinceRecord, Miscellaneous_Request, VaccineUsed, Food_Request, Medicine_Request, Request_Transfer, Replenishment_Request
from unitmanagement.models import K9_Incident, Handler_On_Leave, Handler_Incident, Emergency_Leave
from planningandacquiring.models import K9
from inventory.models import Medicine, Miscellaneous, Medicine_Inventory, Food
from profiles.models import Account, User
from django.db.models import Q

def user_in_session(request):
    serial = request.session['session_serial']
    account = Account.objects.get(serial_number=serial)
    user_in_session = User.objects.get(id=account.UserID.id)   
    return user_in_session.id

class DateInput(forms.DateInput):
    input_type = 'date'

class SelectUnitsForm(forms.Form):
    k9_list = []

    k9 = forms.ChoiceField(choices=k9_list,
                             widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):

        try:
            k9_dict  = kwargs.pop("k9_dict", None)
        except:
            pass

        try:
            check_true = kwargs.pop("check_true", None)
        except:
            pass

        try:
            disable_cb = kwargs.pop("disable_cb", None)
        except:
            pass

        super(SelectUnitsForm, self).__init__(*args, **kwargs)
        if k9_dict:
            self.fields['k9'].choices = k9_dict

        if check_true:
            self.fields['k9'].widget.attrs['checked'] = True

        if disable_cb:
            self.fields['k9'].widget.attrs['readonly'] = True

class PhysicalExamForm(forms.ModelForm):
    EXAMSTATUS = (
        ('Normal', 'Normal'),
        ('Abnormal', 'Abnormal'),
        ('Not Examined', 'Not Examined'),
    )
    #dog = forms.ModelChoiceField(queryset = K9.objects.all().order_by('name'))
    general_appearance = forms.CharField(label = 'general_appearance', widget = forms.Select(choices=EXAMSTATUS))
    integumentary = forms.CharField(label = 'integumentary', widget = forms.Select(choices=EXAMSTATUS))
    musculo_skeletal = forms.CharField(label = 'musculo_skeletal', widget = forms.Select(choices=EXAMSTATUS))
    respiratory = forms.CharField(label = 'respiratory', widget = forms.Select(choices=EXAMSTATUS))
    genito_urinary = forms.CharField(label = 'genito_urinary', widget = forms.Select(choices=EXAMSTATUS))
    nervous = forms.CharField(label = 'nervous', widget = forms.Select(choices=EXAMSTATUS))
    circulatory = forms.CharField(label = 'circulatory', widget = forms.Select(choices=EXAMSTATUS))
    digestive = forms.CharField(label = 'digestive', widget = forms.Select(choices=EXAMSTATUS))
    mucous_membrances = forms.CharField(label = 'mucous_membrances', widget = forms.Select(choices=EXAMSTATUS))
    lymph_nodes = forms.CharField(label = 'lymph_nodes', widget = forms.Select(choices=EXAMSTATUS))
    eyes = forms.CharField(label = 'eyes', widget = forms.Select(choices=EXAMSTATUS))
    ears = forms.CharField(label = 'ears', widget = forms.Select(choices=EXAMSTATUS))
    remarks = forms.CharField(label = 'remarks', widget = forms.Textarea(attrs={'rows':'4'}))
    cleared = forms.BooleanField(label = 'cleared', widget=forms.CheckboxInput)

    class Meta:
        model = PhysicalExam
        fields = ('dog', 'cage_number', 'general_appearance', 'integumentary',
        'musculo_skeletal', 'respiratory', 'genito_urinary', 'nervous', 'circulatory', 'digestive',
        'mucous_membrances', 'lymph_nodes', 'eyes', 'ears', 'remarks', 'date_next_exam',
        'heart_rate','respiratory_rate','temperature','weight', 'cleared')

    def __init__(self, *args, **kwargs):
        super(PhysicalExamForm, self).__init__(*args, **kwargs)
        self.fields['cage_number'].required = False
        self.fields['remarks'].required = False
        self.fields['date_next_exam'].required = False
        self.fields['cleared'].required = False
        # a = K9.objects.filter(id=request.session['phex_k9_id'])
        # self.fields['dog'].initial = a



class HealthForm(forms.ModelForm):
    CHOICE = (
        (True,'Yes'),
        (False,'No')
    )

    treatment = forms.CharField(widget = forms.Textarea(attrs={'rows':'4'}))
    problem = forms.CharField(widget = forms.Textarea(attrs={'rows':'4'}))
    follow_up =forms.ChoiceField(choices=CHOICE,widget=forms.RadioSelect)
    follow_up_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))

    
    class Meta:
        model = Health
        fields = ('dog','problem', 'treatment', 'incident_id', 'image', 'follow_up', 'follow_up_date')
        

    def __init__(self, *args, **kwargs):
        super(HealthForm, self).__init__(*args, **kwargs)
        self.fields['dog'].required = False
        self.fields['problem'].required = False
        self.fields['incident_id'].required = False
        self.fields['image'].required = False
        self.fields['follow_up_date'].required = False

class HealthMedicineForm(forms.ModelForm):
    TIME_OF_DAY = (
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Night', 'Night'),
        ('Morning/Afternoon', 'Morning/Afternoon'),
        ('Morning/Night', 'Morning/Night'),
        ('Afternoon/Night', 'Afternoon/Night'),
        ('Morning/Afternoon/Night', 'Morning/Afternoon/Night'),
    )

    class Meta:
        model = HealthMedicine
        fields = ('medicine', 'quantity', 'time_of_day', 'duration')

    medicine = forms.ModelChoiceField(queryset = Medicine_Inventory.objects.exclude(quantity=0).exclude(medicine__med_type='Vaccine'))
    time_of_day = forms.CharField(label = 'Time of Day', widget = forms.Select(choices=TIME_OF_DAY))
    duration = forms.IntegerField(label = 'Duration (Days)')

    def __init__(self, *args, **kwargs):
        super(HealthMedicineForm, self).__init__(*args, **kwargs)
        self.fields['medicine'].required = False

class VaccinationRecordForm(forms.ModelForm):

    class Meta:
        model = VaccinceRecord
        fields = ('deworming_1', 'deworming_2', 'deworming_3', 'dhppil_cv_1', 'heartworm_1', 'bordetella_1', 
        'tick_flea_1', 'dhppil_cv_2', 'deworming_4', 'heartworm_2', 'bordetella_2', 'anti_rabies', 'tick_flea_2',
        'dhppil_cv_3', 'heartworm_3', 'dhppil4_1', 'tick_flea_3', 'dhppil4_2', 'heartworm_4', 'tick_flea_4', 
        'heartworm_5', 'tick_flea_5', 'heartworm_6', 'tick_flea_6', 'heartworm_7', 'tick_flea_7', 'heartworm_8')

    def __init__(self, *args, **kwargs):
        super(VaccinationRecordForm, self).__init__(*args, **kwargs)
        self.fields['deworming_1'].required = False
        self.fields['deworming_2'].required = False
        self.fields['deworming_3'].required = False
        self.fields['dhppil_cv_1'].required = False
        self.fields['heartworm_1'].required = False
        self.fields['bordetella_1'].required = False
        self.fields['tick_flea_1'].required = False
        self.fields['dhppil_cv_2'].required = False
        self.fields['deworming_4'].required = False
        self.fields['heartworm_2'].required = False
        self.fields['bordetella_2'].required = False
        self.fields['anti_rabies'].required = False
        self.fields['tick_flea_2'].required = False
        self.fields['dhppil_cv_3'].required = False
        self.fields['heartworm_3'].required = False
        self.fields['tick_flea_3'].required = False
        self.fields['dhppil4_2'].required = False
        self.fields['heartworm_4'].required = False
        self.fields['tick_flea_4'].required = False
        self.fields['heartworm_5'].required = False
        self.fields['tick_flea_5'].required = False
        self.fields['heartworm_6'].required = False
        self.fields['tick_flea_6'].required = False
        self.fields['heartworm_7'].required = False
        self.fields['tick_flea_7'].required = False
        self.fields['heartworm_8'].required = False


class VaccinationUsedForm(forms.ModelForm):
    vaccine = forms.ModelChoiceField(queryset = Medicine_Inventory.objects.all(), label=None)
    date_vaccinated = forms.DateField(widget = DateInput(), label=None)
    image = forms.ImageField()

    class Meta:
        model = VaccineUsed
 
        fields=('age', 'disease', 'vaccine', 'date_vaccinated', 'image', 'veterinary', 'done')
    
    def __init__(self, *args, **kwargs):
        super(VaccinationUsedForm, self).__init__(*args, **kwargs)
        self.fields['age'].required = False
        self.fields['disease'].required = False
        self.fields['vaccine'].required = False
        self.fields['date_vaccinated'].required = False
        self.fields['image'].required = False
        self.fields['veterinary'].required = False
        self.fields['done'].required = False

class VaccinationYearlyForm(forms.ModelForm):
    vaccine = forms.ModelChoiceField(queryset = Medicine_Inventory.objects.all(), label=None)
    date_vaccinated = forms.DateField(widget = DateInput(), label=None)
    image = forms.ImageField()

    class Meta:
        model = VaccineUsed
 
        fields=('disease', 'vaccine', 'date_vaccinated', 'image', 'veterinary', 'done')
    
    def __init__(self, *args, **kwargs):
        super(VaccinationYearlyForm, self).__init__(*args, **kwargs)
        self.fields['disease'].required = False
        self.fields['vaccine'].required = False
        self.fields['date_vaccinated'].required = False
        self.fields['image'].required = False
        self.fields['veterinary'].required = False
        self.fields['done'].required = False

class RequestTransferForm(forms.ModelForm):
    class Meta:
        model = Request_Transfer
        fields = ('handler', 'date_of_transfer', 'location_from', 'location_to')

        widgets = {
            'date_of_transfer': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super(RequestTransferForm, self).__init__(*args, **kwargs)
        self.fields['handler'].widget.attrs['disabled'] = True
        self.fields['location_from'].widget.attrs['disabled'] = True
        self.fields['location_from'].required = False

class ChooseTeamForm(forms.Form):
    location_to = forms.ChoiceField(choices=[], widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        super(ChooseTeamForm, self).__init__(*args, **kwargs)
        team = Team_Assignment.objects.exclude(total_dogs_deployed__lt = 1)
        try:
            location_from = kwargs.pop("location_from", None)
            team = team.exclude(id = location_from.id)
        except:
            pass

        team_list = []
        for item in team:
            team_list.append((item.id, item.team))
        self.fields['location_to'].choices = team_list

class EmergencyLeaveForm(forms.ModelForm):
    class Meta:
        model = Emergency_Leave
        fields = ('reason', )


class K9IncidentForm(forms.ModelForm):
    CONCERN = (
        ('Lost', 'Lost'),
        ('Stolen', 'Stolen'),
        ('Accident', 'Accident'),
    )

    k9 = forms.ModelChoiceField(queryset = K9.objects.all(), empty_label=None)
    incident = forms.CharField(max_length=10, label='incident', widget=forms.Select(choices=CONCERN))
    class Meta:
        model = K9_Incident
        fields = ('k9', 'incident', 'title', 'description', 'reported_by', 'clinic')

    def __init__(self, *args, **kwargs):
        super(K9IncidentForm, self).__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['reported_by'].required = False
        self.fields['title'].required = False
        self.fields['incident'].required = False
        self.fields['clinic'].required = False

class HandlerIncidentForm(forms.ModelForm):
    class Meta:
        model = Handler_Incident
        fields = ('handler', 'incident', 'description', 'reported_by', 'k9')

    def __init__(self, *args, **kwargs):
        super(HandlerIncidentForm, self).__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['reported_by'].required = False
        self.fields['k9'].required = False

class HandlerOnLeaveForm(forms.ModelForm):
    incident = forms.CharField()
    handler = forms.ModelChoiceField(queryset = User.objects.none(), empty_label=None)
    class Meta:
        model = Handler_On_Leave
        fields = ('handler', 'incident', 'description', 'date_from', 'date_to')

        widgets = {
            'date_from': DateInput(),
            'date_to': DateInput()
        }

    def __init__(self, *args, **kwargs):
        super(HandlerOnLeaveForm, self).__init__(*args, **kwargs)
        self.fields['incident'].initial = 'On-Leave'
        self.fields['incident'].widget.attrs['readonly'] = "readonly"
        self.fields['handler'].widget.attrs['readonly'] = "readonly"


class DateForm(forms.Form):
    date = forms.DateField(widget=DateInput)

class ReassignAssetsForm(forms.Form):
    k9 = forms.ModelChoiceField(queryset = K9.objects.filter(training_status='For-Deployment').filter(handler=None))
    handler = forms.ModelChoiceField(queryset = User.objects.filter(status='Working').filter(position='Handler').filter(handler=None))

class ReproductiveForm(forms.ModelForm):
    class Meta:
        model = K9
        fields = ('reproductive_stage', 'last_proestrus_date', 'in_heat_months')

        widgets = {
            'last_proestrus_date': DateInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super(ReproductiveForm, self).__init__(*args, **kwargs)
        self.fields['last_proestrus_date'].required = False
        self.fields['reproductive_stage'].required = False
        self.fields['reproductive_stage'].widget.attrs['disabled'] = True


class RequestMiscellaneous(forms.ModelForm):
    miscellaneous = forms.ModelChoiceField(queryset = Miscellaneous.objects.all())
    class Meta:
        model = Miscellaneous_Request
        fields = ('miscellaneous', 'quantity', 'unit')

    def __init__(self, *args, **kwargs):
        super(RequestMiscellaneous, self).__init__(*args, **kwargs)
        self.fields['miscellaneous'].widget.attrs['class'] = 'miscellaneous_item'
        self.fields['unit'].widget.attrs['class'] = 'miscellaneous_unit'
        self.fields['unit'].widget.attrs['readonly'] = True
        # self.fields['miscellaneous'].required = False
        # self.fields['quantity'].required = False

class RequestMedicine(forms.ModelForm):
    medicine = forms.ModelChoiceField(queryset = Medicine_Inventory.objects.exclude(medicine__med_type='Vaccine'))
    class Meta:
        model = Medicine_Request
        fields = ('medicine', 'quantity','unit')

    def __init__(self, *args, **kwargs):
        super(RequestMedicine, self).__init__(*args, **kwargs)
        self.fields['medicine'].widget.attrs['class'] = 'medicine_item'
        self.fields['unit'].widget.attrs['class'] = 'medicine_unit'
        self.fields['unit'].widget.attrs['readonly'] = True
        # self.fields['medicine'].required = False
        # self.fields['quantity'].required = False

class RequestFood(forms.ModelForm):
    food = forms.ModelChoiceField(queryset = Food.objects.filter(foodtype='Adult Dog Food').filter(unit='Sack - 20kg'))
    class Meta:
        model = Food_Request
        fields = ('food', 'quantity','unit')

    def __init__(self, *args, **kwargs):
        super(RequestFood, self).__init__(*args, **kwargs)
        self.fields['food'].widget.attrs['class'] = 'food_item'
        self.fields['unit'].widget.attrs['class'] = 'food_unit'
        self.fields['unit'].widget.attrs['readonly'] = True
        # self.fields['food'].required = False
        # self.fields['quantity'].required = False

class ReplenishmentForm(forms.ModelForm):
    handler = forms.ModelChoiceField(queryset = User.objects.all(), empty_label=None)
    class Meta:
        model= Replenishment_Request
        fields = ('handler',)
    
    def __init__(self, *args, **kwargs):
        super(ReplenishmentForm, self).__init__(*args, **kwargs)

class ItemReplenishmentForm(forms.Form):
    TYPE = (
        ('------------', '------------'),
        ('Dog Food', 'Dog Food'),
        ('Medicine', 'Medicine'),
        ('Miscellaneous', 'Miscellaneous'),
    )
    item_type = forms.CharField(widget=forms.Select(choices=TYPE))
    # item_id = forms.IntegerField()
    item = forms.CharField(widget=forms.Select())
    uom = forms.CharField()
    quantity = forms.IntegerField()
    on_hand = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(ItemReplenishmentForm, self).__init__(*args, **kwargs)
        self.fields['uom'].widget.attrs['readonly'] = True
        self.fields['item_type'].widget.attrs['class'] = 'type'
        self.fields['quantity'].widget.attrs['class'] = 'quantity'
        self.fields['item'].widget.attrs['class'] = 'item'
        self.fields['uom'].widget.attrs['class'] = 'uom'
        self.fields['item_type'].widget.attrs['name'] = 'item_type'
        self.fields['item'].widget.attrs['name'] = 'item'
        self.fields['uom'].widget.attrs['name'] = 'uom'
        self.fields['quantity'].widget.attrs['name'] = 'quantity'
        self.fields['on_hand'].widget.attrs['name'] = 'on_hand'
        self.fields['on_hand'].widget.attrs['class'] = 'on_hand'
        self.fields['on_hand'].required = False
        self.fields['on_hand'].widget.attrs['readonly'] = True
    
class DeathCertK9(forms.ModelForm):
    death_date = forms.DateField(widget = DateInput(), label=None)
    class Meta:
        model = K9
        fields = ('death_cert','death_date')

    def __init__(self, *args, **kwargs):
        super(DeathCertK9, self).__init__(*args, **kwargs)
        self.fields['death_cert'].required = False
        self.fields['death_date'].required = False
