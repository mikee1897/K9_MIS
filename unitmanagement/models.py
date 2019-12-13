from django.db import models

from profiles.models import User
from inventory.models import Medicine, Miscellaneous, Food, Medicine_Inventory
from deployment.models import Incidents, Team_Assignment, Team_Dog_Deployed
from training.models import Training, Training_Schedule
from profiles.models import User, Account
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.sessions.models import Session
from planningandacquiring.models import K9
from django.contrib.auth.models import User as AuthUser
from django.utils import timezone
# Create your models here.


class Handler_K9_History(models.Model):
    handler = models.ForeignKey(User, on_delete=models.CASCADE)
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE)
    date = models.DateField('date', default=timezone.now)

    def __str__(self):
        return str(self.handler) + ': ' + str(self.k9.capability)

class K9_Incident(models.Model):
    INCIDENT = (
        ('Stolen', 'Stolen'),
        ('Lost', 'Lost'),
        ('Accident', 'Accident'),
        ('Sick', 'Sick'),
        ('Missing', 'Missing')
    )
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE, null=True, blank=True)
    incident = models.CharField('incident', max_length=100, choices=INCIDENT, default="")
    title = models.CharField('title', max_length=100)
    date = models.DateField('date', default=timezone.now)
    description = models.TextField('description', max_length=200)
    status = models.CharField('status', max_length=200, default="Pending")
    clinic = models.CharField('clinic', max_length=200, null=True, blank=True)
    reported_by = models.CharField('reported_by', max_length=200, null=True, blank=True)
    def save(self, *args, **kwargs):
        if self.incident == 'Sick' or self.incident == 'Accident':
            if self.clinic == None:
                self.clinic = "PCG CLINIC"
        super(K9_Incident, self).save(*args, **kwargs)

class Image(models.Model):
    incident_id = models.ForeignKey(K9_Incident, on_delete=models.CASCADE, null=True, blank=True)
    image = models.FileField(upload_to='incident_image', blank=True, null=True)


