from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, inlineformset_factory
from django.db.models import aggregates
from django.contrib import messages

from django.db.models import Count, Sum, Q, F
from django.views import generic
from django.utils.safestring import mark_safe
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from dateutil.relativedelta import relativedelta
from pandas import DataFrame as df
import pandas as pd

import datetime
import re
import sys
from datetime import date

from unitmanagement.models import Notification, Request_Transfer, Handler_On_Leave, VaccinceRecord,Call_Back_K9
from training.models import K9_Handler
from planningandacquiring.models import K9
from profiles.models import Personal_Info, User, Account, Education
from inventory.models import Medicine, Miscellaneous, Food, Medicine_Inventory, Medicine_Received_Trail, Miscellaneous_Received_Trail, Food_Received_Trail

from deployment.forms import AreaForm, LocationForm, AssignTeamForm, EditTeamForm, RequestForm, IncidentForm, GeoForm, MonthYearForm, GeoSearch, DateForm, DailyRefresherForm, ScheduleUnitsForm, DeploymentDateForm
from deployment.models import Area, Location, Team_Assignment, Team_Dog_Deployed, Dog_Request, K9_Schedule, Incidents, Daily_Refresher, Maritime, TempDeployment,K9_Pre_Deployment_Items
from django.core.exceptions import MultipleObjectsReturned

from training.models import Training_Schedule, Training

from pyproj import Proj, transform

from faker import Faker
import random

#GeoDjango
from math import sin, cos, radians, degrees, acos
import math
import ast
from decimal import *

import datetime
from datetime import timedelta, date

from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.utils.safestring import mark_safe

from deployment.util import Calendar, get_date, prev_month, next_month, select_month, Calendar_Detailed
from collections import OrderedDict
import json

from deployment.templatetags import index as deployment_template_tags


# from profiles.populate_db import generate_user, generate_k9, generate_event, generate_incident, generate_maritime, \
#     generate_area, generate_location, generate_training, assign_commander_random, fix_dog_duplicates, generate_dogbreed\
#     , create_predeployment_inventory, generate_k9_posttraining_decision, generate_k9_deployment

#GENERATE DB 2
from profiles.populated_db_2 import create_predeployment_inventory, generate_user, create_teams, generate_k9, \
    generate_requests, generate_dogbreed, generate_inventory_trail,generate_daily_refresher, \
    generate_location_incident, generate_handler_incident, generate_handler_leave, generate_k9_incident, \
    generate_health_record, generate_k9_parents, generate_k9_due_retire, generate_sick_breeding, \
    generate_adoption, create_supplier, generate_grading, generate_item_request, generate_maritime, fix_dog_duplicates

import random

from deployment.tasks import assign_TL

from functools import partial, wraps


class MyDictionary(dict):

    # __init__ function
    def __init__(self):
        self = dict()

        # Function to add key:value

    def add(self, key, value):
        self[key] = value

def notif(request):
    serial = request.session['session_serial']
    account = Account.objects.filter(serial_number=serial).last()
    user_in_session = User.objects.filter(id=account.UserID.id).last()

    if user_in_session.position == 'Veterinarian':
        notif = Notification.objects.filter(position='Veterinarian').order_by('-datetime')
    elif user_in_session.position == 'Handler':
        notif = Notification.objects.filter(user=user_in_session).order_by('-datetime')
    else:
        notif = Notification.objects.filter(position='Administrator').order_by('-datetime')

    return notif


def user_session(request):
    serial = request.session['session_serial']
    account = Account.objects.filter(serial_number=serial).last()
    user_in_session = User.objects.filter(id=account.UserID.id).last()
    return user_in_session

def index(request):
    d = Daily_Refresher.objects.filter(id=4).last()
    # CAUTION : Only run this once
    #Only uncomment this if you are populating db
    context = {
      'title':'Deployment',
      'd':d,
    }
    return render (request, 'deployment/index.html', context)

def pre_req_unconfirmed(request):
    user = user_session(request)
    #K9 schedule
    #pre-req items
    #K9_Schedule
    kdi = K9_Pre_Deployment_Items.objects.filter(status='Pending').exclude(initial_sched__date_end__lt=datetime.date.today())

    count = 0
    for kp in kdi:
        date = kp.initial_sched.date_start - relativedelta(days=5)
        if datetime.date.today() >= date:
            count = count+1

    collar = Miscellaneous.objects.filter(miscellaneous__contains="Collar").aggregate(sum=Sum('quantity'))['sum'] - count
    vest = Miscellaneous.objects.filter(miscellaneous__contains="Vest").aggregate(sum=Sum('quantity'))['sum'] - count
    leash = Miscellaneous.objects.filter(miscellaneous__contains="Leash").aggregate(sum=Sum('quantity'))['sum'] - count
    shipping_crate = Miscellaneous.objects.filter(miscellaneous__contains="Shipping Crate").aggregate(sum=Sum('quantity'))['sum'] - count
    food = Food.objects.filter(foodtype="Adult Dog Food").aggregate(sum=Sum('quantity'))['sum']
    medicines = Medicine_Inventory.objects.filter(medicine__med_type="Vitamins").aggregate(sum=Sum('quantity'))['sum'] - count
    grooming_kit = Miscellaneous.objects.filter(miscellaneous__contains="Grooming Kit").aggregate(sum=Sum('quantity'))['sum'] - count
    first_aid_kit = Miscellaneous.objects.filter(miscellaneous__contains="First Aid Kit").aggregate(sum=Sum('quantity'))['sum'] - count
    oral_dextrose = Miscellaneous.objects.filter(miscellaneous__contains="Oral Dextrose").aggregate(sum=Sum('quantity'))['sum'] - count
    ball = Miscellaneous.objects.filter(miscellaneous__contains="Ball").aggregate(sum=Sum('quantity'))['sum'] - count

    item_list = []
    if collar < 0:
        a = abs(collar)
        b = ['Collar',a]
        item_list.append(b)
    if vest < 0:
        a = abs(vest)
        b = ['Vest',a]
        item_list.append(b)
    if leash < 0:
        a = abs(leash)
        b = ['Leash',a]
        item_list.append(b)
    if shipping_crate < 0:
        a = abs(shipping_crate)
        b = ['Shipping Crate',a]
        item_list.append(b)
    if food < 0:
        a = abs(food)
        b = ['Food',a]
        item_list.append(b)
    if medicines < 0:
        a = abs(medicines)
        b = ['Vitamins',a]
        item_list.append(b)
    if grooming_kit < 0:
        a = abs(grooming_kit)
        b = ['Grooming Kit',a]
        item_list.append(b)
    if first_aid_kit < 0:
        a = abs(first_aid_kit)
        b = ['First Aid Kit',a]
        item_list.append(b)
    if oral_dextrose < 0:
        a = abs(oral_dextrose)
        b = ['Oral Dextrose',a]
        item_list.append(b)
    if ball < 0:
        a = abs(ball)
        b = ['Ball',a]
        item_list.append(b)

    if request.method == 'POST':
        item_type = request.POST.get('item_type')
        select = request.POST.get('select')
        quantity = int(request.POST.get('quantity'))
        date = request.POST.get('date')

        if item_type == 'Vitamins':
            mi = Medicine_Inventory.objects.get(id=select)
            mi.quantity = mi.quantity + quantity
            mi.save()
            Medicine_Received_Trail.objects.create(inventory=mi, user=user, expiration_date=date, quantity = quantity)
            messages.success(request, 'You have added '+ str(quantity) + ' to ' + str(mi) + '.')
        elif item_type == 'Adult Dog Food':
            fi = Food.objects.get(id=select)
            fi.quantity = fi.quantity + quantity
            fi.save()
            Food_Received_Trail.objects.create(inventory=fi, user=user, quantity = quantity)
            messages.success(request, 'You have added '+ str(quantity) + ' to ' + str(fi) + '.')
        else:
            misc = Miscellaneous.objects.get(id=select)
            misc.quantity = misc.quantity + quantity
            misc.save()
            Miscellaneous_Received_Trail.objects.create(inventory=misc, user=user, quantity = quantity)
            messages.success(request, 'You have added '+ str(quantity) + ' to ' + str(misc) + '.')

        return redirect('deployment:pre_req_unconfirmed')


    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()

    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'item_list':item_list,
    }
    return render (request, 'deployment/pre_req_unconfirmed.html', context)

