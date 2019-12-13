from django.db import models
from django.utils.timezone import now
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import date as d
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from inventory.models import Medicine, Miscellaneous, Food, Medicine_Inventory
from deployment.models import Team_Assignment, Team_Dog_Deployed
import calendar
#from unitmanagement.models import Notification


from profiles.models import User
from django.db.models import aggregates, Avg, Count, Min, Sum, Q, Max


class Date(models.Model):
    date_from = models.DateField('date_from', null=True)
    date_to = models.DateField('date_to', null=True)

class K9_Supplier(models.Model):
    name = models.CharField('name', max_length=200)
    organization = models.CharField('organization', max_length=200, default='Personal')
    address = models.CharField('address', max_length=200)
    contact_no = models.CharField('contact_no', max_length=200)

    def __str__(self):
        return str(self.name)

class Dog_Breed(models.Model):
    SKILL = (
        ('NDD', 'NDD'),
        ('EDD', 'EDD'),
        ('SAR', 'SAR')
    )

    BREED = (
        ('Belgian Malinois', 'Belgian Malinois'),
        ('Dutch Sheperd', 'Dutch Sheperd'),
        ('German Sheperd', 'German Sheperd'),
        ('Golden Retriever', 'Golden Retriever'),
        ('Jack Russel', 'Jack Russel'),
        ('Labrador Retriever', 'Labrador Retriever'),
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

    SEX = (
        ('Female', 'Female'),
        ('Male', 'Male'),
    )

    breed = models.CharField('breed', choices=BREED,  max_length=200, null=True)
    sex = models.CharField('sex', choices=SEX,  max_length=200, null=True)
    value = models.DecimalField('value',max_digits=50, decimal_places=2,blank=True, null=True)
    life_span = models.IntegerField('life_span', blank=True, null=True)
    temperament = models.CharField('temperament', max_length=200, null=True)
    colors = models.CharField('colors', max_length=200, null=True)
    weight = models.CharField('weight', max_length=200, null=True)
    male_height = models.CharField('male_height', max_length=200, null=True)
    female_height = models.CharField('female_height', max_length=200, null=True)
    skill_recommendation = models.CharField('skill_recommendation', choices=SKILL, max_length=200, null=True, blank=True)
    skill_recommendation2 = models.CharField('skill_recommendation', choices=SKILL, max_length=200, null=True, blank=True)
    skill_recommendation3 = models.CharField('skill_recommendation', choices=SKILL, max_length=200, null=True, blank=True)
    litter_number = models.IntegerField('litter_number', null=True)

    def __str__(self):
        return str(self.breed) +' - '+ str(self.sex)

class K9(models.Model):
    SEX = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )

    COLOR = (
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

    BREED = (
        ('Belgian Malinois', 'Belgian Malinois'),
        ('Dutch Sheperd', 'Dutch Sheperd'),
        ('German Sheperd', 'German Sheperd'),
        ('Golden Retriever', 'Golden Retriever'),
        ('Jack Russel', 'Jack Russel'),
        ('Labrador Retriever', 'Labrador Retriever'),
    )

    STATUS = (
        ('Material Dog', 'Material Dog'),
        ('Working Dog', 'Working Dog'),
        ('Adopted', 'Adopted'),
        ('Due-For-Retirement', 'Due-For-Retirement'),
        ('Retired', 'Retired'),
        ('Dead', 'Dead'),
        ('Sick', 'Sick'),
        ('Stolen', 'Stolen'),
        ('Lost', 'Lost'),
        ('Accident', 'Accident'),
        ('Missing', 'Missing'),
    )

    REPRODUCTIVE = (
        ('Proestrus', 'Proestrus'),
        ('Estrus', 'Estrus'),
        ('Metestrus', 'Metestrus'),
        ('Anestrus', 'Anestrus'),
    )
    SOURCE = (
        ('Procurement', 'Procurement'),
        ('Breeding', 'Breeding'),
    )

    TRAINING = (
        ('Puppy', 'Puppy'),
        ('Unclassified', 'Unclassified'),
        ('Classified', 'Classified'),
        ('On-Training', 'On-Training'),
        ('Trained', 'Trained'),
        ('For-Breeding', 'For-Breeding'),
        ('Breeding', 'Breeding'),
        ('For-Deployment', 'For-Deployment'),
        ('For-Adoption', 'For-Adoption'),
        ('Adopted', 'Adopted'),
        ('Deployed', 'Deployed'),
        ('Light Duty', 'Light Duty'),
        ('Retired', 'Retired'),
        ('Dead', 'Dead'),
        ('Missing', 'Missing'),
    )

    TRAINED = (
        ('Trained', 'Trained'),
        ('Failed', 'Failed')
    )

    image = models.FileField(upload_to='k9_image', default='k9_image/k9_default.png', blank=True, null=True)
    serial_number = models.CharField('serial_number', max_length=200 , default='Unassigned Serial Number')
    name = models.CharField('name', max_length=200)
    handler = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    breed = models.CharField('breed', choices=BREED, max_length=200, blank=True, null=True)
    sex = models.CharField('sex', choices=SEX, max_length=200, default="Unspecified")
    color = models.CharField('color', choices=COLOR, max_length=200, default="Unspecified")
    birth_date = models.DateField('birth_date', null=True, blank=True)
    age = models.IntegerField('age', default = 0)
    source = models.CharField('source', max_length=200, default="Not Specified", choices=SOURCE)
    year_retired = models.DateField('year_retired', null=True, blank=True)
    death_date = models.DateField('death_date', null=True, blank=True)
    assignment = models.CharField('assignment', max_length=200, default="None", null=True, blank=True)
    status = models.CharField('status', choices=STATUS, max_length=200, default="Material Dog")
    training_status = models.CharField('training_status', choices=TRAINING, max_length=200, default="Puppy")
    training_level = models.CharField('training_level', max_length=200, default="Stage 0")
    training_count = models.IntegerField('training_count', default = 0)
    capability = models.CharField('capability', max_length=200, default="None")
    #microchip = models.CharField('microchip', max_length=200, default = 'Unassigned Microchip')
    reproductive_stage = models.CharField('reproductive_stage', choices=REPRODUCTIVE, max_length=200, default="Anestrus")
    age_days = models.IntegerField('age_days', default = 0)
    age_month = models.IntegerField('age_month', default = 0)
    in_heat_months = models.IntegerField('in_heat_months', default = 6)
    last_proestrus_date = models.DateField(blank=True, null=True)
    next_proestrus_date = models.DateField(blank=True, null=True)
    last_estrus_date = models.DateField(blank=True, null=True)
    next_estrus_date = models.DateField(blank=True, null=True)
    metestrus_date = models.DateField(blank=True, null=True)
    anestrus_date = models.DateField(blank=True, null=True)
    supplier =  models.ForeignKey(K9_Supplier, on_delete=models.CASCADE, blank=True, null=True) #if procured
    litter_no = models.IntegerField('litter_no', default = 0)
    last_date_mated = models.DateField(blank=True, null=True)
    trained = models.CharField('trained', choices=TRAINED, max_length=100, blank=True, null=True)
    height = models.DecimalField('height',max_digits=50, decimal_places=2,default=0)
    weight = models.DecimalField('weight',max_digits=50, decimal_places=2,default=0)
    fit = models.BooleanField(default=True)
    date_created = models.DateField('date_created', default=now, blank=True, null=True)
    death_cert = models.FileField(upload_to='k9_image', blank=True, null=True)
    #partnered = models.BooleanField(default=False)

    # def best_fertile_notification(self):
    #     notif = self.estrus_date + td(days=10)
    #     notif = self.estrus_date + td(days=12)
    #     notif = self.estrus_date + td(days=14)
    #     return notif

    def num_in_heat(self):
        return self.in_heat_months/12

    def in_heat_monthly(self):

        upcoming_year = int(dt.now().year) + 1

        months = [0,0,0,0,0,0,0,0,0,0,0,0]
        prostreus_temp = self.last_proestrus_date
        prostreus_temp_year = int(prostreus_temp.year)
        year = []
        while prostreus_temp_year <= upcoming_year:
            if prostreus_temp_year == upcoming_year:

                if prostreus_temp.month == 1:
                    months[0] += 1
                elif prostreus_temp.month == 2:
                    months[1] += 1
                elif prostreus_temp.month == 3:
                    months[2] += 1
                elif prostreus_temp.month == 4:
                    months[3] += 1
                elif prostreus_temp.month == 5:
                    months[4] += 1
                elif prostreus_temp.month == 6:
                    months[5] += 1
                elif prostreus_temp.month == 7:
                    months[6] += 1
                elif prostreus_temp.month == 8:
                    months[7] += 1
                elif prostreus_temp.month == 9:
                    months[8] += 1
                elif prostreus_temp.month == 10:
                    months[9] += 1
                elif prostreus_temp.month == 11:
                    months[10] += 1
                elif prostreus_temp.month == 12:
                    months[11] += 1

            prostreus_temp += relativedelta(months = self.in_heat_months)
            prostreus_temp_year = prostreus_temp.year

        return months

    def calculate_age(self):
        #delta = dt.now().date() - self.birth_date
        #return delta.days
        today = d.today()
        birthdate = self.birth_date
        bday = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        if bday < 1:
            bday = 0
        return bday

    def calculate_months_before(birthday):
        today = d.today()
        birthdate = birthday
        bday = 13 - birthdate.month
        return bday

    def month_remainder(self):
        if d.today().month >= self.birth_date.month:
            month_remainder = d.today().month - self.birth_date.month
        else:
            month_remainder = 12 - self.birth_date.month + d.today().month
        return month_remainder

    def save(self, *args, **kwargs):
        #litter
        if self.sex == 'Female':
            try:
                f = K9_Litter.objects.filter(mother__id=self.id).aggregate(Max('litter_no'))
                self.litter_no = int(f['litter_no__max'])
            except:
                self.litter_no = 0

        else:
            try:
                m = K9_Litter.objects.filter(father__id=self.id).aggregate(Max('litter_no'))
                self.litter_no = int(m['litter_no__max'])
            except:
                self.litter_no = 0

        
        try:
            td = Team_Dog_Deployed.objects.filter(k9__id=self.id).filter(date_pulled=None)[0]
            loc = Team_Assignment.objects.get(id=td.id)
            self.assignment = str(loc)
        except:
            self.assignment = None

        if self.handler != None:
            self.handler.partnered = True
            self.handler.save()

        days = d.today() - self.birth_date
        self.year_retired = self.birth_date + relativedelta(years=+10)
        self.age_days = days.days
        self.age = self.calculate_age()
        self.training_id = self.id
              
        #last_proestrus_date in heat
        #estrus_date start of session,10,12,14
        if self.sex == 'Female':
            if self.last_proestrus_date == None:
                self.last_proestrus_date = d.today() + relativedelta(months=+self.in_heat_months)
            
            self.last_estrus_date = self.last_proestrus_date + relativedelta(days=9)
            self.metestrus_date = self.last_estrus_date + relativedelta(month=2)
            self.anestrus_date = self.metestrus_date + relativedelta(months=4)
            self.next_proestrus_date = self.last_proestrus_date + relativedelta(months=+self.in_heat_months)
            self.next_estrus_date = self.next_proestrus_date + relativedelta(days=9)

            m = d.today() - relativedelta(days=9)
            p = d.today() + relativedelta(days=9)

            if self.last_proestrus_date <= d.today() and self.last_proestrus_date >= m:
                self.reproductive_stage = 'Proestrus'
            elif d.today() == self.last_estrus_date:
                self.reproductive_stage = 'Estrus'
            elif self.last_proestrus_date >=  d.today() and self.last_proestrus_date <= p:
                self.reproductive_stage = 'Proestrus'
            elif d.today() == self.metestrus_date:
                self.reproductive_stage = 'Metestrus'
            elif d.today() == self.anestrus_date:
                self.reproductive_stage = 'Anestrus'
            else:
                self.reproductive_stage = 'Anestrus'

        if self.sex == 'Male':
            self.in_heat_months = 0
            self.last_proestrus_date = None
            self.next_proestrus_date = None
            self.last_estrus_date = None
            self.next_estrus_date = None
            self.metestrus_date = None
            self.anestrus_date = None

        self.age_month = (self.age * 12) + self.month_remainder()
        super(K9, self).save(*args, **kwargs)


    def __str__(self):
        return str(self.name) + " : " + str(self.serial_number)

class K9_Litter(models.Model):
    mother = models.ForeignKey(K9, related_name='dam', on_delete=models.CASCADE, blank=True, null=True)
    father = models.ForeignKey(K9, related_name='sire', on_delete=models.CASCADE, blank=True, null=True)
    litter_no = models.IntegerField('litter_no', blank=True, null=True)
    litter_died = models.IntegerField('litter_died', blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def alive(self):
        litter = int(self.litter_no) - int(self.litter_died)
        return litter

    def save(self, *args, **kwargs):
        if self.litter_no == None:
            self.litter_no = 0
        if self.litter_died == None:
            self.litter_died = 0

        litter = int(self.litter_no) - int(self.litter_died)

        if  self.mother.litter_no < litter:
            self.mother.litter_no = litter
            self.mother.save()

        if  self.father.litter_no < litter:
            self.father.litter_no = litter
            self.father.save()

        self.date = dt.now()
        super(K9_Litter, self).save(*args, **kwargs)

class K9_Past_Owner(models.Model):
    SEX = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    first_name = models.CharField('first_name', max_length=200)
    middle_name = models.CharField('middle_name', max_length=200)
    last_name = models.CharField('last_name', max_length=200)
    address = models.CharField('address', max_length=200)
    sex = models.CharField('sex', choices=SEX, max_length=200, default="Unspecified")
    birth_date = models.DateField('birth_date', blank=True, null=True)
    email = models.EmailField('email', max_length=200, default = "not specified")
    contact_no = models.CharField('contact_no', max_length=200, default = "not specified")

    def __str__(self):
        return str(self.first_name) +' '+ str(self.middle_name) + ' ' + str(self.last_name)

class K9_New_Owner(models.Model):
    SEX = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    first_name = models.CharField('first_name', max_length=200)
    middle_name = models.CharField('middle_name', max_length=200)
    last_name = models.CharField('last_name', max_length=200)
    address = models.CharField('address', max_length=200)
    sex = models.CharField('sex', choices=SEX, max_length=200, default="Unspecified")
    #age = models.IntegerField('age', default = 0)
    birth_date = models.DateField('birth_date', blank=True, null=True)
    email = models.EmailField('email', max_length=200)
    contact_no = models.CharField('contact_no', max_length=200)

    def __str__(self):
        return str(self.first_name) + ' ' + str(self.middle_name) + ' ' + str(self.last_name)

class K9_Donated(models.Model):
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE, blank=True, null=True)
    owner = models.ForeignKey(K9_Past_Owner, on_delete=models.CASCADE)
    date_donated = models.DateField('date_donated', auto_now_add=True)

    def __str__(self):
        return str(self.k9)

class K9_Adopted(models.Model):
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE)
    owner = models.ForeignKey(K9_New_Owner, on_delete=models.CASCADE)
    date_adopted = models.DateField('date_adopted', auto_now_add=True)

    def __str__(self):
        return str(self.k9)


