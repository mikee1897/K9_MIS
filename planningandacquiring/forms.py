from django import forms
from django.forms import ModelForm, ValidationError, Form, widgets
from django.contrib.admin.widgets import AdminDateWidget
from datetime import date, datetime

from .models import K9, K9_Past_Owner, K9_Parent, Date
from .models import K9_Mated
import datetime
import re

from six import string_types

from django.forms.widgets import Widget, Select
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe

from django.forms.widgets import Widget, Select
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe

from profiles.models import User
from .models import K9, K9_Past_Owner, K9_Parent, Date, Dog_Breed, K9_Supplier,Proposal_K9
from django.forms.widgets import CheckboxSelectMultiple


class DateInput(forms.DateInput):
    input_type = 'date'

class DateK9Form(forms.ModelForm):
    class Meta:
        model = K9
        fields = ('birth_date',)
        widgets = {
            'birth_date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super(DateK9Form, self).__init__(*args, **kwargs)
        self.fields['birth_date'].initial = date.today()


class K9SupplierForm(forms.ModelForm):
    address = forms.CharField(widget=forms.Textarea(attrs={'rows':'3', 'style':'resize:none;'}))
    class Meta:
        model = K9_Supplier
        fields = ('name','organization', 'address', 'contact_no')

    def __init__(self, *args, **kwargs):
        super(K9SupplierForm, self).__init__(*args, **kwargs)
        self.fields['organization'].required = False

class SupplierForm(forms.Form):
    supplier = forms.ModelChoiceField(queryset=K9_Supplier.objects.all())
    class Meta:
        model = K9_Supplier
        fields = ('supplier',)

class ProcuredK9Form(forms.Form):
    COLORS = (
        ('Black', 'Black'),
        ('Chocolate', 'Chocolate'),
        ('Yellow', 'Yellow'),
        ('Dark Golden', 'Dark Golden'),
        ('Light Golden', 'Light Golden'),
        ('Cream', 'Cream'),
        ('Golden', 'Golden'),
        ('Brindle', 'Brindle'),
        ('Silver Brindle', 'Silver Brindle'),
        ('Gold Brindle', 'Gold Brindle'),
        ('Salt and Pepper', 'Salt and Pepper'),
        ('Gray Brindle', 'Gray Brindle'),
        ('Blue and Gray', 'Blue and Gray'),
        ('Tan', 'Tan'),
        ('Black-Tipped Fawn', 'Black-Tipped Fawn'),
        ('Mahogany', 'Mahogany'),
        ('White', 'White'),
        ('Black and White', 'Black and White'),
        ('White and Tan', 'White and Tan')
    )
    SEX = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    
    BREED = (
        ('Belgian Malinois', 'Belgian Malinois'),
        ('Dutch Sheperd', 'Dutch Sheperd'),
        ('German Sheperd', 'German Sheperd'),
        ('Golden Retriever', 'Golden Retriever'),
        ('Jack Russel', 'Jack Russel'),
        ('Labrador Retriever', 'Labrador Retriever'),
    )

    date_dhhp = forms.DateField(widget = DateInput(), label='DHPP')
    date_rabies = forms.DateField(widget = DateInput(), label='ANTI-RABIES')
    date_deworm = forms.DateField(widget = DateInput(), label='DEWORMING')
    date_bordertela = forms.DateField(widget = DateInput(), label='BORDERTELLA')
    birth_date = forms.DateField(widget = DateInput(), label='birth_date')
    name = forms.CharField()
    breed = forms.ChoiceField(choices=BREED)
    color = forms.ChoiceField(choices=COLORS)
    sex = forms.ChoiceField(choices=SEX)
    image = forms.ImageField()
    height = forms.DecimalField(decimal_places=2)
    weight = forms.DecimalField(decimal_places=2)

    def __init__(self, *args, **kwargs):
        super(ProcuredK9Form, self).__init__(*args, **kwargs)
        self.fields['image'].required = False

class ReportDateForm(forms.ModelForm):
    class Meta:
        model = Date
        fields = ('date_from', 'date_to')
        widgets = {
            'date_from': DateInput(),
            'date_to': DateInput()
        }

class add_unaffiliated_K9_form(forms.ModelForm):
    class Meta:
        model = K9
        fields = ('name', 'breed', 'sex', 'color', 'birth_date')
        widgets = {
            'birth_date': DateInput(),
        }

class add_donated_K9_form(forms.ModelForm):
    image = forms.ImageField()

    class Meta:
        model = K9
        fields = ('image','name', 'breed', 'sex', 'color', 'birth_date','date_created')
        widgets = {
            'birth_date': DateInput(),
            'date_created': DateInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super(add_donated_K9_form, self).__init__(*args, **kwargs)
        self.fields['breed'].empty_label = None
        self.fields['image'].required = False
        self.fields['date_created'].required = False

class add_donator_form(forms.ModelForm):
    address = forms.CharField(widget=forms.Textarea(attrs={'rows':'2', 'style':'resize:none;'}))

    class Meta:
        model = K9_Past_Owner
        fields = ('first_name', 'middle_name', 'last_name', 'sex', 'birth_date','email', 'contact_no', 'address')
        widgets = {
            'birth_date': DateInput(),
        }

class add_K9_parents_form(forms.Form):
    try:
        females = K9.objects.filter(sex = "Female").filter(training_status = "For-Breeding").filter(age__gte = 1).filter(age__lte = 6)
        males = K9.objects.filter(sex = "Male").filter(training_status = "For-Breeding").filter(age__gte = 1).filter(age__lte = 6)

        mother_list = []
        father_list = []

        for female in females:
            data = (female.id, female.name)
            mother_list.append(data)

        for male in males:
            data  = (male.id, male.name)
            father_list.append(data)

    except:
        mother_list = []
        father_list = []

    mother = forms.ChoiceField(choices=mother_list,
                              widget=forms.RadioSelect)
    father = forms.ChoiceField(choices=father_list,
                              widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        super(add_K9_parents_form, self).__init__(*args, **kwargs)

        females = K9.objects.filter(sex="Female").filter(training_status = "For-Breeding").filter(age__gte = 1).filter(age__lte = 6)
        males = K9.objects.filter(sex="Male").filter(training_status = "For-Breeding").filter(age__gte = 1).filter(age__lte = 6)

        mother_list = []
        father_list = []

        for female in females:
            data = (female.id, female.name)
            mother_list.append(data)

        for male in males:
            data = (male.id, male.name)
            father_list.append(data)

        self.fields['mother'].choices = mother_list
        self.fields['father'].choices = father_list


class add_offspring_K9_form(forms.ModelForm):
    image = forms.ImageField()
    class Meta:
        model = K9
        fields = ('image','name', 'sex', 'color')

    def __init__(self, *args, **kwargs):
        super(add_offspring_K9_form, self).__init__(*args, **kwargs)
        self.fields['image'].required = False
        
class select_breeder(forms.Form):
    k9 = forms.ModelChoiceField(queryset=K9.objects.filter(training_status = 'For-Breeding').filter(status='Working Dog'))

class date_mated_form(forms.ModelForm):
    class Meta:
        model = K9_Mated
        fields = ('date_mated',)
        widgets = {
            'date_mated': DateInput(),
        }

class k9_acquisition_form(forms.ModelForm):
    item = forms.ModelChoiceField(queryset=Dog_Breed.objects.all())
    # value = forms.DecimalField(decimal_places=2, localize=True)
    # quantity = forms.IntegerField(localize=True)
    # total = forms.DecimalField(decimal_places=2,localize=True)
    class Meta:
        model = Proposal_K9
        fields = ('item','quantity','price','total')
    
    def __init__(self, *args, **kwargs):
        super(k9_acquisition_form, self).__init__(*args, **kwargs)
        self.fields['item'].widget.attrs['class'] = 'select_breed'
        self.fields['price'].widget.attrs['class'] = 'select_value'
        self.fields['quantity'].widget.attrs['class'] = 'select_quantity'
        self.fields['total'].widget.attrs['class'] = 'select_total'
        self.fields['total'].widget.attrs['readonly'] = True
        # self.fields['value'].localize = True
        # self.fields['value'].is_localized = True
        # self.fields['quantity'].localize = True
        # self.fields['quantity'].is_localized = True
        # self.fields['total'].localize = True
        # self.fields['total'].is_localized = True
        self.fields['price'].widget.attrs['data-value'] = 0
        self.fields['quantity'].widget.attrs['data-quantity'] = 0
        self.fields['total'].widget.attrs['data-total'] = 0

class k9_detail_form(forms.ModelForm):
    image = forms.ImageField()
    SOURCE = (
        ('Procured', 'Procured'),
        ('Breeding', 'Breeding'),
    )

    training_status = forms.ChoiceField(choices=SOURCE, widget=forms.RadioSelect(attrs={
            'display': 'inline-block',
        }))
    class Meta:
        model = K9
        fields = ('image', 'training_status')
    
    def __init__(self, *args, **kwargs):
        super(k9_detail_form, self).__init__(*args, **kwargs)
        self.fields['training_status'].required = False

#class select_date(forms.Form):

# class budget_food(forms.Form):
#     # class Meta:
#     #     model = Budget_food
#     #     fields = ('food', 'quantity', 'price', 'total', 'budget_allocation')
#     budget_puppy = forms.DecimalField()
#     budget_milk = forms.DecimalField()
#     budget_adult = forms.DecimalField()

#     quantity_puppy = forms.DecimalField()
#     quantity_milk = forms.DecimalField()
#     quantity_adult = forms.DecimalField()

#     price_puppy = forms.IntegerField()
#     price_milk = forms.IntegerField()
#     price_adult = forms.IntegerField()


# class budget_equipment(forms.Form):
#     # class Meta:
#     #     model = Budget_equipment
#     #     fields = ('equipment', 'quantity', 'price', 'total', 'budget_allocation')
#     budget = forms.DecimalField()
#     quantity = forms.IntegerField()
#     price = forms.DecimalField()

# class budget_medicine(forms.Form):
#     # class Meta:
#     #     model = Budget_medicine
#     #     fields = ('medicine', 'quantity', 'price', 'total', 'budget_allocation')
#     budget = forms.DecimalField()
#     quantity = forms.IntegerField()
#     price = forms.DecimalField()


# class budget_vaccine(forms.Form):
#     # class Meta:
#     #     model = Budget_vaccine
#     #     fields = ('vaccine', 'quantity', 'price', 'total', 'budget_allocation')
#     budget = forms.DecimalField()
#     quantity = forms.IntegerField()
#     price = forms.DecimalField()

# class budget_vet_supply(forms.Form):
#     # class Meta:
#     #     model = Budget_vet_supply
#     #     fields = ('vet_supply', 'quantity', 'price', 'total', 'budget_allocation')
#     budget = forms.DecimalField()
#     quantity = forms.IntegerField()
#     price = forms.DecimalField()

# class budget_k9(forms.Form):
#     # class Meta:
#     #     model = Budget_vet_supply
#     #     fields = ('vet_supply', 'quantity', 'price', 'total', 'budget_allocation')
#     budget = forms.DecimalField()
#     quantity = forms.IntegerField()
#     price = forms.DecimalField()

# class budget_date(forms.Form):
#     #date = forms.DateField()
#     date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))

class add_breed_form(forms.ModelForm):
    TEMPERAMENT = (
        ('Kind', 'Kind'),
        ('Outgoing', 'Outgoing'),
        ('Agile', 'Agile'),
        ('Intelligent', 'Intelligent'),
        ('Trusting', 'Trusting'),
        ('Even Tempered', 'Even Tempered'),
        ('Gentle', 'Gentle'),
        ('Reliable', 'Reliable'),
        ('Confident', 'Confident'),
        ('Friendly', 'Friendly'),
        ('Loyal', 'Loyal'),
        ('Alert', 'Alert'),
        ('Curious', 'Curious'),
        ('Watchful', 'Watchful'),
        ('Courageous', 'Courageous'),
        ('Affectionate', 'Affectionate'),
        ('Trainable', 'Trainable'),
        ('Protective', 'Protective'),
        ('Active', 'Active'),
        ('Obedient', 'Obedient'),
        ('Stubborn', 'Stubborn'),
        ('Athletic', 'Athletic'),
        ('Vocal', 'Vocal'),
        ('Energetic', 'Energetic')
    )

    COLORS = (
        ('Black', 'Black'),
        ('Chocolate', 'Chocolate'),
        ('Yellow', 'Yellow'),
        ('Dark Golden', 'Dark Golden'),
        ('Light Golden', 'Light Golden'),
        ('Cream', 'Cream'),
        ('Golden', 'Golden'),
        ('Brindle', 'Brindle'),
        ('Silver Brindle', 'Silver Brindle'),
        ('Gold Brindle', 'Gold Brindle'),
        ('Salt and Pepper', 'Salt and Pepper'),
        ('Gray Brindle', 'Gray Brindle'),
        ('Blue and Gray', 'Blue and Gray'),
        ('Tan', 'Tan'),
        ('Black-Tipped Fawn', 'Black-Tipped Fawn'),
        ('Mahogany', 'Mahogany'),
        ('White', 'White'),
        ('Black and White', 'Black and White'),
        ('White and Tan', 'White and Tan')
    )

    temperament = forms.MultipleChoiceField(required=False,
                                     widget=forms.CheckboxSelectMultiple, choices=TEMPERAMENT)
    colors = forms.MultipleChoiceField(required=False,
                                     widget=forms.CheckboxSelectMultiple, choices=COLORS)


    class Meta:
        model = Dog_Breed
        fields = ('breed', 'life_span', 'litter_number', 'value','sex', 'temperament', 'colors', 'weight', 'male_height','female_height', 'skill_recommendation','skill_recommendation2','skill_recommendation3',)

class DateForm(forms.Form):
    from_date = forms.DateField(widget=DateInput())
    to_date = forms.DateField(widget=DateInput())

class HistDateForm(forms.Form):
    cur_year = datetime.datetime.today().year

    #year_list = []

   # for x in range(cur_year - 15, cur_year + 15):
     #   year_list.append(x)

   # print(year_list)

    #YEAR = (
      #  year_list
   # )
    #hist_date =  forms.ChoiceField(widget = forms.Select(choices=YEAR))
    hist_date = forms.ChoiceField(choices=[(x, x) for x in range(cur_year - 15, cur_year + 15)])