def load_pre_req(request):

    item_type = None

    try:
        item_type = request.GET.get('item_type')
        if item_type == 'Collar':
            data =  Miscellaneous.objects.filter(miscellaneous__contains="Collar")
        elif item_type == 'Vest':
            data =  Miscellaneous.objects.filter(miscellaneous__contains="Vest")
        elif item_type == 'Leash':
            data =  Miscellaneous.objects.filter(miscellaneous__contains="Leash")
        elif item_type == 'Shipping Crate':
            data =  Miscellaneous.objects.filter(miscellaneous__contains="Shipping Crate")
        elif item_type == 'Adult Dog Food':
            data = Food.objects.filter(foodtype="Adult Dog Food")
        elif item_type == 'Vitamins':
            data = Medicine_Inventory.objects.filter(medicine__med_type="Vitamins")
        elif item_type == 'Grooming Kit':
            data =  Miscellaneous.objects.filter(miscellaneous__contains="Grooming Kit")
        elif item_type == 'First Aid Kit':
            data =  Miscellaneous.objects.filter(miscellaneous__contains="First Aid Kit")
        elif item_type == 'Oral Dextrose':
            data =  Miscellaneous.objects.filter(miscellaneous__contains="Oral Dextrose")
        elif item_type == 'Ball':
            data =  Miscellaneous.objects.filter(miscellaneous__contains="Ball")
    except:
        pass

    context = {
        'item_type': item_type,
        'data': data,
    }

    return render(request, 'deployment/pre_req_data.html', context)


# def mass_populate():
#     # Generate all models related to a users, k9s and k9_requests (edit loop count in populate_db.py to change number of created objects
#     generate_user() #generates 400 objects
#     generate_k9() #generates 300 objects
#     generate_area() # generate all regions
#     generate_location() # generate a location per city
#     generate_event() #generates 150 objects
#     generate_incident() #generates 250 objects
#     generate_maritime() # generates 500 objects
#
#     # >>advanced
#     generate_training() #Classify k9s
#     generate_k9_posttraining_decision() # For-Breeding or For-Deployment
#     generate_k9_deployment() # Randomly assign to ports
#
#     # >>fixes
#     generate_dogbreed()
#     assign_commander_random() #Assign commanders to areas
#     fix_dog_duplicates() # fix duplicate names for dogs
#     create_predeployment_inventory() #Inventory items for pre deployment
#
#     return None

# Find handlerss with multiple k9s
def check_handlers_with_multiple_k9s():

    mult_k9 = []
    users = User.objects.all()
    for user in users:
        k9_count = K9.objects.filter(handler=user).count()
        if k9_count > 1:
            mult_k9.append((user, k9_count))

    # for item in mult_k9:
    #     print(item)
    return None

def mass_populate_revisited():
    # GENERAL & DEPLOYMENT
    create_supplier()
    generate_dogbreed()
    
    generate_user()
    create_teams()
    generate_maritime()
    generate_k9()
    
    create_predeployment_inventory()
    generate_inventory_trail()
    
    generate_k9_parents()
    generate_requests()
    
    generate_sick_breeding()
    generate_adoption()
    generate_health_record()
    generate_grading()
    generate_k9_incident()
    generate_handler_leave()
    generate_handler_incident()
    generate_location_incident()
    generate_daily_refresher()
    
    fix_dog_duplicates()
    generate_k9_due_retire()

    #PRINT
    '''
    1 Admin 
    1 Team Leader
    1 Vet
    1 Trainer
    3 Handler with k9

    '''

    #TEST HERE
    
   
    #Handler with k9
    handler = User.objects.filter(position="Handler").filter(assigned=True).filter(partnered=True)

    for i in range(3):
        choice =  random.choice(handler)
        k9 = K9.objects.get(handler=choice)
        print('Handler with K9 - ',choice.id, choice, k9)


    #Team Leader
    tl = Team_Assignment.objects.exclude(team_leader=None)
    leader =  random.choice(tl)
    print('Leader - ', leader.team_leader.id ,leader)

    #Admin
    admin = User.objects.filter(position="Administrator")
    admin =  random.choice(admin)
    print('Admin - ',admin.id ,admin)
    
    #Veterinarian
    vet = User.objects.filter(position="Veterinarian")
    vet =  random.choice(vet)
    print('Vet - ',vet.id ,vet)

    #Trainer
    trainer = User.objects.filter(position="Trainer")
    trainer =  random.choice(trainer)
    print('Trainer - ',trainer.id ,trainer)

    #K9 Due for retirement
    retire = K9.objects.filter(status='Due-For-Retirement').filter(training_status='Deployed')
    for r in retire:
        print("DUE to retire - ", r, r.handler.id, r.handler)
        

    #K9 to be mated dates of notif show 
    print("Date confirm pregnancy: ", date.today() + timedelta(days=22))
    print("Date add litter: ", date.today()  + timedelta(days=63))

    return None

def add_area(request):

    mass_populate_revisited()

    form = AreaForm(request.POST or None)
    style = ""
    area = None
    if request.method == 'POST':
        if form.is_valid():
            area = form.save()
            style = "ui green message"
            messages.success(request, 'Area has been successfully Added!')

        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
      'title':'Add Area Form',
      'texthelp': 'Input Name of Area Here',
      'form': form,
      'actiontype': 'Submit',
      'style':style,
      'notif_data':notif_data,
      'count':count,
      'user':user,
    }
    return render (request, 'deployment/add_area.html', context)

def add_location(request):
    form = LocationForm(request.POST or None)

    geoform = GeoForm(request.POST or None)
    geosearch = GeoSearch(request.POST or None)
    width = 470
    style = ""

    if request.method == 'POST':
        # print(form.errors)
        if form.is_valid() and geoform.is_valid():
            location = form.save()

            team = Team_Assignment.objects.create(location = location)
            team.save()

            checks = geoform['point'].value()
            checked = ast.literal_eval(checks)
            # print(checked['coordinates'])
            toList = list(checked['coordinates'])
            # print(toList)
            lon = Decimal(toList[0])
            lat = Decimal(toList[1])
            # print("LONGTITUDE")
            # print(lon)
            # print("LATITUDE")
            # print(lat)
            location.longtitude = lon
            location.latitude = lat
            location.save()

            style = "ui green message"
            messages.success(request, 'Location has been successfully Added!')
            form = LocationForm()
        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
      'title':'Add Location Form',
      'texthelp': 'Input Location Details Here',
      'form': form,
      'geoform': geoform,
      'geosearch': geosearch,
       'width' :width,

      'actiontype': 'Submit',
      'style':style,
      'notif_data':notif_data,
      'count':count,
      'user':user,

    }
    return render (request, 'deployment/add_location.html', context)


def load_locations(request):

    search_query = request.GET.get('search_query')
    width = request.GET.get('width')


    if search_query == "":
        geolocator = Nominatim(user_agent="Locator", timeout=None)
    else:
        geolocator = Nominatim(user_agent="Locator", format_string="%s, Philippines", timeout=None)

    locations = geolocator.geocode(search_query, exactly_one=False)

    # print(locations)

    context = {
        'locations' : locations,
        'width': width
    }

    return render(request, 'deployment/location_data.html', context)

def load_map(request):
    lng = request.GET.get('lng')
    lat = request.GET.get('lat')

    width = request.GET.get('width')

    # print("TEST coordinates")
    # print(str(lat) + " , " + str(lng))

    geoform = GeoForm(request.POST or None, lat=lat, lng=lng, width=width)

    context = {
        'geoform' : geoform
    }

    return render(request, 'deployment/map_data.html', context)

def assign_team_location(request):
    form = AssignTeamForm(request.POST or None)
    style = ""

    if request.method == 'POST':
        if form.is_valid():
            f = form.save(commit=False)
            f.team_leader.assigned=True
            f.location.status='assigned'
            f.save()

            #Location
            l=Location.objects.get(id=f.location.id)
            l.status = 'assigned'

            #Team Leader
            u = User.objects.get(id=f.team_leader.id)
            u.assigned = True

            l.save()
            u.save()

            style = "ui green message"
            return redirect('deployment:assigned_location_list')
        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
      'title':'Assign Team to Location',
      'texthelp': 'Input Team and Location Details Here',
      'form': form,
      'actiontype': 'Submit',
      'style':style,
      'notif_data':notif_data,
      'count':count,
      'user':user,
    }
    return render (request, 'deployment/assign_team_location.html', context)

def edit_team(request, id):
    data = Team_Assignment.objects.get(id=id)
    form = EditTeamForm(request.POST or None, instance = data)
    style = ""
    if request.method == 'POST':
        if form.is_valid():
            data.team = request.POST.get('team')
            data.EDD_demand = request.POST.get('EDD_demand')
            data.NDD_demand = request.POST.get('NDD_demand')
            data.SAR_demand = request.POST.get('SAR_demand')
            data.save()
            style = "ui green message"
            messages.success(request, 'Team Details has been successfully Updated !')
        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
      'title': data.team,
      'texthelp': 'Edit Team Details Here',
      'form': form,
      'data': data,
      'actiontype': 'Submit',
      'style':style,
      'notif_data':notif_data,
      'count':count,
      'user':user,
    }
    return render(request, 'deployment/edit_team.html', context)