class Health(models.Model):
    dog = models.ForeignKey(K9, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField('date', default=timezone.now)
    problem = models.TextField('problem', max_length=800, null=True, blank=True)
    treatment = models.TextField('treatment', max_length=800, null=True, blank=True)
    status = models.CharField('status', max_length=200, default="On-Going")
    veterinary = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    duration = models.IntegerField('duration', null=True, blank=True, default=0)
    date_done = models.DateField('date_done', null=True, blank=True)
    incident_id = models.ForeignKey(K9_Incident, on_delete=models.CASCADE, null=True, blank=True)
    image = models.FileField(upload_to='prescription_image', blank=True, null=True,  default='prescription_image/no-image.jpg')
    follow_up = models.BooleanField(default=False)
    follow_up_date = models.DateField('follow_up_date', null=True, blank=True)
    follow_up_done = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + ': ' + str(self.date) #+' - ' + str(self.dog.name)

    def expire(self):
        expired = self.date_done + timedelta(days=7)
        e = expired - date.today()
        return e.days

    def expire_date(self):
        expired = self.date_done + timedelta(days=7)
        return expired
    #
    def save(self, *args, **kwargs):
        if self.date != None:
            self.date_done = self.date + timedelta(days=self.duration)
    
        if date.today() == self.date_done:
            self.dog.status = 'Working Dog'
        super(Health, self).save(*args, **kwargs)


class HealthMedicine(models.Model):
    TIME_OF_DAY = (
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Night', 'Night'),
        ('Morning/Afternoon', 'Morning/Afternoon'),
        ('Morning/Night', 'Morning/Night'),
        ('Afternoon/Night', 'Afternoon/Night'),
        ('Morning/Afternoon/Night', 'Morning/Afternoon/Night'),
    )

    health = models.ForeignKey(Health, on_delete=models.CASCADE, related_name='health')
    medicine = models.ForeignKey(Medicine_Inventory, on_delete=models.CASCADE)
    quantity = models.IntegerField('quantity', default=0)
    time_of_day = models.CharField('time_of_day', choices=TIME_OF_DAY, max_length=200, default="")
    duration = models.IntegerField('duration', default=1)

    def __str__(self):
        return str(self.id) + ': ' + str(self.health.date)  # + '-' + str(self.health.dog)

class Transaction_Health(models.Model):
    health = models.ForeignKey(Health, on_delete=models.CASCADE, null=True, blank=True, related_name='initial_health')
    health2 = models.ForeignKey(Health, on_delete=models.CASCADE, null=True, blank=True,  related_name='follow_health')
    incident = models.ForeignKey(K9_Incident, on_delete=models.CASCADE, null=True, blank=True, related_name='initial')
    follow_up = models.ForeignKey(K9_Incident, on_delete=models.CASCADE, null=True, blank=True, related_name='follow_up')
    status = models.CharField('status', max_length=200, default="Pending")

class PhysicalExam(models.Model):
    EXAMSTATUS = (
        ('Normal', 'Normal'),
        ('Abnormal', 'Abnormal'),
        ('Not Examined', 'Not Examined'),
    )

    BODY_SCORE = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )

    dog = models.ForeignKey(K9, on_delete=models.CASCADE)
    veterinary = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cage_number = models.IntegerField('cage_number', default=0)
    general_appearance = models.CharField('general_appearance', choices=EXAMSTATUS, max_length=200, default='Normal')
    integumentary = models.CharField('integumentary', choices=EXAMSTATUS, max_length=200, default='Normal')
    musculo_skeletal = models.CharField('musculo_skeletal', choices=EXAMSTATUS, max_length=200, default='Normal')
    respiratory = models.CharField('respiratory', choices=EXAMSTATUS, max_length=200, default='Normal')
    genito_urinary = models.CharField('genito_urinary', choices=EXAMSTATUS, max_length=200, default='Normal')
    nervous = models.CharField('nervous', choices=EXAMSTATUS, max_length=200, default='Normal')
    circulatory = models.CharField('circulatory', choices=EXAMSTATUS, max_length=200, default='Normal')
    digestive = models.CharField('digestive', choices=EXAMSTATUS, max_length=200, default='Normal')
    mucous_membrances = models.CharField('mucous_membrances', choices=EXAMSTATUS, max_length=200, default='Normal')
    lymph_nodes = models.CharField('lymph_nodes', choices=EXAMSTATUS, max_length=200, default='Normal')
    eyes = models.CharField('eyes', choices=EXAMSTATUS, max_length=200, default='Normal')
    ears = models.CharField('ears', choices=EXAMSTATUS, max_length=200, default='Normal')
    remarks = models.TextField('remarks', max_length=200, null=True, blank=True)
    date = models.DateField('date', default=timezone.now)
    date_next_exam = models.DateField('date_next_exam', null=True, blank=True)
    status = models.CharField('status', max_length=200, default="Pending")
    body_score = models.IntegerField('body_score', choices=BODY_SCORE, default = 3)
    heart_rate = models.IntegerField('heart_rate', null=True, blank=True)
    respiratory_rate = models.IntegerField('respiratory_rate', null=True, blank=True)
    temperature = models.DecimalField('temperature',null=True, blank=True, max_digits=50, decimal_places=2)
    weight = models.DecimalField('weight', null=True, blank=True, max_digits=50, decimal_places=2)
    cleared = models.BooleanField(default=False)

    def due_notification(self):
        notif = self.date_next_exam - timedelta(days=7)
        return notif

    def save(self, *args, **kwargs):
        # self.date_next_exam = self.date + timedelta(days=365)
        # if self.body_score == 1 or self.body_score == 5:
        #     self.cleared == False
        # else:
        #     self.cleared == True
        super(PhysicalExam, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.date) + ': ' + str(self.dog.name)

