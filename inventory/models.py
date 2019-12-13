from django.db import models
from datetime import datetime, date, timedelta
from profiles.models import User
from django.utils import timezone
# from unitmanagement.models import Notification
# Create your models here.

#Medicine
class Medicine(models.Model):
    UOM = (
        ('mg', 'mg'),
        ('mL', 'mL'),
        ('suspension', 'suspension'),
    )
    TYPE = (
        ('Tablet', 'Tablet'),
        ('Capsule', 'Capsule'),
        ('Bottle', 'Bottle'),
        ('Vitamins', 'Vitamins'),
        ('Vaccine', 'Vaccine'),
        ('Preventive', 'Preventive'),
    )

    IMMUNIZATION = (
        ('Anti-Rabies', 'Anti-Rabies'),
        ('Bordetella Bronchiseptica Bacterin', 'Bordetella Bronchiseptica Bacterin'),
        ('Deworming', 'Deworming'),
        ('DHPPiL+CV', 'DHPPiL+CV'),
        ('DHPPiL4', 'DHPPiL4'),
        ('Heartworm', 'Heartworm'),
        ('Tick and Flea', 'Tick and Flea'),
    )

    medicine = models.CharField(max_length=100)
    medicine_fullname = models.CharField(max_length=100, blank=True, null=True)
    med_type = models.CharField('med_type', choices=TYPE, max_length=50, blank=True, null=True)
    immunization = models.CharField('immunization', choices=IMMUNIZATION, max_length=50, blank=True, null=True)
    dose = models.IntegerField('dose', default=1, blank=True, null=True)
    uom = models.CharField('uom', max_length=10, default='pc', blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    price = models.DecimalField('price', max_digits=50, decimal_places=2, null=True)
    # used_yearly = models.IntegerField('used_yearly', default=0, blank=True, null=True)
    # duration = models.IntegerField('duration', default=0, blank=True, null=True)

    def __str__(self):
        return self.medicine_fullname

    def dosage(self):
        return str(self.dose) +' ' + str(self.uom)

    def save(self, *args, **kwargs):
        self.medicine_fullname = str(self.medicine) +' - ' + str(self.dose) + str(self.uom)
        # if self.med_type == 'Vaccine':
        #     self.used_yearly = 365 / int(self.duration)

        super(Medicine, self).save(*args, **kwargs)

class Medicine_Inventory(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField('quantity', default=0)

    def __str__(self):
        return self.medicine.medicine_fullname
#TODO
# add user
class Medicine_Inventory_Count(models.Model):
    inventory = models.ForeignKey(Medicine_Inventory, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    old_quantity = models.IntegerField('old_quantity', default=0)
    quantity = models.IntegerField('quantity', default=0)
    date_counted = models.DateField('date_counted', default=timezone.now)
    time = models.TimeField('time', auto_now_add=True, blank=True)

    def difference(self):
        diff = self.quantity - self.old_quantity
        return diff 

    def __str__(self):
        return self.inventory.medicine.medicine_fullname


class Medicine_Received_Trail(models.Model):
    inventory = models.ForeignKey(Medicine_Inventory, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    old_quantity = models.IntegerField('old_quantity', default=0)
    quantity = models.IntegerField('quantity', default=0)
    date_received = models.DateField('date_received', default=timezone.now)
    time = models.TimeField('time', auto_now_add=True, blank=True)
    expiration_date = models.DateField('expiration_date', null=True, blank=True)
    status = models.CharField(max_length=100, default='Pending')

    def difference(self):
        diff = self.quantity + self.old_quantity
        return diff 

    def __str__(self):
        return self.inventory.medicine.medicine_fullname

class Medicine_Subtracted_Trail(models.Model):
    inventory = models.ForeignKey(Medicine_Inventory, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, default="", null=True, blank=True)
    price = models.DecimalField('price', max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    old_quantity = models.IntegerField('old_quantity', default=0)
    quantity = models.IntegerField('quantity', default=0)
    date_subtracted = models.DateField('date_subtracted', default=timezone.now)
    time = models.TimeField('time', auto_now_add=True, blank=True)

    def __str__(self):
        return self.inventory.medicine.medicine_fullname + ' : ' +str(self.date_subtracted)

    def save(self, *args, **kwargs):
        self.name = str(self.inventory)
        self.price = self.inventory.medicine.price
        super(Medicine_Subtracted_Trail, self).save(*args, **kwargs)
#Food
class Food(models.Model):
    FOODTYPE = (
        ('Adult Dog Food', 'Adult Dog Food'),
        ('Puppy Dog Food', 'Puppy Dog Food'),
        ('Milk', 'Milk'),
    )
    UNIT = (
        ('kilograms', 'kilograms'),
        ('Sack - 20kg', 'Sack - 20kg'),
        ('Box - 1L', 'Box - 1L'),
    )

    food = models.CharField(max_length=100)
    foodtype = models.CharField('foodtype', choices=FOODTYPE, max_length=50)
    unit = models.CharField('unit', choices=UNIT, max_length=50)
    description = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField('price', max_digits=50, decimal_places=2, null=True)
    quantity = models.IntegerField('quantity', default=0)

    def __str__(self):
        return self.food

# class Food_Inventory(models.Model):
#     food = models.ForeignKey(Food, on_delete=models.CASCADE)
#     quantity = models.DecimalField('quantity', default=0, decimal_places=2, max_digits=10)

#     def quantity_grams(self):
#         grams = self.quantity * 1000
#         return grams
    
#     def __str__(self):
#         return self.food.food

#TODO
# add user
class Food_Inventory_Count(models.Model):
    inventory = models.ForeignKey(Food, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    old_quantity = models.IntegerField('old_quantity', default=0)
    quantity = models.IntegerField('quantity', default=0)
    date_counted = models.DateField('date_counted', default=timezone.now)
    time = models.TimeField('time', auto_now_add=True, blank=True)

    def difference(self):
        diff = self.quantity - self.old_quantity
        return diff 
        
    def __str__(self):
        return self.inventory.food

class Food_Received_Trail(models.Model):
    inventory = models.ForeignKey(Food, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    old_quantity = models.IntegerField('old_quantity', default=0)
    quantity = models.IntegerField('quantity', default=0)
    date_received = models.DateField('date_received', default=timezone.now)
    time = models.TimeField('time', auto_now_add=True, blank=True)

    def difference(self):
        diff = self.quantity + self.old_quantity
        return diff 

    def __str__(self):
        return self.inventory.food

class Food_Subtracted_Trail(models.Model):
    inventory = models.ForeignKey(Food, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    old_quantity = models.IntegerField('old_quantity', default=0)
    quantity = models.IntegerField('quantity', default=0)
    date_subtracted = models.DateField('date_subtracted', default=timezone.now)
    time = models.TimeField('time', auto_now_add=True, blank=True)

    def __str__(self):
        return self.inventory.food

class Miscellaneous(models.Model):
    UOM = (
        ('pc', 'pc'),
        ('pack', 'pack'),
        ('box', 'box'),
        ('roll', 'roll'),
        ('can', 'can'),
        ('bottle', 'bottle'),
        ('tube', 'tube'),
    )

    TYPE = (
        ('Vet Supply', 'Vet Supply'),
        ('Kennel Supply', 'Kennel Supply'),
        ('Others', 'Others'),
    )

    miscellaneous = models.CharField(max_length=100)
    uom = models.CharField(max_length=100, choices=UOM, default="pack")
    misc_type = models.CharField(max_length=100, choices=TYPE, default="Others")
    description = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField('price', max_digits=50, decimal_places=2, null=True)
    quantity = models.IntegerField('quantity', default=0)

    def __str__(self):
        return self.miscellaneous

# class Miscellaneous_Inventory(models.Model):
#     miscellaneous = models.ForeignKey(Miscellaneous, on_delete=models.CASCADE)
#     quantity = models.IntegerField('quantity', default=0)

#     def __str__(self):
#         return self.miscellaneous.miscellaneous

#TODO
# add user
class Miscellaneous_Inventory_Count(models.Model):
    inventory = models.ForeignKey(Miscellaneous, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    old_quantity = models.IntegerField('old_quantity', default=0)
    quantity = models.IntegerField('quantity', default=0)
    date_counted = models.DateField('date_counted', default=timezone.now)
    time = models.TimeField('time', auto_now_add=True, blank=True)

    def difference(self):
        diff = self.quantity - self.old_quantity
        return diff 

    def __str__(self):
        return self.inventory.miscellaneous

class Miscellaneous_Received_Trail(models.Model):
    inventory = models.ForeignKey(Miscellaneous, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    old_quantity = models.IntegerField('old_quantity', default=0)
    quantity = models.IntegerField('quantity', default=0)
    date_received = models.DateField('date_received', default=timezone.now)
    time = models.TimeField('time', auto_now_add=True, blank=True)

    def difference(self):
        diff = self.quantity + self.old_quantity
        return diff 

    def __str__(self):
        return self.inventory.miscellaneous

class Miscellaneous_Subtracted_Trail(models.Model):
    inventory = models.ForeignKey(Miscellaneous, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    old_quantity = models.IntegerField('old_quantity', default=0)
    quantity = models.IntegerField('quantity', default=0)
    date_subtracted = models.DateField('date_subtracted', default=timezone.now)
    time = models.TimeField('time', auto_now_add=True, blank=True)

    def __str__(self):
        return self.inventory.miscellaneous

class DamagedEquipemnt(models.Model):
    CONCERN = (
        ('Broken', 'Broken'),
        ('Lost', 'Lost'),
        ('Stolen', 'Stolen'),
    )

    inventory = models.ForeignKey(Miscellaneous, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField('quantity', default=0)
    concern = models.CharField('concern', max_length=100, choices=CONCERN)
    date = models.DateField('date', auto_now_add=True)
    time = models.TimeField('time', auto_now_add=True, blank=True)

    def __str__(self):
        return self.inventory

class Safety_Stock(models.Model):
    puppy_food = models.IntegerField('puppy_food', default=0)
    adult_food = models.IntegerField('adult_food', default=0)
    milk = models.IntegerField('milk', default=0)