def assigned_location_list(request):
    data = Team_Assignment.objects.all()

    user = user_session(request)
    date_now = datetime.date.today()

    # print(user)
    # print(user.position)

    if user.position == "Commander":
        areas = Area.objects.filter(commander=user)
        locations = Location.objects.filter(area__in = areas)
        data = data.filter(location__in=locations)

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title' : 'K9s and Handlers Assigned Field Officer Units',
        'data' : data,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }

    return render(request, 'deployment/assigned_location_list.html', context)

#NOTE You cannot deploy k9s in this view anymore
def team_location_details(request, id):
    data = Team_Assignment.objects.get(id=id)
    # print(data.id)
    incidents = Incidents.objects.filter(location = data.location)
    edd_inc = Incidents.objects.filter(location = data.location).filter(type = "Explosives Related").count()
    ndd_inc = Incidents.objects.filter(location=data.location).filter(type="Narcotics Related").count()
    sar_inc = Incidents.objects.filter(location=data.location).filter(type="Search and Rescue Related").count()
    style = ""

    #filter personal_info where city != Team_Assignment.city
    handlers = Personal_Info.objects.exclude(city=data.location.city)

    user_deploy = []
    for h in handlers:
    #    print(h)
       user_deploy.append(h.UserID)

    # #filter K9 where handler = person_info and k9 assignment = None
    can_deploy = K9.objects.filter(handler__in=user_deploy).filter(training_status='For-Deployment')
    dogs_deployed = Team_Dog_Deployed.objects.filter(team_assignment=data).filter(status='Deployed').filter(date_pulled = None).exclude(k9__handler = None)
    dogs_pulled = Team_Dog_Deployed.objects.filter(team_assignment=data).exclude(date_pulled = None)#.filter(status='Pulled-Out')

    tl_dog = None
    for tdd in dogs_deployed:
        if tdd.k9.handler.position == "Team Leader":
            tl_dog = tdd.k9
    if tl_dog is not None:
        dogs_deployed = dogs_deployed.exclude(k9 = tl_dog)

    if request.method == 'POST':
        checks =  request.POST.getlist('checks') # get the id of all the dogs checked
        #print(checks)

        #get the k9 instance of checked dogs
        checked_dogs = K9.objects.filter(id__in=checks)
        #print(checked_dogs)

        for checked_dogs in checked_dogs:
            Team_Dog_Deployed.objects.create(team_assignment=data, k9=checked_dogs) # date = team_assignment
            # TODO: if dog is equal capability increment
            if checked_dogs.capability == 'EDD':
                data.EDD_deployed = data.EDD_deployed + 1
            elif checked_dogs.capability == 'NDD':
                data.NDD_deployed = data.NDD_deployed + 1
            else:
                data.SAR_deployed = data.SAR_deployed + 1

            data.save()
            dog = K9.objects.get(id=checked_dogs.id)
            dog.assignment = str(data)
            dog.save()

        messages.success(request, 'Dogs has been successfully Deployed!')

        return redirect('deployment:team_location_details', id = id)

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title' : data,
        'data' : data,
        'style': style,
        'can_deploy':can_deploy,
        'dogs_deployed':dogs_deployed,
        'dogs_pulled': dogs_pulled,
        'sar_inc': sar_inc,
        'ndd_inc': ndd_inc,
        'edd_inc': edd_inc,
        'notif_data':notif_data,
        'count':count,
        'user':user,

        'tl_dog' : tl_dog
    }

    return render(request, 'deployment/team_location_details.html', context)

def remove_dog_deployed(request, id):
    pull_k9 = Team_Dog_Deployed.objects.get(id=id)
    k9 = K9.objects.get(id=pull_k9.k9.id)
    team_assignment = Team_Assignment.objects.get(id=pull_k9.team_assignment.id)

    #change Team_Dog_Deployed model
    pull_k9.status = 'Pulled-Out'
    pull_k9.date_pulled = datetime.date.today()
    pull_k9.save()

    #change K9 model
    k9.assignment = 'None'
    k9.save()

    #change Team_Assignment model
    if pull_k9.k9.capability == 'EDD':
         team_assignment.EDD_deployed  = team_assignment.EDD_deployed - 1
    elif pull_k9.k9.capability == 'NDD':
        team_assignment.NDD_deployed = team_assignment.NDD_deployed - 1
    elif pull_k9.k9.capability == 'SAR':
        team_assignment.SAR_deployed = team_assignment.SAR_deployed - 1
    else:
        pass
    team_assignment.save()

    messages.success(request, 'Dogs has been successfully Pulled!')

    return redirect('deployment:team_location_details', id=pull_k9.team_assignment.id)

def dog_request(request):

    form = RequestForm(request.POST or None)

    geoform = GeoForm(request.POST or None)
    geosearch = GeoSearch(request.POST or None)
    width = 470

    style = ""

    if request.method == 'POST':
        # print(form.errors)
        form.validate_date()
        if form.is_valid():

            cd = form.cleaned_data['phone_number']
            regex = re.compile('[^0-9]')
            form.phone_number = regex.sub('', cd)

            location = form.save() #instance of form

            checks = geoform['point'].value()
            checked = ast.literal_eval(checks)
            # print(checked['coordinates'])
            toList = list(checked['coordinates'])
            # print(toList)
            lon = Decimal(toList[0])
            lat = Decimal(toList[1])
            # print("LONGTITUDE")
            # print(lon)
            # print("LATITUDE")
            # print(lat)
            location.longtitude = lon
            location.latitude = lat

            serial = request.session['session_serial']
            account = Account.objects.get(serial_number=serial)
            user_in_session = User.objects.get(id=account.UserID.id)


            if location.sector_type != "Disaster": #TODO, wala pa process for disasters
                if user_in_session.position == 'Operations' or  user_in_session.position == 'Administrator':
                    location.sector_type = "Big Event"
                    location.status = "Approved"
                else:
                    location.sector_type = "Small Event"


            location.save()

            style = "ui green message"
            messages.success(request, 'Request has been successfully Added!')
            form = RequestForm()
        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
      'title':'K9 Request Form',
      'texthelp': 'Input Location Details Here',
      'form': form,

      'geoform': geoform,
      'geosearch': geosearch,
       'width' :width,

      'actiontype': 'Submit',
      'style':style,
      'notif_data':notif_data,
      'count':count,
      'user':user,

    }
    return render (request, 'deployment/request_form.html', context)


def request_dog_list(request):
    data = Dog_Request.objects.all().order_by('start_date')
    user = user_session(request)
    date_now = datetime.date.today()

    # print(user)
    # print(user.position)

    if user.position == "Commander":
        areas = Area.objects.filter(commander = user).last()
        print(areas)
        data = data.filter(area=areas).filter(sector_type = "Small Event")
        print("A COMMANDER")
    else:
        data = data.filter(sector_type="Big Event")
        print("NOT A COMMANDER")

    data1 = data.filter(status='Pending').exclude(start_date__lte = datetime.date.today())
    data2 = data.filter(status='Approved').exclude(k9s_deployed__gte = F('k9s_needed')).exclude(start_date__lte = datetime.date.today())
    data3 = data.filter(status='Approved').filter(k9s_deployed__gte = F('k9s_needed')).exclude(start_date__lte = datetime.date.today())

    # latest_date = Dog_Request.objects.latest('end_date')
    # latest_date = latest_date.end_date
    # k9_schedule = Dog_Request.objects.filter(end_date__range=[str(date_now), str(latest_date)])

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'data': data,
        'title': 'Request Dog List',
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'data1':data1,
        'data2':data2,
        'data3' : data3
    }
    return render (request, 'deployment/request_dog_list.html', context)