class VaccinceRecord(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Done', 'Done'),
    )

    k9 = models.ForeignKey(K9, on_delete=models.CASCADE, null=True, blank=True)
    deworming_1 = models.BooleanField(default=False)     #2weeks
    deworming_2 = models.BooleanField(default=False)     #4weeks
    deworming_3 = models.BooleanField(default=False)     #6weeks
    deworming_4 = models.BooleanField(default=False)     #9weeks

    dhppil_cv_1 = models.BooleanField(default=False)     #6weeks *
    dhppil_cv_2 = models.BooleanField(default=False)     #9weeks *
    dhppil_cv_3 = models.BooleanField(default=False)     #12weeks *

    heartworm_1 = models.BooleanField(default=False)     #6weeks
    heartworm_2 = models.BooleanField(default=False)     #10weeks
    heartworm_3 = models.BooleanField(default=False)     #14weeks
    heartworm_4 = models.BooleanField(default=False)     #18weeks
    heartworm_5 = models.BooleanField(default=False)     #22weeks
    heartworm_6 = models.BooleanField(default=False)     #26weeks
    heartworm_7 = models.BooleanField(default=False)     #30weeks
    heartworm_8 = models.BooleanField(default=False)     #34weeks

    anti_rabies = models.BooleanField(default=False)     #12weeks *

    bordetella_1 = models.BooleanField(default=False)    #8weeks *
    bordetella_2 = models.BooleanField(default=False)    #11weeks *

    dhppil4_1 = models.BooleanField(default=False)       #15weeks *
    dhppil4_2 = models.BooleanField(default=False)       #18weeks *

    tick_flea_1 = models.BooleanField(default=False)     #8weeks
    tick_flea_2 = models.BooleanField(default=False)     #12weeks
    tick_flea_3 = models.BooleanField(default=False)     #16weeks
    tick_flea_4 = models.BooleanField(default=False)     #20weeks
    tick_flea_5 = models.BooleanField(default=False)     #24weeks
    tick_flea_6 = models.BooleanField(default=False)     #28weeks
    tick_flea_7 = models.BooleanField(default=False)     #32weeks
    status = models.CharField('status', choices=STATUS, max_length=200, default='Pending')
    def __str__(self):
        return str(self.k9)

    def save(self, *args, **kwargs):
        if self.dhppil4_1 == True and self.dhppil4_2 == True and self.bordetella_1 == True and self.bordetella_2 == True and self.dhppil_cv_1 == True and self.dhppil_cv_2 == True and self.dhppil_cv_3 == True and self.anti_rabies == True:
            k9 = K9.objects.get(id=self.k9.id)
            k9.training_status = 'Unclassified'
            k9.save()

        if self.deworming_1 == True and self.deworming_2 == True and self.deworming_3 == True and self.deworming_4 == True and self.dhppil_cv_1 == True and self.dhppil_cv_2 == True and self.dhppil_cv_3 == True and self.heartworm_1 == True and self.heartworm_2 == True and self.heartworm_3 == True and self.heartworm_4 == True and self.heartworm_5 == True and self.heartworm_6 == True and self.heartworm_7 == True and self.heartworm_8 == True and self.anti_rabies == True and self.bordetella_1 == True and self.bordetella_2 == True and self.dhppil4_1 == True and self.dhppil4_2 == True and self.tick_flea_1 == True and self.tick_flea_2 == True and self.tick_flea_3 == True and self.tick_flea_4 == True and self.tick_flea_5 == True and self.tick_flea_6 == True and self.tick_flea_7 == True:
            self.status = 'Done'
        
        super(VaccinceRecord, self).save(*args, **kwargs)


class VaccineUsed(models.Model):
    vaccine_record = models.ForeignKey(VaccinceRecord, on_delete=models.CASCADE, related_name='record', null=True, blank=True)
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE, null=True, blank=True)
    order = models.IntegerField('order', default=0)
    age = models.CharField('age', max_length=200, null=True, blank=True)
    disease = models.CharField('disease', max_length=200, null=True, blank=True)
    vaccine = models.ForeignKey(Medicine_Inventory, on_delete=models.CASCADE, null=True, blank=True)
    date_vaccinated = models.DateField('date_vaccinated', null=True, blank=True)
    veterinary = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.FileField(upload_to='health_image', blank=True, null=True)
    done = models.BooleanField(default=False)
    date = models.DateField('date', default=timezone.now)

    def __str__(self):
        return str(self.k9) + ':' + str(self.disease) + '-' + str(self.date_vaccinated)

class Replenishment_Request(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Received', 'Received'),
    )

    handler = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tl_request')
    status = models.CharField('status', max_length=200, default="Pending", choices=STATUS)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='admin_give')
    date_approved = models.DateField('date_approved', null=True, blank=True)
    date_received = models.DateField('date_received', null=True, blank=True)
    date_requested = models.DateField('date_requested', default=timezone.now)
