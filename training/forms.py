from django import forms
from django.forms import ModelForm, ValidationError, Form, widgets
from django.contrib.admin.widgets import AdminDateWidget
from datetime import date, datetime
from planningandacquiring.models import K9
from training.models import K9_Handler, Training, K9_Adopted_Owner
from deployment.models import Daily_Refresher
from profiles.models import User
from unitmanagement.models import Handler_K9_History

class DateInput(forms.DateInput):
    input_type = 'date'


class ClassifySkillForm(forms.Form):
    CHOICES = (
        ('SAR', 'SAR'),
        ('NDD', 'NDD'),
        ('EDD', 'EDD'),
    )

    skill = forms.ChoiceField(choices=CHOICES,
                               widget=forms.RadioSelect)


class TestForm(forms.Form):
    k9 = forms.ModelChoiceField(queryset=K9.objects.all())

class add_handler_form(forms.ModelForm):
    handler = forms.ModelChoiceField(queryset = User.objects.filter(status='Working').filter(position='Handler').filter(partnered=False))
    
    class Meta:
        model = K9_Handler
        fields = ('handler',)

    # def __init__(self, *args, **kwargs):
    #     super(add_handler_form, self).__init__(*args, **kwargs)
    #     self.fields['handler'].queryset = self.fields['handler'].queryset.exclude(position="Veterinarian")
    #     self.fields['handler'].queryset = self.fields['handler'].queryset.exclude(position="Administrator")
    #     assigned_handler = K9_Handler.objects.all()
    #     assigned_handler_list = []
    #     for handler in assigned_handler:
    #         assigned_handler_list.append(handler.id)
    #     self.fields['handler'].queryset = self.fields['handler'].queryset.exclude(pk__in=assigned_handler_list)

class assign_handler_form(forms.ModelForm): 
    handler = forms.ModelChoiceField(queryset = User.objects.filter(status='Working').filter(position='Handler').filter(partnered=False),
    widget=forms.RadioSelect(), empty_label=None)
    
    class Meta:
        model = Handler_K9_History
        fields = ('handler','k9')

    def __init__(self, *args, **kwargs):
        super(assign_handler_form, self).__init__(*args, **kwargs)
        self.fields['handler'].required = False
        self.fields['k9'].required = False


class TrainingUpdateForm(forms.ModelForm):
    GRADE = (
        ("0", "0"),
        ("75", "75"),
        ("80", "80"),
        ("85", "85"),
        ("90", "90"),
        ("95", "95"),
        ("100", "100"),
    )
    remarks = forms.CharField(widget = forms.Textarea(attrs={'rows':'3', 'style':'resize:none;'}))

    stage1_1 = forms.CharField(widget=forms.Select(choices=GRADE))
    stage1_2 = forms.CharField(widget=forms.Select(choices=GRADE))
    stage1_3 = forms.CharField(widget=forms.Select(choices=GRADE))
    stage2_1 = forms.CharField(widget=forms.Select(choices=GRADE))
    stage2_2 = forms.CharField(widget=forms.Select(choices=GRADE))
    stage2_3 = forms.CharField(widget=forms.Select(choices=GRADE))
    stage3_1 = forms.CharField(widget=forms.Select(choices=GRADE))
    stage3_2 = forms.CharField(widget=forms.Select(choices=GRADE))
    stage3_3 = forms.CharField(widget=forms.Select(choices=GRADE))

    class Meta:
        model = Training
        fields = ('stage1_1', 'stage1_2', 'stage1_3', 'stage2_1', 'stage2_2', 'stage2_3', 'stage3_1',
        'stage3_2', 'stage3_3', 'remarks')

    def __init__(self, *args, **kwargs):
        super(TrainingUpdateForm, self).__init__(*args, **kwargs)
        self.fields['remarks'].required = False

class SerialNumberForm(forms.Form):
    DOG_TYPE=(
        ('For-Deployment', 'For-Deployment'),
        ('For-Breeding', 'For-Breeding'),
    )
    #microchip = forms.CharField(max_length=200)
    dog_type = forms.CharField(max_length=200, widget = forms.Select(choices=DOG_TYPE))

# class AdoptionForms(forms.ModelForm):
#     address = forms.CharField(widget=forms.Textarea(attrs={'rows':'2', 'style':'resize:none;'}))

#     class Meta:
#         model = K9_Adopted_Owner
#         fields = ('first_name', 'middle_name', 'last_name', 'sex', 'birth_date','email', 'contact_no', 'address','file_adopt')
#         widgets = {
#             'birth_date': DateInput(),
#         }

class RecordForm(forms.ModelForm):

    class Meta:
        model = Daily_Refresher
        fields = '__all__'


class DateForm(forms.Form):
    choose_date = forms.DateField( widget=DateInput())
    # input_type = 'date'
    #input_type = 'date'
    # format='%Y/%m/%d'),
    #                                   input_formats=('%Y/%m/%d',

class adoption_K9_form(forms.ModelForm):
    file_adopt = forms.FileField()
    k9 = forms.ModelChoiceField(queryset = K9.objects.filter(training_status='For-Adoption'))
    breed = forms.CharField(max_length=200)
    color = forms.CharField(max_length=200)
    sex = forms.CharField(max_length=200)
    age = forms.CharField(max_length=200)
    
    class Meta:
        model = K9_Adopted_Owner
        fields = ('k9','file_adopt')

    def __init__(self, *args, **kwargs):
        super(adoption_K9_form, self).__init__(*args, **kwargs)
        self.fields['file_adopt'].required = False
        self.fields['k9'].label_from_instance = lambda obj: "%s" % obj.name
        self.fields['k9'].widget.attrs['class'] = 'k9_name'
        self.fields['breed'].widget.attrs['class'] = 'breed'
        self.fields['color'].widget.attrs['class'] = 'color'
        self.fields['sex'].widget.attrs['class'] = 'sex'
        self.fields['age'].widget.attrs['class'] = 'age'
        self.fields['breed'].widget.attrs['readonly'] = True
        self.fields['color'].widget.attrs['readonly'] = True
        self.fields['sex'].widget.attrs['readonly'] = True
        self.fields['age'].widget.attrs['readonly'] = True