def request_dog_details(request, id):
    data2 = Dog_Request.objects.get(id=id)
    in_the_past = False
    if datetime.datetime.today().date() >= data2.start_date:
        in_the_past = True

    # print("IN THE PAST")
    # print(in_the_past)
    '''data = Team_Assignment.objects.get(id=id)'''
    #k9 = Team_Dog_Deployed.objects.filter(team_requested=data2)
    style = ""
    # filter personal_info where city != Team_Assignment.city
    handlers = Personal_Info.objects.exclude(city=data2.city)

    handler_can_deploy = []  # append the id of the handlers
    for h in handlers:
        handler_can_deploy.append(h.UserID.id)
    # print(handler_can_deploy)

    # get instance of user using personal_info.id
    # id of user is the fk.id of person_info
    user = User.objects.filter(id__in=handler_can_deploy).exclude(position = "Team Leader").exclude(status = "Emergency Leave").exclude(status = "On-Leave").exclude(status = 'No Longer Employed').exclude(status = 'Retired').exclude(status ='Died').exclude(status ='MIA')

    user_deploy = []  # append the user itself
    for u in user:
        user_deploy.append(u.id)

    # print("Viable User Ids")
    # print(user_deploy)
    # #filter K9 where handler = person_info and k9 assignment = None
    can_deploy = K9.objects.filter(handler__id__in=user_deploy).filter(training_status='Deployed').filter(status = 'Working Dog')
        # .filter(assignment='None')

    # print("can_deploy_by_handler")
    # print(can_deploy)

    # dogs deployed to Dog Request
    # Don't need to filter data2.status == "Approved" since wala rin naman k9_schedule if naka pending pa yung request
    dogs_deployed = K9_Schedule.objects.filter(dog_request=data2) #.filter(status='Request') (unnecessary filter)

    sar_deployed = 0
    ndd_deployed = 0
    edd_deployed = 0

    TL_candidates = []

    for item in dogs_deployed:
        if item.k9.capability == "SAR":
            sar_deployed += 1
        elif item.k9.capability == "NDD":
            ndd_deployed += 1
        else:
            edd_deployed += 1

        TL_candidates.append(item.k9.handler)

    #TODO

    # print("TL Candidates")
    # print(TL_candidates)
    TL = None
    if len(TL_candidates) >= 1:
        TL = assign_TL(None, handler_list_arg=TL_candidates)

        if not (datetime.datetime.today().date() >= data2.start_date and datetime.datetime.today().date() <= data2.end_date):
            TL.position = "Handler"
            TL.save()

        data2.team_leader = TL
        data2.save()

    #TODO Find issue where handler has multiple k9s
    tl_dog = None
    try:
        if TL is not None:
            tl_dog = K9.objects.get(handler = TL)
            dogs_deployed = dogs_deployed.exclude(k9 = tl_dog)
    except: pass

    #>>>> start of new Code for saving schedules instead of direct deployment
    # TODO Filter can deploy to with teams without date conflicts
    can_deploy_filtered = []
    for k9 in can_deploy:
        #1 = true, 0 = false
        deployable = 1
        schedules = K9_Schedule.objects.filter(k9=k9).filter(status ="Request").filter(date_start__gte = data2.start_date)
        transfer_requests = Request_Transfer.objects.filter(handler = k9.handler).filter(date_of_transfer__gte = data2.start_date)
        leaves = Handler_On_Leave.objects.filter(handler = k9.handler).filter(date_from__gte = data2.start_date)

        #TODO obtain schedule of request then compare to start and end date of schedules (loop)
        for sched in schedules:
            if (sched.date_start >= data2.start_date and sched.date_start <= data2.end_date) \
                    or (sched.date_end >= data2.start_date and sched.date_end <= data2.end_date) \
                    or (data2.start_date >= sched.date_start and data2.start_date <= sched.date_end) \
                    or (data2.end_date >= sched.date_start and data2.end_date <= sched.date_end):
                deployable = 0

        for transfer in transfer_requests: #Checks if may conflict with transfer requests
            date_of_transfer = transfer.date_of_transfer
            if date_of_transfer >= data2.start_date and date_of_transfer <= data2.end_date:
                deployable = 0

        for leave in leaves:
            if (leave.date_from >= data2.start_date and leave.date_from <= data2.end_date) \
                    or (leave.date_to >= data2.start_date and leave.date_to <= data2.end_date) \
                    or (data2.start_date >= leave.date_from and data2.start_date <= leave.date_to) \
                    or (data2.end_date >= leave.date_from and data2.end_date <= leave.date_to):
                deployable = 0

        if deployable == 1 and deployment_template_tags.current_location(k9, data2.id) != "PCGK9 Taguig Base": #checks if K9's current location is at a port
            can_deploy_filtered.append(k9.id)

    can_deploy2 =  K9.objects.filter(id__in = can_deploy_filtered) #Trained and Assigned dogs without date conflicts TODO Remove K9s that have not yet been deployed to a port
    #TODO If a dog is deployed to a request, the dog will only be deployed if system datetime is same as scheduled request.
    #>>Also, dog deployment means scheduling first

    can_deploy = can_deploy2
    # print("can_deploy_no_conflict")
    # print(can_deploy)

    #K9s that are within AOR of request
    k9s_within_AOR = []
    if data2.sector_type == "Small Event":
        AOR = data2.area
        for k9 in can_deploy:
            location = deployment_template_tags.current_location(k9, data2.id)
            if location  != "PCGK9 Taguig Base":
                if location.area == AOR:
                    k9s_within_AOR.append(k9.id)

    #TODO Combine df of within AOR and ouside AOR if event is small

    can_deploy_list = []
    maritime_count_list = []
    incident_count_list = [] #Note: only related to skill
    distance_list = [] #distance of current location to request
    location_list =[]
    area_list = []

    #Note that can_deploy is same as usual if event is Big
    if data2.sector_type == "Small Event":
        can_deploy_inside_AOR = can_deploy.filter(pk__in = k9s_within_AOR)
        can_deploy_outside_AOR = can_deploy.exclude(pk__in = k9s_within_AOR)

        can_deploy = can_deploy_inside_AOR #TODO as of this code, only units within AOR if Small Event

    for k9 in can_deploy:
        can_deploy_list.append(k9)
        maritime_count = 0
        incident_count = 0

        try:
            team_dog_deployed = Team_Dog_Deployed.objects.filter(k9=k9, status="Deployed").last()
            if (team_dog_deployed.date_pulled is None):
                team_assignment_id = team_dog_deployed.team_assignment.id
                team_assignment = Team_Assignment.objects.get(id=team_assignment_id)
                location = team_assignment.location
                location_list.append(location)
                area_list.append(location.area)

                maritime_count = Maritime.objects.filter(location=location).count()
                maritime_count_list.append(maritime_count)

                if k9.capability == "SAR":
                    incident_count = Incidents.objects.filter(location=location).filter(
                        type="Search and Rescue Related").count()

                if k9.capability == "NDD":
                    incident_count = Incidents.objects.filter(location=location).filter(
                        type="Narcotics Related").count()
                else:
                    incident_count = Incidents.objects.filter(location=location).filter(
                        type="Explosives Related").count()
                incident_count_list.append(incident_count)

        except:
            location_list.append("PCGK9 Taguig Base")
            area_list.append("National Capital Region")
            maritime_count_list.append(int(0))
            incident_count_list.append(int(0))


        distance = deployment_template_tags.calculate_distance_from_current(k9, data2.id)
        distance_list.append(distance)

    df_data = {
        "K9" : can_deploy_list,
        "Location" : location_list,
        "Area" : area_list,
        "Distance" : distance_list,
        "Maritime" : maritime_count_list,
        "Incident" : incident_count_list,
    }

    #TODO Find a way to somehow put all within AOR on top first for Small Events, otherwise create a seperate dataframe
    can_deploy_dataframe = df(data=df_data)
    can_deploy_dataframe.sort_values(by=["Distance", "Maritime", "Incident"],
                                   ascending=[True, True, True], inplace=True)

    if data2.sector_type == "Small Event":
        for k9 in can_deploy_outside_AOR:
            can_deploy_list.append(k9)
            maritime_count = 0
            incident_count = 0

            try:
                team_dog_deployed = Team_Dog_Deployed.objects.filter(k9=k9, status="Deployed").last()
                if (team_dog_deployed.date_pulled is None):
                    team_assignment_id = team_dog_deployed.team_assignment.id
                    team_assignment = Team_Assignment.objects.get(id=team_assignment_id)
                    location = team_assignment.location
                    location_list.append(location)
                    area_list.append(location.area)

                    maritime_count = Maritime.objects.filter(location=location).count()
                    maritime_count_list.append(maritime_count)

                    if k9.capability == "SAR":
                        incident_count = Incidents.objects.filter(location=location).filter(
                            type="Search and Rescue Related").count()

                    if k9.capability == "NDD":
                        incident_count = Incidents.objects.filter(location=location).filter(
                            type="Narcotics Related").count()
                    else:
                        incident_count = Incidents.objects.filter(location=location).filter(
                            type="Explosives Related").count()
                    incident_count_list.append(incident_count)

            except:
                location_list.append("PCGK9 Taguig Base")
                area_list.append("National Capital Region")
                maritime_count_list.append(int(0))
                incident_count_list.append(int(0))

            distance = deployment_template_tags.calculate_distance_from_current(k9, data2.id)
            distance_list.append(distance)

        df_data = {
            "K9": can_deploy_list,
            "Location": location_list,
            "Area": area_list,
            "Distance": distance_list,
            "Maritime": maritime_count_list,
            "Incident": incident_count_list,
        }


        can_deploy_outside_AOR_dataframe = df(data=df_data)
        can_deploy_outside_AOR_dataframe.sort_values(by=["Distance", "Maritime", "Incident"],
                                         ascending=[True, True, True], inplace=True)

        can_deploy_dataframe = pd.concat([can_deploy_dataframe, can_deploy_outside_AOR_dataframe])#Puts within AOR on top first
        can_deploy_dataframe.reset_index(drop=True, inplace=True)

    if request.method == 'POST':
        if 'approve' in request.POST:
            data2.remarks = request.POST.get('remarks')
            data2.status = "Approved"
            data2.save()
            return redirect('deployment:request_dog_details', id=id)
        elif 'deny' in request.POST:
            data2.remarks = request.POST.get('remarks')
            data2.status = "Denied"
            data2.save()
            return redirect('deployment:request_dog_details', id=id)

        checks = request.POST.getlist('checks')  # get the id of all the dogs checked
        # print("Checked Dogs")
        # print(checks)

        # get the k9 instance of checked dogs
        checked_dogs = K9.objects.filter(id__in=checks)
        # print(checked_dogs)

        for dog in checked_dogs:
            # TODO Only save k9.assignment when system datetime is same as request
            # TODO Don't create Team_Dog_Deployed if hindi pa officially "Deployed"
            # Team_Dog_Deployed.objects.create(team_requested=data2, k9=checked_dogs, status="Scheduled", handler = str(k9.handler.fullname))

            K9_Schedule.objects.create(k9 = dog, dog_request = data2, date_start = data2.start_date, date_end = data2.end_date, status = "Request")

            Notification.objects.create(position='Handler', user=dog.handler, notif_type='handler_request_scheduled',
                                        message="Your have an upcoming K9 request on " + str(
                                            data2.start_date) + ". Be there!")

            #
            # if checked_dogs.capability == 'EDD':
            #     data2.EDD_deployed = data2.EDD_deployed + 1
            # elif checked_dogs.capability == 'NDD':
            #     data2.NDD_deployed = data2.NDD_deployed + 1
            # else:
            #     data2.SAR_deployed = data2.SAR_deployed + 1

            data2.k9s_deployed =  data2.k9s_deployed + 1
            data2.save()
            # dog = K9.objects.get(id=checked_dogs.id)
            # dog.assignment = str(data2) #TODO only save assignments for ports
            # dog.save()

        style = "ui green message"
        messages.success(request, 'Dogs has been successfully Scheduled!')

        return redirect('deployment:request_dog_details', id=id)

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title': data2,
        'data2': data2,
        'can_deploy': can_deploy,
        'style': style,
        'dogs_deployed': dogs_deployed,
        'user':user,
        'can_deploy_df': can_deploy_dataframe,

        'sar_deployed' : sar_deployed,
        'ndd_deployed' : ndd_deployed,
        'edd_deployed' : edd_deployed,

        'tl_dog' : tl_dog,
        'in_the_past' : in_the_past
    }

    return render(request, 'deployment/request_dog_details.html', context)