# Request Equipment Connect to K9_Pre_Deployment Equipments
class Miscellaneous_Request(models.Model):
    request = models.ForeignKey(Replenishment_Request, on_delete=models.CASCADE, null=True, blank=True,related_name='misc_replenishment')
    miscellaneous = models.ForeignKey(Miscellaneous, on_delete=models.CASCADE)
    quantity = models.IntegerField('quantity', null=True, blank=True)
    unit = models.CharField('unit', max_length=200, null=True, blank=True)

class Medicine_Request(models.Model):
    request = models.ForeignKey(Replenishment_Request, on_delete=models.CASCADE, null=True, blank=True, related_name='med_replenishment')
    medicine = models.ForeignKey(Medicine_Inventory, on_delete=models.CASCADE)
    quantity = models.IntegerField('quantity', null=True, blank=True)
    unit = models.CharField('unit', max_length=200, null=True, blank=True)

class Food_Request(models.Model):
    request = models.ForeignKey(Replenishment_Request, on_delete=models.CASCADE, null=True, blank=True,related_name='food_replenishment')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.IntegerField('quantity', null=True, blank=True)
    unit = models.CharField('unit', max_length=200, null=True, blank=True)
    
class Handler_On_Leave(models.Model):

    STATUS = (
        ('Approved', 'Approved'),
        ('Denied', 'Denied'),
        ('Pending', 'Pending')
    )

    handler = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='handler_leave')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='admin')
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE, null=True, blank=True)
    incident = models.CharField('incident', max_length=100, default="On-Leave")
    date = models.DateField('date', default=timezone.now)
    description = models.TextField('description', max_length=200, null=True, blank=True)
    reply = models.TextField('description', max_length=200, null=True, blank=True)
    status = models.CharField('status', max_length=200, default="Pending")
    date_from = models.DateField('date_from', null=True, blank=True)
    date_to = models.DateField('date_to', null=True, blank=True)
    duration = models.IntegerField('duration', null=True, blank=True)
    is_actioned = models.BooleanField('is_actioned', null=True, blank=True, default=False)

    def save(self, *args, **kwargs):
        days = self.date_to - self.date_from
        self.duration = days.days
        super(Handler_On_Leave, self).save(*args, **kwargs)


class Handler_Incident(models.Model):
    INCIDENT = (
        ('Rescued People', 'Rescued People'),
        ('Made an Arrest', 'Made an Arrest'),
        ('Poor Performance', 'Poor Performance'),
        ('Violation', 'Violation'),
        ('Accident', 'Accident'),
        ('MIA', 'MIA'),
        ('Died', 'Died'),
        ('Others', 'Others'),
    )
    handler = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name='handler_incident')
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE, null=True, blank=True)
    incident = models.CharField('incident', choices=INCIDENT,max_length=100, null=True, blank=True)
    date = models.DateField('date', default=timezone.now)
    description = models.TextField('description', max_length=200)
    status = models.CharField('status', max_length=200, default="Pending")
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='leader')

    def save(self, *args, **kwargs):
        if self.incident == 'Died':
            self.handler.status = 'Died'
            self.handler.partnered = False
            self.handler.assigned = None
            self.k9.handler = None
        super(Handler_Incident, self).save(*args, **kwargs)

class Request_Transfer(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Denied', 'Denied'),
        ('Approved', 'Approved'),
        ('Done', 'Done'),
    )

    handler = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_created =  models.DateField('date_created', default=timezone.now)
    date_of_transfer = models.DateField('date_created', null=True, blank=True)
    location_from = models.ForeignKey('deployment.Team_Assignment', on_delete=models.CASCADE, related_name='location_from', null=True, blank=True)
    location_to = models.ForeignKey('deployment.Team_Assignment', on_delete=models.CASCADE, related_name='location_to', null=True, blank=True)
    status = models.CharField('status', choices=STATUS,max_length=100, default='Pending')
    remarks = models.TextField('remarks', max_length=200, null=True, blank=True)

class Call_Back_K9(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Returned', 'Returned'),
    )
    date_created =  models.DateField('date_created', default=timezone.now)
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE, null=True, blank=True)
    handler = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField('status', choices=STATUS,max_length=100, default='Pending')
    date_confirmed = models.DateField('date_confirmed', null=True, blank=True)
    date_returned = models.DateField('date_returned', null=True, blank=True)

