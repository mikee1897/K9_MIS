from django.db import models
from planningandacquiring.models import K9
from profiles.models import User
from deployment.models import Location

from datetime import datetime as dt
from datetime import timedelta as td
from datetime import date as d
import ast
from decimal import *
from django.utils import timezone
# Create your models here.

class K9_Genealogy(models.Model):
    o = models.ForeignKey(K9, on_delete=models.CASCADE, blank=True, null=True)
    m = models.ForeignKey(K9, on_delete=models.CASCADE, related_name="m", blank=True, null=True)
    f = models.ForeignKey(K9, on_delete=models.CASCADE, related_name="f", blank=True, null=True)
    depth = models.IntegerField('depth',default=0) # family tree level
    zero = models.ForeignKey(K9, on_delete=models.CASCADE, related_name="zero", blank=True, null=True) #latest born

class K9_Handler(models.Model):
    handler = models.ForeignKey(User, on_delete=models.CASCADE, related_name= "handler", blank=True, null=True)
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE, related_name="k9", blank=True, null=True)
    deployment_area = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="deployment_area", blank=True, null=True)

    def __str__(self):
        # handler = User.objects.get(id=self.handler.id)
        # k9 = K9.objects.get(id=self.k9.id)
        # handler_name = str(handler)
        # k9_name = k9.name
        return str(self.handler.lastname) + " : " + str(self.k9.name)

#TODO save grade as 0 if grade input is 0
class Training(models.Model):
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE, blank=True, null=True)
    training = models.CharField('training', max_length=50, default="None")
    stage = models.CharField('stage', max_length=200, default="Stage 0")
    stage1_1 = models.CharField('stage1_1', blank=True, null=True, max_length=500, default="0")
    stage1_2 = models.CharField('stage1_2', blank=True, null=True, max_length=500, default="0")
    stage1_3 = models.CharField('stage1_3', blank=True, null=True, max_length=500, default="0")
    stage2_1 = models.CharField('stage2_1', blank=True, null=True, max_length=500, default="0")
    stage2_2 = models.CharField('stage2_2', blank=True, null=True, max_length=500, default="0")
    stage2_3 = models.CharField('stage2_3', blank=True, null=True, max_length=500, default="0")
    stage3_1 = models.CharField('stage3_1', blank=True, null=True, max_length=500, default="0")
    stage3_2 = models.CharField('stage3_2', blank=True, null=True, max_length=500, default="0")
    stage3_3 = models.CharField('stage3_3', blank=True, null=True, max_length=500, default="0")
    grade = models.CharField('grade', blank=True, null=True, max_length=500)
    remarks = models.CharField('remarks', max_length=500, blank=True, null=True)
    date_finished = models.DateField('date_finished', null=True, blank=True)

    def __str__(self):
        return str(self.k9) +' - ' + str(self.training) +' : ' + str(self.stage)
        

    def save(self, *args, **kwargs):

        average = Decimal(self.stage1_1) + Decimal(self.stage1_2) + Decimal(self.stage1_3) + Decimal(self.stage2_1) + Decimal(self.stage2_2) + Decimal(self.stage2_3) + Decimal(self.stage3_1) + Decimal(self.stage3_2) + Decimal(self.stage3_3)
        average = average/ Decimal(9)
        average = round(average, 1)
        self.grade = average

        if self.date_finished:
            stage = 'Finished Training'
        super(Training, self).save(*args, **kwargs)

class Training_History(models.Model):
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE)
    handler = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

class Training_Schedule(models.Model):
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE, blank=True, null=True)
    stage = models.CharField('stage', max_length=200, default="Stage 0")
    date_start = models.DateTimeField('date_start', null=True, blank=True)
    date_end = models.DateTimeField('date_end', null=True, blank=True)
    remarks = models.CharField('remarks', max_length=500, blank=True, null=True)

    def __str__(self):
        return str(self.k9) +'  - ' + str(self.stage)

class K9_Adopted_Owner(models.Model):
    SEX = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    k9 = models.ForeignKey(K9, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField('first_name', max_length=200)
    middle_name = models.CharField('middle_name', max_length=200)
    last_name = models.CharField('last_name', max_length=200)
    address = models.CharField('address', max_length=200)
    date_adopted = models.DateField('date_adopted', default=timezone.now)
    date_returned = models.DateField('date_returned', blank=True, null=True)
    reason = models.TextField('remarks', max_length=500, blank=True, null=True)
    file_adopt = models.FileField(upload_to='adoption_papers', blank=True, null=True)

    def __str__(self):
        return str(self.first_name) + ' ' + str(self.middle_name) + ' ' + str(self.last_name)