def remove_dog_request(request, id):
    # pull_k9 = Team_Dog_Deployed.objects.filter(id=id).last()
    k9 = K9.objects.filter(id=id).last()
    dog_request = Dog_Request.objects.filter(id=id).last()

    sched = K9_Schedule.objects.filter(Q(k9 = k9), Q(dog_request = dog_request))
    sched.delete()

    #change Team_Dog_Deployed model
    # pull_k9.status = 'Pulled-Out'
    # pull_k9.date_pulled = datetime.date.today()
    # pull_k9.save()

    #change K9 model
    # k9.assignment = 'None'
    # k9.save()
    #TODO Only put None if K9 is currently deployed on said request

    #change Dog_Request model
    if k9.capability == 'EDD':
        dog_request.EDD_deployed  = dog_request.EDD_deployed - 1
    elif k9.capability == 'NDD':
        dog_request.NDD_deployed = dog_request.NDD_deployed - 1
    elif k9.capability == 'SAR':
        dog_request.SAR_deployed = dog_request.SAR_deployed - 1
    else:
        pass
    dog_request.k9s_deployed = dog_request.k9s_deployed - 1
    dog_request.save()

    messages.success(request, 'Dogs has been successfully un-scheduled')

    return redirect('deployment:request_dog_details', id=dog_request.id)

# def deployment_report(request):
#     assignment = Team_Assignment.objects.all()
#
#     #NOTIF SHOW
#     notif_data = notif(request)
#     count = notif_data.filter(viewed=False).count()
#     user = user_session(request)
#     context = {
#         'title': 'Request Dog List',
#         'assignment': assignment,
#         'notif_data':notif_data,
#         'count':count,
#         'user':user,
#     }
#     return render (request, 'deployment/request_dog_list.html', context)


def view_schedule(request, id):

    date_now = datetime.date.today()

    k9 = K9.objects.filter(id = id).last()


    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'k9' : k9,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }

    return render(request, 'deployment/k9_schedule.html', context)


def deployment_area_details(request):
    user = user_session(request)

    data = None
    try:
        data = Team_Assignment.objects.filter(team_leader=user).last()
    except:
         pass

    tdd = Team_Dog_Deployed.objects.filter(team_assignment=data).filter(status='Deployed')

    sar_inc = Incidents.objects.filter(location=data.location).filter(type='Search and Rescue Related').count()
    ndd_inc = Incidents.objects.filter(location=data.location).filter(type='Narcotics Related').count()
    edd_inc = Incidents.objects.filter(location=data.location).filter(type='Explosives Related').count()
    incidents = Incidents.objects.filter(location=data.location).filter(type='Others').count()

    mn = []
    for td in tdd:
        pi = Personal_Info.objects.filter(UserID=td.handler).last()
        mn.append(pi.mobile_number)

    data_list = zip(tdd, mn)


    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'data':data,
        'tdd':tdd,
        'sar_inc':sar_inc,
        'ndd_inc':ndd_inc,
        'edd_inc':edd_inc,
        'incidents':incidents,
        'data_list':data_list,
    }

    return render(request, 'deployment/deployment_area_details.html', context)

def add_incident(request):
    user = user_session(request)
    form = IncidentForm(request.POST or None)
    style = "ui green message"


    user_serial = request.session['session_serial']

    # print("USER SERIAL")
    # print(user_serial)

    user = Account.objects.filter(serial_number=user_serial).last()
    current_user = User.objects.filter(id=user.UserID.id).last()

    ta = Team_Assignment.objects.filter(team_leader=current_user).last()


    form.initial['date'] = date.today()
    form.fields['location'].queryset = Location.objects.filter(id=ta.location.id)

    if request.method == 'POST':
        if form.is_valid():
            f = form.save(commit=False)
            f.user = user
            f.save()

            style = "ui green message"
            messages.success(request, 'Incident has been successfully added!')
            return redirect('deployment:add_incident')
        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    context = {
        'title': 'Report Incident Form',
        'texthelp': 'Input Incident Details Here',
        'form': form,
        'actiontype': 'Submit',
        'style': style,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render(request, 'deployment/incident_form.html', context)

def incident_list(request):
    title = "Incidents List View"
    incidents = Incidents.objects.all()

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'incidents': incidents,
        'title': title,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }

    return render(request, 'deployment/incident_list.html', context)


def choose_date(request):
    form = DateForm(request.POST or None)

def fou_details(request):
    user = user_session(request)
    data = Team_Assignment.objects.filter(team_leader=user).last()

    tdd = Team_Dog_Deployed.objects.filter(team_assignment=data).filter(status='Deployed')

    a = []
    for td in tdd:
        a.append(td.handler)

    #a =User.objects.filter(id=tdd.handler.id)
    pi = Personal_Info.objects.filter(UserID__in = a)

    data_list = zip(tdd,pi)

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'data_list':data_list,
    }

    return render(request, 'deployment/fou_details.html', context)