# class Call_Back_Handler(models.Model):
#     STATUS = (
#         ('Pending', 'Pending'),
#         ('Confirmed', 'Confirmed'),
#         ('Returned', 'Returned'),
#     )
#     date_created = models.DateField('date_created', default=timezone.now)
#     handler = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     status = models.CharField('status', choices=STATUS, max_length=100, default='Pending')
#     date_confirmed = models.DateField('date_confirmed', null=True, blank=True)
#     date_returned = models.DateField('date_returned', null=True, blank=True)

class Temporary_Handler(models.Model):
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE, null=True, blank=True)
    original = models.ForeignKey(User, null=True, related_name='original', on_delete=models.CASCADE)
    temp = models.ForeignKey(User, null=True, related_name='temp', on_delete=models.CASCADE)
    date_given = models.DateField('date_given', null=True, blank=True)
    date_returned = models.DateField('date_returned', null=True, blank=True)

class Emergency_Leave(models.Model):
    STATUS = (
        ('Ongoing', 'Ongoing'),
        ('Returned', 'Returned'),
        ('MIA', 'MIA')
    )

    handler = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_of_leave = models.DateField('date_given', null=True, blank=True)
    date_of_return = models.DateField('date_returned', null=True, blank=True)
    duration = models.IntegerField('duration', null=True, blank=True, default=0)
    status = models.CharField('status', choices=STATUS, max_length=100, default='Ongoing')
    reason = models.TextField('reason', max_length=200)
    is_actioned = models.BooleanField('is_actioned', null=True, blank=True, default=False)

    def save(self, *args, **kwargs):
        if self.date_of_return !=None and self.date_of_leave != None:
            days = self.date_of_return-self.date_of_leave
            self.duration = days.days
        super(Emergency_Leave, self).save(*args, **kwargs)