class K9_Parent(models.Model):
    mother = models.ForeignKey(K9, on_delete=models.CASCADE, related_name= "mother", blank=True, null=True)
    father = models.ForeignKey(K9, on_delete=models.CASCADE, related_name="father", blank=True, null=True)
    offspring = models.ForeignKey(K9, on_delete=models.CASCADE, blank=True, null=True)

class K9_Mated(models.Model):
    STATUS = (
        ('Breeding', 'Breeding'),
        ('Pregnant', 'Pregnant'),
        ('Failed', 'Failed'),
        ('Pregnancy Done', 'Pregnancy Done'),
    )

    mother = models.ForeignKey(K9, on_delete=models.CASCADE, related_name= "mom", blank=True, null=True)
    father = models.ForeignKey(K9, on_delete=models.CASCADE, related_name="dad", blank=True, null=True)
    status = models.CharField('status', max_length=200, choices=STATUS, default = "Breeding")
    date_mated = models.DateField('date_mated', blank=True, null=True)

class K9_Quantity(models.Model):
    quantity = models.IntegerField('quantity', default=0)
    date_bought = models.DateField('date_bought', null=True)

#TODO K9 Value Price
class Proposal_Budget(models.Model):
    k9_current = models.IntegerField('k9_current', default=0) #current k9
    k9_needed = models.IntegerField('k9_needed', default=0) #needed to procure k9
    k9_breeded = models.IntegerField('k9_breeded', default=0) # born k9
    # k9_current_train = models.IntegerField('k9_current_train', default=0) #current k9 that needs training
    k9_total = models.DecimalField('k9_total', default=0, max_digits=50, decimal_places=2,)
    food_milk_total = models.DecimalField('food_milk_total', default=0, max_digits=50, decimal_places=2,)
    vac_prev_total = models.DecimalField('vac_prev_total', default=0, max_digits=50, decimal_places=2,)
    medicine_total = models.DecimalField('medicine_total', default=0, max_digits=50, decimal_places=2,)
    vet_supply_total = models.DecimalField('vet_supply_total', default=0, max_digits=50, decimal_places=2,)
    kennel_total = models.DecimalField('kennel_total', default=0, max_digits=50, decimal_places=2, )
    others_total = models.DecimalField('others_total', default=0, max_digits=50, decimal_places=2,)
    training_total = models.DecimalField('training_total', default=0, max_digits=50, decimal_places=2,)
    grand_total = models.DecimalField('grand_total', default=0, max_digits=50, decimal_places=2,)
    train_count = models.IntegerField('train_count', default=0)
    date_created = models.DateField('date_created')
    year_budgeted = models.DateField('year_budgeted')

    def save(self, *args, **kwargs):
        self.year_budgeted = self.date_created  + relativedelta(years=+1)
        super(Proposal_Budget, self).save(*args, **kwargs)