def daily_refresher_form(request):
    user = user_session(request)
    k9 = None
    try:
        k9 = K9.objects.filter(handler=user).last()
    except MultipleObjectsReturned:
        k9 = K9.objects.filter(handler=user).last()
    form = DailyRefresherForm(request.POST or None)
    style = "ui green message"
    drf = Daily_Refresher.objects.filter(handler=user).filter(date=datetime.date.today())

    dr = None
    if drf.exists():
        dr = 1
    else:
        dr = 0

    if request.method == 'POST':
        # print(form.errors)
        if form.is_valid():
            f = form.save(commit=False)
            f.k9 = k9
            f.handler = user

            mar = request.POST.get('select')
            f.mar = mar

            port = (f.port_find / f.port_plant * 20)
            building = (f.building_find /f.building_plant * 20)
            vehicle = (f.vehicle_find /f.vehicle_plant * 20)
            baggage = (f.baggage_find /f.baggage_plant * 20)
            others = (f.others_find /f.others_plant * 20)

            # MODEL save__
            # find = (f.port_find+f.building_find+f.vehicle_find+f.baggage_find+f.others_find)
            # plant = (f.port_plant+f.building_plant+f.vehicle_plant+f.baggage_plant+f.others_plant)

            # f.rating = 100 - ((plant - find) * 5)

            #TIME
            #time = (f.port_time + f.building_time + f.vehicle_time + f.baggage_time + f.others_time)
            # print(f.port_time)
            ######################
            f.save()

            style = "ui green message"
            messages.success(request, 'Refresher Form has been Recorded!')
            return redirect('deployment:daily_refresher_form')
        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'form':form,
        'dr':dr,
        'style':style,
    }


    return render(request, 'deployment/daily_refresher_form.html', context)

#TODO: this
def incident_detail(request, id):
    incident = Incidents.objects.filter(id = id).last()
    title = "Incident Detail View"


    # NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context ={
        'incident' : incident,
        'title': title,
        'notif_data': notif_data,
        'count': count,
        'user': user,
    }

    return render(request, 'deployment/incident_detail.html', context)

def deployment_report(request):

    from_date = request.session["session_fromdate"]
    to_date = request.session["session_todate"]
    requestdog = Dog_Request.objects.filter(start_date__range = [from_date, to_date])
    incident = Incidents.objects.filter(date__range = [from_date, to_date])
    user = request.session["session_username"]
    team = Team_Assignment.objects.filter(date_added__range = [from_date, to_date])
    deployed = Team_Dog_Deployed.objects.filter(date_added__range = [from_date, to_date]).filter(date_pulled__range = [from_date, to_date])

    context = {
        'title': "",
        'requestdog': requestdog,
        'from_date': from_date,
        'to_date': to_date,
        'incident': incident,
        'user': user,
        'team': team,
        'deployed': deployed,
    }
    return render(request, 'deployment/deployment_report.html', context)

def Average(lst):
    return sum(lst) / len(lst)

def choose_location(request):

    #TODO Add user field to TempDeployment to avoid issues when multiple users are using the system at the same time (also check ancestral view from training module)
    removal = TempDeployment.objects.all()
    removal.delete()

    locations = Location.objects.all()

    location_incident_count_list = []
    location_maritime_count_list = []
    location_list = []
    team_list = []
    for location in locations:
        incident_count = Incidents.objects.filter(location=location).count()
        location_incident_count_list.append(incident_count)
        maritime_count = Maritime.objects.filter(location=location).count()
        location_maritime_count_list.append(maritime_count)
        team = Team_Assignment.objects.filter(location = location).last()
        location_list.append(location)
        team_list.append(team)

    df_data = {
        'Location': location_list,
        'Maritime': location_maritime_count_list,
        'Incident': location_incident_count_list,
        'Team' : team_list
    }
    location_dataframe = df(data=df_data)
    location_dataframe.sort_values(by=['Maritime', 'Incident'], ascending=[True, True])

    context = {
        'locations': location_dataframe,
    }

    return render(request, 'deployment/location_list.html', context)

#TODO filter units available by capability if the number has already met demand requirements
#TODO add counter for units that are set for deployment
#TODO sort units by incident count

#TODO capability_blacklist only updates when another location is selected
def load_units(request):

    selected_list = []

    location_id = request.GET.get('location')
    location = Location.objects.filter(id = location_id).last()

    # filter personal_info where city != Team_Assignment.city
    handlers = Personal_Info.objects.exclude(city=location.city)

    user_deploy = []
    for h in handlers:
        user_deploy.append(h.UserID)

    capability_blacklist = []

    team = Team_Assignment.objects.filter(location=location).last()

    sar_count_select = 0
    ndd_count_select = 0
    edd_count_select = 0

    try: #The solution lies on the checkbox initial values right here
        fullstring = request.GET.get('fullstring')
        fullstring = json.loads(fullstring)

        # print("FullString")
        # print(fullstring)

        for item in fullstring.values(): # item == checked checkboxes
            selected_list.append(item)

        # print("SELECTED LIST")
        # print(selected_list)

        # START TEST


        temp = TempDeployment.objects.filter(location=location)
        k9s = K9.objects.filter(pk__in = selected_list)

        # print("TEMP OBJECTS")
        # print(temp)

        for item in temp:
            if item.k9.capability == "SAR":
                sar_count_select += 1
            elif item.k9.capability == "NDD":
                ndd_count_select += 1
            else:
                edd_count_select += 1

        if (team.EDD_deployed + edd_count_select) >= team.EDD_demand:
            capability_blacklist.append("EDD")
        if (team.NDD_deployed + ndd_count_select) >= team.NDD_demand:
            capability_blacklist.append("NDD")
        if (team.SAR_deployed + sar_count_select) >= team.SAR_demand:
            capability_blacklist.append("SAR")

        # print("CAPABILITY BLACKLIST")
        # print(capability_blacklist)

        # print(sar_count_select)
        # print(ndd_count_select)
        # print(edd_count_select)

        # END TEST

    except:
        pass

    # #filter K9 where handler = person_info and k9 assignment = None
    can_deploy = K9.objects.filter(handler__in=user_deploy).filter(training_status='For-Deployment').filter(
        assignment='None').exclude(capability__in=capability_blacklist)

    context = {
        'location': location,
        'can_deploy' : can_deploy,
        'selected_list' : selected_list,
        'team' : team,
        'sar': sar_count_select,
        'ndd': ndd_count_select,
        'edd': edd_count_select
    }

    return render(request, 'deployment/ajax_load_units.html', context)


def load_units_selected(request): #Note : Maybe we can use a db solution for this one

    scheduleFormset = formset_factory(ScheduleUnitsForm, extra=1, can_delete=True)

    fullstring = request.GET.get('fullstring')
    fullstring = json.loads(fullstring)

    k9_list = []
    k9_list_id = []

    try:
        location_id = request.GET.get('location')
        location = Location.objects.filter(id=location_id).last()

        for item in fullstring.values():
            k9 = K9.objects.filter(id=item).last()
            k9_list.append(k9)
            k9_list_id.append(k9.id)

            # >>>>>>>

            if TempDeployment.objects.filter(k9=k9).exists():
                pass
            else:
                temp = TempDeployment.objects.create(location=location, k9=k9)
                temp.save()

                removal = TempDeployment.objects.exclude(id=temp.id).filter(k9=k9).filter(
                    location=location)  # hindi dapat idelete yung previously saved
                removal.delete()

    except:
        for item in fullstring.values():
            k9 = K9.objects.filter(id=item).last()
            k9_list.append(k9)
            k9_list_id.append(k9.id)

            # >>>>>>>

            if TempDeployment.objects.filter(k9=k9).exists():
                pass
            else:
                removal = TempDeployment.objects.filter(k9=k9)  # Dapat icheck niya kung ano yung mga hindi naka select
                removal.delete()


    can_deploy = K9.objects.filter(training_status='For-Deployment').filter(
        assignment='None').exclude(pk__in= k9_list_id)

    removal = TempDeployment.objects.exclude(k9__in=k9_list)
    removal.delete()

    temp_deploy = TempDeployment.objects.all()

    k9_list_id = list(dict.fromkeys(k9_list_id))

    context = {
        'can_deploy': can_deploy,
        'temp_deploy' : temp_deploy,
        'formset' : scheduleFormset,
        'selected_list' : k9_list_id
    }

    return render(request, 'deployment/ajax_load_units_selected.html', context)