class Notification(models.Model):
    POSITION = (
        ('Administrator', 'Administrator'),
        ('Veterinarian', 'Veterinarian'),
        ('Handler', 'Handler'),
    )

    NOTIF_TYPE = (
        ('physical_exam', 'physical_exam'),
        ('vaccination', 'vaccination'),
        ('dog_request', 'dog_request'),
        ('inventory_low', 'inventory_low'), #VERIFY
        ('heat_cycle', 'heat_cycle'),
        ('location_incident', 'location_incident'),
        ('equipment_request', 'equipment_request'), #VERIFY
        ('k9_died', 'k9_died'),
        ('k9_sick', 'k9_sick'),
        ('k9_stolen', 'k9_stolen'),
        ('k9_accident', 'k9_accident'),
        ('handler_died', 'handler_died'),
        ('handler_on_leave', 'handler_on_leave'),
        ('retired_k9', 'retired_k9'),
        ('medicine_done', 'medicine_done'),
        ('medicine_given', 'medicine_given'),
        ('call_back', 'call_back'),
        ('pregnancy', 'pregnancy'),
        ('breeding', 'breeding'),
        ('initial_deployment', 'initial_deployment'),
        ('checkup', 'checkup'),
        ('k9_given', 'k9_given'),
    )

    k9 = models.ForeignKey(K9, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    other_id = models.IntegerField(blank=True, null=True)
    notif_type = models.CharField('notif_type', max_length=100, choices=NOTIF_TYPE, blank=True, null=True)
    position = models.CharField('position', max_length=100, choices=POSITION, default="Administrator")
    message = models.CharField(max_length=200)
    viewed = models.BooleanField(default=False)
    datetime = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super(Notification, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.message) + ' : ' + str(self.datetime)

#When medicine is created, also create inventory instance
@receiver(post_save, sender=Medicine)
def create_medicine_inventory(sender, instance, **kwargs):
    if kwargs.get('created', False):
        Medicine_Inventory.objects.create(medicine=instance, quantity=0)

# K9 Training
# @receiver(post_save, sender=K9)
# def create_training_record(sender, instance, **kwargs):
#     if kwargs.get('created', False):
#         Training.objects.create(k9=instance, training=instance.capability)
#         Training_Schedule.objects.create(k9 = instance)

@receiver(post_save, sender=K9)
def create_training_record(sender, instance, **kwargs):
    if kwargs.get('created', False):
        Training.objects.create(k9=instance, training='EDD', stage = "Stage 0")
        Training.objects.create(k9=instance, training='NDD', stage = "Stage 0")
        Training.objects.create(k9=instance, training='SAR', stage = "Stage 0")

        Training_Schedule.objects.create(k9 = instance)

#create vaccine record, and vaccine used
@receiver(post_save, sender=K9)
def create_k9_vaccines(sender, instance, **kwargs):
    if kwargs.get('created', False):
        if instance.source == 'Procurement':
            cvr = VaccinceRecord.objects.create(k9=instance,  deworming_1=True, deworming_2=True, deworming_3=True,
            deworming_4=True, dhppil_cv_1=True, dhppil_cv_2=True, dhppil_cv_3=True, heartworm_1=True, heartworm_2=True,
            heartworm_3=True, heartworm_4=True, heartworm_5=True, heartworm_6=True, heartworm_7=True, heartworm_8=True,
            anti_rabies=True, bordetella_1=True, bordetella_2=True, dhppil4_1=True, dhppil4_2=True, tick_flea_1=True,
            tick_flea_2=True, tick_flea_3=True, tick_flea_4=True, tick_flea_5=True, tick_flea_6=True, tick_flea_7=True)

        else:
            cvr = VaccinceRecord.objects.create(k9=instance)
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '2 Weeks', disease='1st Deworming', order='1')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '4 Weeks', disease='2nd Deworming', order='2')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '6 Weeks', disease='3rd Deworming', order='3')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '6 Weeks', disease='1st dose DHPPiL+CV Vaccination', order='4')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '6 Weeks', disease='1st Heartworm Prevention', order='5')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '8 Weeks', disease='1st dose Bordetella Bronchiseptica Bacterin', order='6')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '8 Weeks', disease='1st Tick and Flea Prevention', order='7')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '9 Weeks', disease='2nd dose DHPPiL+CV', order='8')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '9 Weeks', disease='4th Deworming', order='9')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '10 Weeks', disease='2nd Heartworm Prevention', order='10')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '11 Weeks', disease='2nd dose Bordetella Bronchiseptica Bacterin', order='11')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '12 Weeks', disease='Anti-Rabies Vaccination', order='12')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '12 Weeks', disease='2nd Tick and Flea Prevention', order='13')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '12 Weeks', disease='3rd dose DHPPiL+CV Vaccination', order='14')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '14 Weeks', disease='3rd Heartworm Prevention', order='15')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '15 Weeks', disease='1st dose DHPPiL4 Vaccination', order='16')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '16 Weeks', disease='3rd Tick and Flea Prevention', order='17')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '18 Weeks', disease='2nd dose DHPPiL4 Vaccination', order='18')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '18 Weeks', disease='4th Heartworm Prevention', order='19')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '20 Weeks', disease='4th Tick and Flea Prevention', order='20')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '22 Weeks', disease='5th Heartworm Prevention', order='21')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '24 Weeks', disease='5th Tick and Flea Prevention', order='22')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '26 Weeks', disease='6th Heartworm Prevention', order='23')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '28 Weeks', disease='6th Tick and Flea Prevention', order='24')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '30 Weeks', disease='7th Heartworm Prevention', order='25')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '32 Weeks', disease='7th Tick and Flea Prevention', order='26')
            VaccineUsed.objects.create(vaccine_record = cvr, k9=instance, age= '34 Weeks', disease='8th Heartworm Prevention', order='27')



#######################################################################################################################

#TODO EDIT
@receiver(post_save, sender=PhysicalExam)
def phex_next_date(sender, instance, **kwargs):
    if kwargs.get('created', False):
        instance.date_next_exam = instance.date + relativedelta(year=+1)
        instance.save()

#TODO EDIT
# HANDLER INCIDENT repored
@receiver(post_save, sender=Handler_Incident)
def create_handler_incident_notif(sender, instance, **kwargs):
    if kwargs.get('created', False):
        if instance.incident == 'Died':
            Notification.objects.create(user = instance.handler,
                            position = 'Administrator',
                            other_id = instance.id,
                            notif_type = 'handler_died',
                            message= 'Reported Deceased! ' + str(instance.handler))
        else:
            Notification.objects.create(user = instance.handler,
                            position = 'Administrator',
                            other_id = instance.id,
                            notif_type = 'handler_on_leave',
                            message= 'On-Leave Request! ' + str(instance.handler))