class Proposal_K9(models.Model):
    item = models.ForeignKey(Dog_Breed, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default=0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    percent = models.DecimalField('percent', default=0, max_digits=50, decimal_places=10,)
    proposal = models.ForeignKey(Proposal_Budget, on_delete=models.CASCADE, blank=True, null=True)
    # k9_count = models.IntegerField('k9_count', default=0)

class Proposal_Training(models.Model):
    quantity = models.IntegerField('quantity', default=0)
    price = models.DecimalField('price', default=18000, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    percent = models.DecimalField('percent', default=0, max_digits=50, decimal_places=10,)
    proposal = models.ForeignKey(Proposal_Budget, on_delete=models.CASCADE, blank=True, null=True)

class Proposal_Milk_Food(models.Model):
    item = models.ForeignKey(Food, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default=0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    percent = models.DecimalField('percent', default=0, max_digits=50, decimal_places=10,)
    proposal = models.ForeignKey(Proposal_Budget, on_delete=models.CASCADE, blank=True, null=True)
    # k9_count = models.IntegerField('k9_count', default=0)

class Proposal_Vac_Prev(models.Model):
    item = models.ForeignKey(Medicine_Inventory, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default=0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    percent = models.DecimalField('percent', default=0, max_digits=50, decimal_places=10,)
    proposal = models.ForeignKey(Proposal_Budget, on_delete=models.CASCADE, blank=True, null=True)
    # k9_count = models.IntegerField('k9_count', default=0)

class Proposal_Medicine(models.Model):
    item = models.ForeignKey(Medicine_Inventory, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default = 0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    percent = models.DecimalField('percent', default=0, max_digits=50, decimal_places=10,)
    proposal = models.ForeignKey(Proposal_Budget, on_delete=models.CASCADE, blank=True, null=True)
    # k9_count = models.IntegerField('k9_count', default=0)

class Proposal_Vet_Supply(models.Model):
    item = models.ForeignKey(Miscellaneous, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default = 0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    percent = models.DecimalField('percent', default=0, max_digits=50, decimal_places=10,)
    proposal = models.ForeignKey(Proposal_Budget, on_delete=models.CASCADE, blank=True, null=True)
    # k9_count = models.IntegerField('k9_count', default=0)

class Proposal_Kennel_Supply(models.Model):
    item = models.ForeignKey(Miscellaneous, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default=0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    percent = models.DecimalField('percent', default=0, max_digits=50, decimal_places=10,)
    proposal = models.ForeignKey(Proposal_Budget, on_delete=models.CASCADE, blank=True, null=True)
    # k9_count = models.IntegerField('k9_count', default=0)
    
class Proposal_Others(models.Model):
    item = models.ForeignKey(Miscellaneous, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default=0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    percent = models.DecimalField('percent', default=0, max_digits=50, decimal_places=10,)
    proposal = models.ForeignKey(Proposal_Budget, on_delete=models.CASCADE, blank=True, null=True)
    # k9_count = models.IntegerField('k9_count', default=0)

class Actual_Budget(models.Model):
    k9_current = models.IntegerField('k9_current', default=0)
    k9_needed = models.IntegerField('k9_needed', default=0)
    k9_breeded = models.IntegerField('k9_breeded', default=0)
    k9_total = models.DecimalField('k9_total', default=0, max_digits=50, decimal_places=2,)
    petty_cash = models.DecimalField('petty_cash', default=0, max_digits=50, decimal_places=2,)
    food_milk_total = models.DecimalField('food_milk_total', default=0, max_digits=50, decimal_places=2,)
    vac_prev_total = models.DecimalField('vac_prev_total', default=0, max_digits=50, decimal_places=2,)
    medicine_total = models.DecimalField('medicine_total', default=0, max_digits=50, decimal_places=2,)
    vet_supply_total = models.DecimalField('vet_supply_total', default=0, max_digits=50, decimal_places=2,)
    kennel_total = models.DecimalField('kennel_total', default=0, max_digits=50, decimal_places=2, )
    others_total = models.DecimalField('others_total', default=0, max_digits=50, decimal_places=2,)
    training_total = models.DecimalField('training_total', default=0, max_digits=50, decimal_places=2,)
    grand_total = models.DecimalField('grand_total', default=0, max_digits=50, decimal_places=2,)
    train_count = models.IntegerField('train_count', default=0)
    date_created = models.DateField('date_created', auto_now_add=True)
    year_budgeted = models.DateField('year_budgeted', blank=True, null=True)
    
class Actual_K9(models.Model):
    item = models.ForeignKey(Dog_Breed, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default=0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    proposal = models.ForeignKey(Actual_Budget, on_delete=models.CASCADE, blank=True, null=True)
    
class Actual_Training(models.Model):
    quantity = models.IntegerField('quantity', default=0)
    price = models.DecimalField('price', default=18000, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    proposal = models.ForeignKey(Actual_Budget, on_delete=models.CASCADE, blank=True, null=True)

class Actual_Milk_Food(models.Model):
    item = models.ForeignKey(Food, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default=0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    proposal = models.ForeignKey(Actual_Budget, on_delete=models.CASCADE, blank=True, null=True)

class Actual_Vac_Prev(models.Model):
    item = models.ForeignKey(Medicine_Inventory, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default=0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    percent = models.DecimalField('percent', default=0, max_digits=50, decimal_places=10,)
    proposal = models.ForeignKey(Actual_Budget, on_delete=models.CASCADE, blank=True, null=True)

class Actual_Medicine(models.Model):
    item = models.ForeignKey(Medicine_Inventory, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default = 0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    percent = models.DecimalField('percent', default=0, max_digits=50, decimal_places=10,)
    proposal = models.ForeignKey(Actual_Budget, on_delete=models.CASCADE, blank=True, null=True)

class Actual_Vet_Supply(models.Model):
    item = models.ForeignKey(Miscellaneous, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default = 0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    proposal = models.ForeignKey(Actual_Budget, on_delete=models.CASCADE, blank=True, null=True)

class Actual_Kennel_Supply(models.Model):
    item = models.ForeignKey(Miscellaneous, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default=0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    proposal = models.ForeignKey(Actual_Budget, on_delete=models.CASCADE, blank=True, null=True)
    
class Actual_Others(models.Model):
    item = models.ForeignKey(Miscellaneous, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField('quantity', default=0)
    price = models.DecimalField('price', default=0, max_digits=50, decimal_places=2,)
    total = models.DecimalField('total', default=0, max_digits=50, decimal_places=2,)
    proposal = models.ForeignKey(Actual_Budget, on_delete=models.CASCADE, blank=True, null=True)