def assign_k9_to_initial_ports(location_dataframe, k9s_scheduled_list): #Note: no changes made to dataframe here
    end_assignment = 0
    iteration = 0

    # can_deploy = K9.objects.filter(training_status='For-Deployment').filter(
    #     assignment='None').exclude(pk__in=k9s_scheduled_list)

    temp = TempDeployment.objects.all()  # add user field to avoid complications involving multiple users in the future
    k9_id_list = []
    for item in temp:
        k9_id_list.append(item.k9.id)
        # print("TEMP K9")
        # print(item.k9)

    while end_assignment == 0 and K9.objects.filter(training_status='For-Deployment').filter(
                assignment=None).exclude(pk__in=k9_id_list).exclude(pk__in=k9s_scheduled_list) is not None:

        # Solution 2: Loop through dataframe first
        for item in location_dataframe.values:
            incident_type_selected = 0
            location = item[0]
            incident_type_list = item[5]
            team = item[6]  # check if only 1 unit is assigned (must be 2)

            temp = TempDeployment.objects.all()  # add user field to avoid complications involving multiple users in the future
            k9_id_list = []
            for item in temp:
                k9_id_list.append(item.k9.id)
                # print("TEMP K9")
                # print(item.k9)

            handlers = Personal_Info.objects.filter(city=location.city)

            handler_exclude_list = []  # append the id of the handlers
            for h in handlers:
                handler_exclude_list.append(h.UserID.id)
            # print(handler_can_deploy)

            # get instance of user using personal_info.id
            # id of user is the fk.id of person_info
            user_exclude = User.objects.filter(id__in=handler_exclude_list)

            # Get K9s ready for deployment #exclude already scheduled K9s
            can_deploy = K9.objects.filter(training_status='For-Deployment').exclude(pk__in=k9_id_list).exclude(pk__in=k9s_scheduled_list).exclude(handler__in = user_exclude) #Same code in main
            # End Get K9s ready for deployment

            # print("CAN DEPLOY QUERYSET")
            # print(can_deploy)

            # if can_deploy is None:
            #     sys.exit()

            k9s_assigned = 0
            finish_location_assignment = 0
            for k9 in can_deploy:
                # print("CAN DEPLOY K9")
                # print(k9)
                if finish_location_assignment == 0:
                    type = incident_type_list[iteration][0]
                    if type == k9.capability:

                        sar_count = 0
                        ndd_count = 0
                        edd_count = 0
                        for item in TempDeployment.objects.filter(
                                location=location):  # this code also checks temporarily assigned k9s
                            if item.k9.capability == "SAR":
                                sar_count += 1
                            elif item.k9.capability == "NDD":
                                ndd_count += 1
                            elif item.k9.capability == "EDD":
                                edd_count += 1
                            else:
                                pass

                        if type == "SAR":
                            if team.SAR_deployed + sar_count < team.SAR_demand:
                                TempDeployment.objects.create(k9=k9, location=location)
                                k9s_assigned += 1

                        elif type == "NDD":
                            if team.NDD_deployed + ndd_count < team.NDD_demand:
                                TempDeployment.objects.create(k9=k9, location=location)
                                k9s_assigned += 1

                        elif type == "EDD":
                            if team.EDD_deployed + edd_count < team.EDD_demand:
                                TempDeployment.objects.create(k9=k9, location=location)
                                k9s_assigned += 1

                        else:
                            pass

                    # dogs_scheduled_count = Team_Dog_Deployed.objects.filter(status="Scheduled",
                    #                                                         team_assignment = team).count()
                    dogs_scheduled_count = K9_Schedule.objects.filter(status="Initial Deployment", team=team).filter(k9__in = can_deploy).count()
                    if (team.total_dogs_deployed + k9s_assigned + dogs_scheduled_count) >= 2:  # There must be atleast 2 units per location #TODO Include schedule K9s
                        # print("Units per Location " + str(location))
                        # print(team.total_dogs_deployed + k9s_assigned)
                        finish_location_assignment = 1


        #Code does not reach this part
        if iteration == 2:
            end_assignment = 1
        else:
            iteration += 1

    return None


