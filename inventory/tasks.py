from __future__ import absolute_import, unicode_literals
from celery import shared_task, task
import time
from K9_insys.celery import app
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from datetime import timedelta, date, datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta

from inventory.models import Medicine_Subtracted_Trail, Medicine_Received_Trail, Medicine_Inventory, Medicine, Food_Subtracted_Trail, Food, Miscellaneous, Miscellaneous_Subtracted_Trail, Safety_Stock
from planningandacquiring.models import K9
from unitmanagement.models import Notification
from django.db.models import Sum

# TODO TEST
# All Dogs in PCGK9 base
# exclude: dead, deployed, adopted
# 6AM
# @periodic_task(run_every=crontab(hour=6, minute=0))
def auto_subtract():
    # TODO Vitamins consumption
    # vitamins = Medicine_Inventory.objects.filter(medicine__med_type='Vitamins').exclude(quantity=0).order_by('quantity')
    # v = K9.objects.filter(status='Working Dog').count()

    # for vitamins in vitamins:
    #     if v > 0:
    #         if v > vitamins.quantity:
    #             Medicine_Subtract_Trail.objects.create(inventory=vitamins, quantity=vitamins.quantity)
    #             v = v-vitamins.quantity
    #             vitamins.quantity = 0
    #             vitamins.save()
    #         else:
    #             Medicine_Subtract_Trail.objects.create(inventory=vitamins, quantity=v)
    #             vitamins.quantity = vitamins.quantity-v
    #             v=0
    #             vitamins.save()

    # FOOD CONSUMPTION EVERYDAY
    k9_labrador = K9.objects.filter(breed='Labrador Retriever').filter(age__gte=1).exclude(training_status='Deployed').exclude(status='Adopted').exclude(status='Stolen').exclude(status='Lost').exclude(status='Dead').count()
    k9_jack_russel = K9.objects.filter(breed='Jack Russel').filter(age__gte=1).exclude(training_status='Deployed').exclude(status='Adopted').exclude(status='Stolen').exclude(status='Lost').exclude(status='Dead').count()
    k9_others = K9.objects.filter(age__gte=1).exclude(breed='Labrador Retriever').exclude(breed='Jack Russel').exclude(training_status='Deployed').exclude(status='Adopted').exclude(status='Stolen').exclude(status='Lost').exclude(status='Dead').count()
    food = Food.objects.filter(foodtype='Adult Dog Food').filter(unit='kilograms').exclude(quantity=0).order_by('quantity')

    # dog_count * food_per_day
    lab = k9_labrador * 0.5
    jack = k9_jack_russel * 0.3
    oth = k9_others * 0.8
    total = lab+jack+oth
    t = Decimal(total)

    for food in food:
        if t > 0:
            if t > food.quantity:
                Food_Subtracted_Trail.objects.create(inventory=food, quantity=food.quantity)
                t = t-food.quantity
                food.quantity = 0
                food.save()
            else:
                Food_Subtracted_Trail.objects.create(inventory=food, quantity=t)
                food.quantity = food.quantity-t
                t=0
                food.save()

    # PUPPY FOOD CONSUMPTION
    # get puppy count by age
    third_fourth = K9.objects.filter(age_days__range=(21,28)).count() # 3rd-4th week : milk only
    fifth_sixth = K9.objects.filter(age_days__range=(29,42)).count() # 5th-6th week
    seventh_eight = K9.objects.filter(age_days__range=(43,57)).count() # 5th-6th week
    ninth_tenth = K9.objects.filter(age_days__range=(58,72)).count() # 9th-10th week
    eleventh_twelve = K9.objects.filter(age_days__range=(73,87)).count() # 11th-12th week

    four = K9.objects.filter(age_month=4).count() # 4 mos
    five = K9.objects.filter(age_month=5).count() # 5 mos
    six = K9.objects.filter(age_month=6).count() # 6 mos
    seven = K9.objects.filter(age_month=7).count() # 7 mos
    eight = K9.objects.filter(age_month=8).count() # 8 mos
    nine_twelve = K9.objects.filter(age_month__range=(9,12)).count() # 9-12 mos

    # get puppy milk per day consumption by age
    tf_milk = third_fourth * 32
    fs_milk = fifth_sixth * 48
    se_milk = seventh_eight * 48
    nt_milk = ninth_tenth * 60
    et_milk = eleventh_twelve * 72

    # get puppy food per day consumption by age
    fs_food = fifth_sixth * 0.08
    se_food = seventh_eight * 0.12
    nt_food = ninth_tenth * 0.18
    et_food = eleventh_twelve * 0.24
    four_food = four * 0.25
    five_food = five * 0.30
    six_food = six * 0.35
    seven_food = seven * 0.40
    eight_food = eight * 0.45
    nine_twelve_food = nine_twelve * 0.50

    milk = tf_milk + fs_milk + se_milk + nt_milk + et_milk
    food = fs_food + se_food + nt_food + et_food + four_food + five_food + six_food + seven_food + eight_food + nine_twelve_food

    query_milk = Food.objects.filter(foodtype='Milk').exclude(quantity=0).order_by('quantity')
    query_food = Food.objects.filter(foodtype='Puppy Dog Food').filter(unit='kilograms').exclude(quantity=0).order_by('quantity')

    t_food = Decimal(food)
    t_milk = Decimal(milk)

    # Subtract Milk
    for query_milk in query_milk:
        if t_milk > 0:
            if t_milk > query_milk.quantity:
                Food_Subtracted_Trail.objects.create(inventory=food, quantity=query_milk.quantity)
                t_milk = t_milk-query_milk.quantity
                query_milk.quantity = 0
                query_milk.save()
            else:
                Food_Subtracted_Trail.objects.create(inventory=food, quantity=t_milk)
                query_milk.quantity = query_milk.quantity-t_milk
                t_milk=0
                query_milk.save()

    # Subtract Puppy Food
    for query_food in query_food:
        if t_food > 0:
            if t_food > query_food.quantity:
                Food_Subtracted_Trail.objects.create(inventory=food, quantity=query_food.quantity)
                t_food = t_food-query_food.quantity
                query_food.quantity = 0
                query_food.save()
            else:
                Food_Subtracted_Trail.objects.create(inventory=food, quantity=t_food)
                query_food.quantity = query_food.quantity-t_food
                t_food=0
                query_food.save()


    # EXPIRATION OF MEDICINE
    med_receive = Medicine_Received_Trail.objects.filter(expiration_date=date.today())
    med_inventory = Medicine_Inventory.objects.all()
    for med in med_receive: #receive trail
        for m in med_inventory: #inventory
            if m.medicine == med.inventory.medicine:
                m.quantity = m.quantity - med.quantity
                m.save()

    # TODO Get Delivery Days
    # INVENTORY LOW NOTIFICATION
    delivery_days = 4
    day_adult = Decimal(total) * delivery_days
    day_puppy = Decimal(food) * delivery_days
    day_milk = Decimal(milk) * delivery_days

    try:
        stock = Safety_Stock.objects.get(id=1)
        stock.puppy_food = day_puppy
        stock.adult_food = day_adult
        stock.milk = milk
        stock.save()
    except (stock.DoesNotExist):
        pass

    adult_dfq = Food.objects.filter(foodtype='Adult Dog Food').filter(unit='kilograms').aggregate(sum=Sum('quantity'))['sum']
    puppy_dfq = Food.objects.filter(foodtype='Puppy Dog Food').filter(unit='kilograms').aggregate(sum=Sum('quantity'))['sum']
    milk_q = Food.objects.filter(foodtype='Milk').filter(unit='kilograms').aggregate(sum=Sum('quantity'))['sum']

    if adult_dfq <= day_adult:
        Notification.objects.create(message= 'Adult Dog Food is low. Its time to reorder!', notif_type='inventory_low')
    if puppy_dfq <= day_puppy:
        Notification.objects.create(message= 'Puppy Dog Food is low. Its time to reorder!', notif_type='inventory_low')
    if milk_q <= day_milk:
        Notification.objects.create(message= 'Milk is low. Its time to reorder!', notif_type='inventory_low')