#TODO HEALTH TEST
@receiver(post_save, sender=Health)
def create_handler_health_notif(sender, instance, **kwargs):
    if kwargs.get('created', False):
            Notification.objects.create(user = instance.dog.handler,
                            k9 = instance.dog,
                            position = 'Handler',
                            other_id = instance.id,
                            notif_type = 'medicine_given',
                            message= 'Health Concern has been reviewed. See Details.')

#TODO K9 INCIDENT Add died and accident
@receiver(post_save, sender=K9_Incident)
def create_k9_incident_notif(sender, instance, **kwargs):
    if kwargs.get('created', False):
        if instance.incident == 'Sick':
            Notification.objects.create(k9 = instance.k9,
                            position = 'Veterinarian',
                            other_id = instance.id,
                            notif_type = 'k9_sick',
                            message= str(instance.k9.name) + ' has a health concern! ')
        elif instance.incident == 'Lost':
            Notification.objects.create(k9 = instance.k9,
                            position = 'Administrator',
                            other_id = instance.id,
                            notif_type = 'k9_lost',
                            message= str(instance.k9.name) + ' is reported Lost! ')
        elif instance.incident == 'Stolen':
            Notification.objects.create(k9 = instance.k9,
                            position = 'Administrator',
                            other_id = instance.id,
                            notif_type = 'k9_stolen',
                            message= str(instance.k9.name) + ' is reported Stolen! ')

# #TODO EQUIPMENT Verify
# @receiver(post_save, sender=Equipment_Request)
# def create_damaged_equipment_notif(sender, instance, **kwargs):
#     if kwargs.get('created', False):
#         Notification.objects.create(user = instance.handler,
#                             position = 'Administrator',
#                             other_id=instance.id,
#                             notif_type = 'equipment_request',
#                             message='Equipment Concern!')

#TODO EQUIPMENT Verify
@receiver(post_save, sender=Call_Back_K9)
def back_to_base(sender, instance, **kwargs):
    if kwargs.get('created', False):
        td = Team_Dog_Deployed.objects.filter(k9=instance.k9).filter(date_pulled=None)[0]
        ta = Team_Assignment.objects.filter(id=td.team_assignment.id)[0]
        Notification.objects.create(user =  ta.team_leader,
                                position = 'Handler',
                                other_id=instance.k9.id,
                                notif_type = 'back_to_base',
                                message= str(instance.k9.handler) + ' and '+str(instance.k9)+ ' has been called back to base.')

@receiver(post_save, sender=AuthUser)
def account_create(sender, instance, **kwargs):
    if kwargs.get('created', False):
        try:
            UserID = User.objects.last()
            Account.objects.create(UserID = UserID,serial_number=instance.username, email_address=instance.email, password=instance.password)
        except:
            UserID = User.objects.create(position='Administrator',rank='PO1',firstname=instance.username, lastname='Superuser', middlename='Su',birthdate=date.today())
            Account.objects.create(UserID = UserID,serial_number=instance.username, email_address=instance.email, password=instance.password)
            instance.first_name = instance.username
            instance.last_name = 'Superuser'
            instance.save()

#LOCATION INCIDENT reported
@receiver(post_save, sender=Incidents)
def location_incident(sender, instance, **kwargs):
    if kwargs.get('created', False):
        c = ''
        if instance.type == 'Explosives Related':
            c = ' has reported an '
        elif instance.type == 'Narcotics Related' or instance.type == 'Search and Rescue Related':
            c = ' has reported a '
        else:
            pass

        if c == '':
            Notification.objects.create(user = instance.user,
                                position = 'Administrator',
                                other_id=instance.id,
                                notif_type = 'location_incident',
                                message= str(instance.user) + ' has reported an incident at ' +
                                str(instance.location) + '.')
        else:
            Notification.objects.create(user = instance.user,
                                position = 'Administrator',
                                other_id=instance.id,
                                notif_type = 'location_incident',
                                message= str(instance.user) + c + str(instance.type) +
                                ' incident at ' + str(instance.location) + '.')