def schedule_units(request):

    removal = TempDeployment.objects.all() #TODO add user field then only delete objects from said user
    removal.delete()

    events = K9_Schedule.objects.filter(status="Initial Deployment").filter(date_start__gte = datetime.datetime.today())

    # #K9s estimated training duration
    # sar_done = K9.objects.filter(training_status = "Trained").filter(capability = "SAR").count()
    # ndd_done = K9.objects.filter(training_status = "Trained").filter(capability = "NDD").count()
    # edd_done = K9.objects.filter(training_status = "Trained").filter(capability = "EDD").count()
    # k9s_training = K9.objects.filter(training_status = "On-Training")
    #
    # k9_training_list = []
    # duration_estimate_list = []
    # train_end_estimate_list = []
    # for k9 in k9s_training:
    #     train_sched = Training_Schedule.objects.filter(k9=k9).exclude(date_start = None).exclude(date_end = None)
    #
    #     duration_list = []
    #     if train_sched:
    #         k9_training_list.append(k9)
    #
    #
    #         for item in train_sched:
    #             delta = item.date_end - item.date_start
    #             duration_list.append(int(delta.days))
    #
    #         duration_average = Average(duration_list)
    #         duration_estimate_list.append(duration_average)
    #
    #         days_estimate_before_end = duration_average * (9 - len(duration_list))
    #         train_end_estimate_list.append(days_estimate_before_end)
    #
    # df_training_data = {
    #     'K9': k9_training_list,
    #     'Duration': duration_estimate_list,
    #     'End_Estimate': train_end_estimate_list,
    # }
    #
    # training_dataframe = df(data=df_training_data)
    # training_dataframe = training_dataframe.sort_values(by=['End_Estimate'],
    #                                                     ascending=[True])
    #
    # #END K9s estimated training duration

    pre_dep = K9_Pre_Deployment_Items.objects.filter(status="Cancelled")

    k9s_tobe_redeployed = []
    for item in pre_dep:
        k9s_tobe_redeployed.append(item.k9)

    # Prioritize Locations
    locations = Location.objects.all()
    location_incident_list = []
    location_maritime_list = []
    location_list = []
    team_list = []
    total_dogs_deployed_list = []
    incident_order_list = []

    location_incident_list_count = []
    location_maritime_list_count = []
    sorter_col = []
    for location in locations:
        maritimes = Maritime.objects.filter(location=location)
        location_maritime_list.append(maritimes)
        incidents = Incidents.objects.filter(location=location)
        location_incident_list.append(incidents)

        location_incident_list_count.append(maritimes.count())
        location_maritime_list_count.append(incidents.count())

        team = Team_Assignment.objects.filter(location=location).last()

        if team.total_dogs_deployed == 1:
            sorter_col.append(1)
        elif team.total_dogs_deployed == 0:
            sorter_col.append(0)
        else:
            sorter_col.append(-1)

        location_list.append(location)
        team_list.append(team)

        #dogs_scheduled_count = Team_Dog_Deployed.objects.filter(status = "Scheduled", team_assignment = team).count()
        dogs_scheduled_count = K9_Schedule.objects.filter(Q(status = "Initial Deployment") | Q(k9__in = k9s_tobe_redeployed)).filter(team = team).count()

        total_dogs_deployed_list.append(team.total_dogs_deployed + dogs_scheduled_count) #TODO Included scheduled K9s

        #Sort incidents
        incident_type_list = []
        incident_type_order_list = []
        for incident in incidents:
            # type = incident.type
            incident_type_list.append(incident.type)


        #order incident_type_order_list[] by the most count from incident_type_list[]
        sar_incident = 0
        ndd_incident = 0
        edd_incident = 0
        for type in incident_type_list:
            if type == "Search and Rescue Related":
                sar_incident += 1
            elif type == "Narcotics Related":
                ndd_incident += 1
            elif type == "Explosives Related":
                edd_incident += 1
            else:
                pass


        incident_type_order_list.append(('SAR', sar_incident))
        incident_type_order_list.append(('NDD', ndd_incident))
        incident_type_order_list.append(('EDD', edd_incident))

        #incident_type_order_list.sort(reverse=True)#TODO find a way to sort a list of tuples
        incident_type_order_list.sort(key=lambda  tup: tup[1], reverse=True)

        incident_order_list.append(incident_type_order_list)

        #Replace code up to this point with a better version (too loopy and hardcody)

    #TODO add incident_type_order_list[] to the dataframe columns
    #TODO Add currently scheduled to templates
    df_data = {
        'Location': location_list,
        'Maritime': location_maritime_list,
        'Incident': location_incident_list,
        'Maritime_count': location_maritime_list_count,
        'Incident_count': location_incident_list_count,
        'Incident_Order_List': incident_order_list,
        'Team': team_list,
        'Dogs_deployed': total_dogs_deployed_list,
        'Sorter': sorter_col
        }
    location_dataframe = df(data=df_data)
    location_dataframe.sort_values(by=['Sorter', 'Dogs_deployed', 'Maritime_count', 'Incident_count'], ascending=[False, True, False, False], inplace=True)

    print(location_dataframe)
         #End Sort incidents
    #End Prioritize Location

    #TODO For those whose deploymetns are cancelled, pwede sila isama
    #Temporary assignment
    k9s_scheduled_list = []
    # k9s_scheduled = Team_Dog_Deployed.objects.filter(status="Scheduled")
    k9s_scheduled = K9_Schedule.objects.filter(status="Initial Deployment").exclude(k9__in = k9s_tobe_redeployed)

    for item in k9s_scheduled:
        k9s_scheduled_list.append(item.k9.id)

    assign_k9_to_initial_ports(location_dataframe, k9s_scheduled_list)

    # temp = TempDeployment.objects.all()  # add user field to avoid complications involving multiple users in the future
    k9_id_list = []

    locations = list(location_dataframe['Location'])

    for location in locations:
        # temp_count = 0
        # for item in temp:
        #     if item.location == location:
        #         temp_count += 1
        temp_count = TempDeployment.objects.filter(location = location).count()

        #TODO We are already deleting k9s pending for deployment right here
        if temp_count < 2:
            removal = TempDeployment.objects.filter(location=location) #TODO add user field then only delete objects from said user
            removal.delete()


    temp = TempDeployment.objects.all()
    for item in temp:
        k9_id_list.append(item.k9.id)

    temp_list = []
    for location in locations:
        temp = TempDeployment.objects.filter(location = location)
        temp_list.append(temp)

    #End Temporary assignment


    location_dataframe['Temp_list'] = temp_list
    temp_list = list(location_dataframe['Temp_list'])

    # print(temp_list)

    idx = 0
    delete_indexes = []

    for item in temp_list:
        if not item:
            delete_indexes.append(idx)
        idx += 1

    # print("DELETE INDEXES")
    # print(delete_indexes)

    #TODO Issue with current code where 2 k9s with varying skills are less likely be put in the same port together because of incident order list
    location_dataframe.drop(location_dataframe.index[delete_indexes], inplace=True) #Delete rows without any K9s assigned
    location_dataframe.reset_index(drop=True, inplace=True)

    location_dataframe.sort_values(by=['Sorter', 'Dogs_deployed', 'Maritime_count', 'Incident_count'],
                                   ascending=[False, True, False, False], inplace=True)

    print(location_dataframe)
    # NEW CODE
    location_dataframe.drop(columns='Temp_list', inplace=True)
    location_dataframe.drop(columns='Sorter', inplace=True)
    assign_k9_to_initial_ports(location_dataframe, k9s_scheduled_list)

    team_list = list(location_dataframe['Team'])
    locations = list(location_dataframe['Location'])

    temp_list = []
    k9_id_list = []
    for location in locations:
        temp = TempDeployment.objects.filter(location=location)
        temp_list.append(temp)
        for item in temp:
            k9_id_list.append(item.k9.id)

    location_dataframe['Temp_list'] = temp_list

    #TODO exclude k9s pending for deployment if they are already assigned on 2nd evaluation
    can_deploy = K9.objects.filter(training_status='For-Deployment').filter(
        assignment=None).exclude(pk__in=k9_id_list).exclude(pk__in=k9s_scheduled_list)

    # END NEW CODE

    d = datetime.datetime.today() + timedelta(days=7)
    # schedFormset = formset_factory(DeploymentDateForm, extra=len(locations))
    schedFormset = formset_factory(wraps(DeploymentDateForm)(partial(DeploymentDateForm, init_date = d)), extra=len(locations))
    formset = schedFormset(request.POST or None)

    style = ""

    # print(location_dataframe)


    if request.method == 'POST':
        invalid = False
        msg = ''
        ctr = 0
        if formset.is_valid:
            for form in formset:
                if form.is_valid:
                    try:
                        deployment_date = form['deployment_date'].value()
                        deployment_date = datetime.datetime.strptime(deployment_date, "%Y-%m-%d").date()
                        delta = deployment_date - datetime.date.today()

                        if delta.days < 7:
                            invalid = True
                            ctr = ctr + 1
                            msg = msg + str(ctr) + ', '

                    except:pass


            if invalid == True:
                style = "ui red message"
                messages.warning(request, 'Dates should have atleast 1 week allowance on Row ' + msg)

            idx = 0
            k9_count = 0
            for form in formset:
                if form.is_valid and invalid == False:
                    # try:
                    deployment_date = form['deployment_date'].value()
                    deployment_date = datetime.datetime.strptime(deployment_date, "%Y-%m-%d").date()
                    delta = deployment_date - datetime.date.today()

                    if delta.days < 7:
                        style = "ui red message"
                        messages.warning(request, 'Dates should have atleast 1 week allowance')
                    else:
                        team = team_list[idx]
                        temp = temp_list[idx]

                        for item in temp:

                            #deploy = Team_Dog_Deployed.objects.create(team_assignment = team, k9 = item.k9, status = "Scheduled", date_added = deployment_date)
                            deploy = K9_Schedule.objects.create(team = team, k9 = item.k9, status = "Initial Deployment", date_start = deployment_date)
                            deploy.save()

                            # phex = K9_Schedule.objects.create(team = team, k9 = item.k9, status = "Checkup", date_start = deployment_date - timedelta(days=7))
                            # phex.save()

                            current_pre_reqs =  K9_Pre_Deployment_Items.objects.filter(k9 = item.k9)
                            current_pre_reqs.delete()

                            pre_req_item = K9_Pre_Deployment_Items.objects.create(k9 = item.k9, initial_sched = deploy)
                            pre_req_item.save()

                            k9_count += 1

                idx += 1

            Notification.objects.create(position='Veterinarian', user=None, notif_type='vet_dep_phex_new',
                                        message='There are ' + str(k9_count) + ' new k9s needed to be scheduled for physical exam.')


            # current_phex = K9_Schedule.objects.filter(status="Checkup").filter(date_start__gt = datetime.datetime.today()).order_by('date_start')
            #
            # ctr = 0
            # date_index = datetime.datetime.today() + timedelta(days=1)
            # for item in current_phex:
            #     if ctr < 10:
            #         item.date_start = date_index
            #         item.save()
            #         ctr += 1
            #     else:
            #         date_index += timedelta(days=1)
            #         item.date_start = date_index
            #         item.save()
            #         ctr = 0


            if invalid == False:
                style = "ui green message"
                # messages.success(request, 'Units have been successfully scheduled for deployment!')
                return redirect('profiles:dashboard')

    df_is_empty = False
    if location_dataframe.empty:
        df_is_empty = True

    #TODO Issue for SAR units since they can't be deployed initially on ports because of "2 minimum" restriction

    user = user_session(request)
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()

    context = {
        'df' : location_dataframe,
        'can_deploy': can_deploy,
        'temp': TempDeployment.objects.all(),
        'formset' :schedFormset,
        'style': style,
        'df_is_empty' : df_is_empty,
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'events':events,
        # 'sar_done': sar_done,
        # 'ndd_done' : ndd_done,
        # 'edd_done' : edd_done,
        # 'train_df' : training_dataframe
    }

    return render(request, 'deployment/schedule_units.html', context)

def transfer_request(request, k9_id, team_assignment_id, location_id):

    #TODO check if date of transfer has conflict
    #TODO if unit is transferring, prompt commander/operations if he wants to replace units assigned to a request

    k9 = K9.objects.filter(id = k9_id).last()
    team = Team_Assignment.objects.filter(id = team_assignment_id).last() #Current Team
    location = Location.objects.filter(id = location_id).last()  #Location to transfer to (user input)
    team_to_transfer = Team_Assignment.objects.filter(location = location).last() #Team to transfer to

    can_transfer = 0

    try:
        team_dog_deployed = Team_Dog_Deployed.objects.filter(k9=k9, status="Deployed").filter(team_assignment = team).last() #check current team_assignment
        if (team_dog_deployed.date_pulled is None):
            date_deployed = team_dog_deployed.date_added
            delta = date.today() - date_deployed
            duration = delta.days

            if k9.capability == "SAR":
                if team_to_transfer.SAR_deployed < team_to_transfer.SAR_demand:
                    can_transfer = 1
            elif K9.capability == "NDD":
                if team_to_transfer.NDD_deployed < team_to_transfer.NDD_demand:
                    can_transfer = 1
            else:
                if team_to_transfer.EDD_deployed < team_to_transfer.EDD_demand:
                    can_transfer = 1


            if duration >= 730 and (team.total_dogs_deployed - 1) >= 2 and can_transfer == 0:
                can_transfer = 1

        if can_transfer == 1:
            team_dog_deployed.date_pulled = date.today()
            team_dog_deployed.save()
            deploy = Team_Dog_Deployed.objects.create(k9=k9, team_assignment=team_to_transfer)

    except:
        pass


    return None
