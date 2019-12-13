from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, inlineformset_factory
from django.db.models import aggregates
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as AuthUser
from django.db.models import Q
from django.core.exceptions import MultipleObjectsReturned
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from django.db.models import Sum
from datetime import datetime, date
import calendar
import ast
from decimal import *
import pandas as pd
import numpy as np
import re

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from profiles.serializers import NotificationSerializer, UserSerializer
from deployment.views import load_map, load_locations

from profiles.models import User, Personal_Info, Education, Account
from deployment.models import Location, Team_Assignment, Dog_Request, Incidents, Team_Dog_Deployed, Daily_Refresher, \
    Area, K9_Schedule, K9_Pre_Deployment_Items
from deployment.forms import GeoForm, GeoSearch, RequestForm, MaritimeForm
from profiles.forms import add_User_form, add_personal_form, add_education_form, add_user_account_form, CheckArrivalForm
from planningandacquiring.models import K9, K9_Mated, Actual_Budget
from unitmanagement.models import Notification, Request_Transfer, PhysicalExam,Call_Back_K9, VaccinceRecord, \
    K9_Incident, VaccineUsed, Replenishment_Request, Transaction_Health, Emergency_Leave, Temporary_Handler, \
    Handler_On_Leave, Handler_Incident, K9_Incident
from training.models import Training_Schedule, Training
from inventory.models import Miscellaneous, Food, Medicine_Inventory, Medicine

from deployment.tasks import subtract_inventory, assign_TL, task_to_dash_dep

from deployment.views import team_location_details, request_dog_details, mass_populate_revisited
from unitmanagement.forms import EmergencyLeaveForm
from unitmanagement.tasks import check_leave_window, task_to_dash_um
from planningandacquiring.tasks import task_to_dash_pq

# Create your views here.

def notif(request):
    serial = request.session['session_serial']
    account = Account.objects.get(serial_number=serial)
    user_in_session = User.objects.get(id=account.UserID.id)

    if user_in_session.position == 'Veterinarian':
        notif = Notification.objects.filter(position='Veterinarian').order_by('-datetime')
    elif user_in_session.position == 'Handler' or user_in_session.position == 'Team Leader':
        notif = Notification.objects.filter(user=user_in_session).order_by('-datetime')
    else:
        notif = Notification.objects.filter(position='Administrator').order_by('-datetime')

    return notif

def notif_list(request):

    notif_data = notif(request)

    dept_notif = notif_data.filter(notif_type='dog_request').filter(notif_type='location_incident').filter(notif_type='call_back').filter(notif_type='initial_deployment')

    um_notif = notif_data.exclude(notif_type='dog_request').exclude(notif_type='location_incident').exclude(notif_type='call_back').exclude(notif_type='initial_deployment')

    count = notif_data.filter(viewed=False).count()
    user = user_session(request)

    context={
        'notif_data':notif_data,
        'dept_notif':dept_notif,
        'um_notif':um_notif,
        'count':count,
        'user':user,
    }
    return render (request, 'profiles/notification_list.html', context)

def user_session(request):
    serial = request.session['session_serial']
    account = Account.objects.get(serial_number=serial)
    user_in_session = User.objects.get(id=account.UserID.id)
    return user_in_session

def dashboard(request):
    user = user_session(request)

    #Regular Leave & Emergency Leave
    rl = Handler_On_Leave.objects.filter(status='Pending').count()
    el = Emergency_Leave.objects.filter(status='Ongoing').count()

    #Incident
    hi = Handler_Incident.objects.filter(status='Pending').count()
    k9i = K9_Incident.objects.filter(status='Pending').count()

    can_deploy = K9.objects.filter(training_status='For-Deployment').filter(assignment='None').count()
    NDD_count = K9.objects.filter(capability='NDD').count()
    EDD_count = K9.objects.filter(capability='EDD').count()
    SAR_count = K9.objects.filter(capability='SAR').count()

    NDD_deployed = list(Team_Assignment.objects.aggregate(Sum('NDD_deployed')).values())[0]
    EDD_deployed = list(Team_Assignment.objects.aggregate(Sum('EDD_deployed')).values())[0]
    SAR_deployed = list(Team_Assignment.objects.aggregate(Sum('SAR_deployed')).values())[0]

    if not NDD_deployed:
        NDD_deployed = 0
    if not EDD_deployed:
        EDD_deployed = 0
    if not SAR_deployed:
        SAR_deployed = 0

    NDD_demand = list(Team_Assignment.objects.aggregate(Sum('NDD_demand')).values())[0]
    EDD_demand = list(Team_Assignment.objects.aggregate(Sum('EDD_demand')).values())[0]
    SAR_demand = list(Team_Assignment.objects.aggregate(Sum('SAR_demand')).values())[0]

    if not NDD_demand:
        NDD_demand = 0
    if not EDD_demand:
        EDD_demand = 0
    if not SAR_demand:
        SAR_demand = 0

    k9_demand = NDD_demand + EDD_demand + SAR_demand
    k9_deployed = NDD_deployed + EDD_deployed + SAR_deployed

    # k9_demand_request = NDD_needed + EDD_needed + SAR_needed
    # k9_deployed_request = NDD_deployed_request + EDD_deployed_request + SAR_deployed_request

    unclassified_k9 = K9.objects.filter(capability="None").count()
    untrained_k9 = K9.objects.filter(training_status="Unclassified").count()
    on_training = K9.objects.filter(training_level="Stage 1").count()
    trained = K9.objects.filter(training_status="Trained").count()

    #equipment_requests = Equipment_Request.objects.filter(request_status="Pending").count()

    for_breeding = K9.objects.filter(training_status="For-Breeding").count()

    #Calendar

    events = Dog_Request.objects.all()

    #Counts
    c_count = K9.objects.filter(training_status='Classified').count()
    item_req_count = Replenishment_Request.objects.filter(status='Pending').count()
    up_count = K9.objects.filter(status='Working Dog').filter(handler=None).exclude(training_status = "For-Breeding").exclude(training_status = "Breeding").count()
    tq_count = Request_Transfer.objects.filter(status='Pending').count()

    pre_dep_items = K9_Pre_Deployment_Items.objects.filter(Q(status = "Pending") | Q(status = "Confirmed") | Q(status = "Done"))
    k9s_scheduled = K9_Schedule.objects.filter(status="Initial Deployment")
    k9s_scheduled_list = []
    for item in k9s_scheduled:
        k9s_scheduled_list.append(item.k9.id)

    exclude_k9_list = []
    for item in pre_dep_items:
        exclude_k9_list.append(item.k9.id)

    dept_count = K9.objects.filter(training_status='For-Deployment').exclude(pk__in = exclude_k9_list).exclude(handler=None).count() #initial deployment k9s
    pq_count = K9_Pre_Deployment_Items.objects.filter(status='Pending').count() #TODO change algo
    ua_count = K9.objects.filter(training_status = "MIA").count()

    print("Dept Count")
    print(dept_count)

    ab = None
    try:
        ab = Actual_Budget.objects.get(year_budgeted__year=datetime.today().year)

        aq = K9.objects.filter(date_created__year=datetime.today().year).count()

        ab_k9 = (ab.k9_needed + ab.k9_breeded) - aq

        if ab_k9 < 0:
            ab_k9 = 0

        ab_total = ab.others_total + ab.kennel_total + ab.vet_supply_total + ab.medicine_total + ab.vac_prev_total + ab.food_milk_total + ab.petty_cash


    except ObjectDoesNotExist:
        ab_k9 = 0
        ab_total = None
    item_list = []
    pre_req_count = 0
    try:
        kdi = K9_Pre_Deployment_Items.objects.filter(status='Pending').exclude(initial_sched__date_end__lt=date.today())

        for kp in kdi:
            date_1 = kp.initial_sched.date_start - relativedelta(days=5)
            if date.today() >= date_1:
                pre_req_count = pre_req_count+1

        try:
            collar = Miscellaneous.objects.filter(miscellaneous__contains="Collar").aggregate(sum=Sum('quantity'))['sum'] - pre_req_count
            vest = Miscellaneous.objects.filter(miscellaneous__contains="Vest").aggregate(sum=Sum('quantity'))['sum'] - pre_req_count
            leash = Miscellaneous.objects.filter(miscellaneous__contains="Leash").aggregate(sum=Sum('quantity'))['sum'] - pre_req_count
            shipping_crate = Miscellaneous.objects.filter(miscellaneous__contains="Shipping Crate").aggregate(sum=Sum('quantity'))['sum'] - pre_req_count
            food = Food.objects.filter(foodtype="Adult Dog Food").aggregate(sum=Sum('quantity'))['sum']
            medicines = Medicine_Inventory.objects.filter(medicine__med_type="Vitamins").aggregate(sum=Sum('quantity'))['sum'] - pre_req_count
            grooming_kit = Miscellaneous.objects.filter(miscellaneous__contains="Grooming Kit").aggregate(sum=Sum('quantity'))['sum'] - pre_req_count
            first_aid_kit = Miscellaneous.objects.filter(miscellaneous__contains="First Aid Kit").aggregate(sum=Sum('quantity'))['sum'] - pre_req_count
            oral_dextrose = Miscellaneous.objects.filter(miscellaneous__contains="Oral Dextrose").aggregate(sum=Sum('quantity'))['sum'] - pre_req_count
            ball = Miscellaneous.objects.filter(miscellaneous__contains="Ball").aggregate(sum=Sum('quantity'))['sum'] - pre_req_count

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

        except:
            pass

    except kdi.ObjectDoesNotExist:
        pass

    cbs = Call_Back_K9.objects.filter(Q(status='Pending') | Q(status='Confirmed'))

    cb_list = []
    for c in cbs:
        cb_list.append(c.k9.id)

    due_retire =  K9.objects.filter(training_status="Deployed").filter(status='Due-For-Retirement').exclude(handler=None).exclude(assignment="None").count()

    cb_conf_count = Call_Back_K9.objects.filter(status='Confirmed').count()
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    context = {
        'can_deploy': can_deploy,
        'k9_demand': k9_demand,
        'k9_deployed': k9_deployed,
        # 'k9_demand_request': k9_demand_request,
        # 'k9_deployed_request': k9_deployed_request,
        'unclassified_k9': unclassified_k9,
        'untrained_k9': untrained_k9,
        'on_training': on_training,
        'trained': trained,
        #'equipment_requests': equipment_requests,
        'for_breeding': for_breeding,

        'events': events,
        'ab': ab,
        'ab_k9': ab_k9,
        'ab_total':ab_total,

        'c_count': c_count,
        'item_req_count': item_req_count,
        'up_count': up_count,
        'tq_count': tq_count,
        'dept_count': dept_count,
        'pq_count': pq_count,
        'ua_count': ua_count,
        'pre_req_count':len(item_list),

        'rl': rl,
        'el':el,
        'k9i':k9i,
        'hi':hi,
        'due_retire':due_retire,
        'cb_conf_count':cb_conf_count,

        'notif_data':notif_data,
        'count':count,
        'user':user,
    }

    return render (request, 'profiles/dashboard.html', context)


#TODO all Team dogs deployed under the team of TL with "Pending status" are to be confirmed for arrival
def team_leader_dashboard(request):
    user = user_session(request)
    ta = None
    incident_count = 0
    tdd = None
    tdd_count= 0

    form = RequestForm(request.POST or None)
    geoform = GeoForm(request.POST or None)
    geosearch = GeoSearch(request.POST or None)

    maritime_form = MaritimeForm(request.POST or None, initial = {'date' : datetime.today().date(), 'time' : datetime.now().time()})
    working_handlers = User.objects.exclude(status = "Died").exclude(status = "MIA").exclude(status = "Retired").exclude(status = "No Longer Employed")

    temporary_care_k9s = Temporary_Handler.objects.filter(temp = user).filter(date_returned = None)

    k9 = None
    for_arrival = None
    check_arrival = None
    reveal_arrival = False

    ki = None
    try:
        k9 = K9.objects.filter(handler = user).last()
        ki = K9_Incident.objects.filter(Q(incident='Stolen') | Q(incident='Accident') | Q(incident='Lost')).filter(
        status='Pending').latest('id')
    except:pass

    
    ta = None
    try:
        ta = Team_Assignment.objects.filter(team_leader=user).last()
    except: pass

    dog_request = None

    try:
        incident_count = Incidents.objects.filter(location=ta.location).count()
        tdd = Team_Dog_Deployed.objects.filter(team_assignment=ta).filter(
            date_pulled=None).filter(handler__in = working_handlers)  # only currently deployed k9s | NOTE : tasks pull out k9s not confirmed within 5 days
        tdd_count = tdd.count()

        # NOTE: System checks every nth hours if handler arrival is confirmed, escalate to admin if not confirm (tasks.py)
        for_arrival = tdd.filter(status="Pending")
    except: pass


    #TODO check arrival of units at request and from request to port
    #NOTE: There are no requests with conflicting schedules that have the same handler, much less the same TL.

    #Handlers are pulled out from current assignment through Team_Dog_Deployed then is assigned to Dog_Request.
    #Dog_Request TLs are assigned as soon as deployment date hits
    #After dog request ends, everyone reverts back to "Handler" position. Note that Team_Assignment TLs cannot be deployed to Requests, making life easier

    reveal_for_arrival_request = False
    td_dr = None
    dr = None
    dog_req = None
    try: #NOTE: TL won't see this anyway unless he's not a TL within date range of Dog_Request
        # dr = Dog_Request.objects.filter(team_leader = user).exclude(start_date__lt=datetime.today().date()).exclude(end_date__gt=datetime.today().date()).last()
        dr = Dog_Request.objects.filter(team_leader=user).filter(Q(start_date__lte = datetime.today().date()), Q(end_date__gte = datetime.today().date())).last()
        dog_req = dr
        td_dr = Team_Dog_Deployed.objects.exclude(team_requested = None).filter(team_requested = dr).filter(status = "Pending").filter(handler__in = working_handlers)

        #TODO add filter to td_dr for requests that start today. Celery na bahala sa pag pull out if hindi na confirm
        #TODO if td_dr is today, reveal for_arrival_request
        #TODO change Team_Dog_Deployed.status to "Deployed" if nag confirm si TL
    except: pass

    current_assignment = None
    if dog_req == None:
        current_assignment = ta
    else:
        current_assignment = dog_req

    if for_arrival:
        reveal_arrival = True

    if td_dr:
        reveal_for_arrival_request = True

    # print("For arrival")
    # print(for_arrival)

    check_arrival = CheckArrivalForm(request.POST or None, for_arrival=for_arrival)
    check_arrival_dr = CheckArrivalForm(request.POST or None, for_arrival=td_dr)

    print(ta)
    print(dr)

    if ta:
        current_location = tdd.filter(handler__status = 'Emergency Leave').exclude(status = "Deployed")
        print("CURRENT LOC")
        print(current_location)
    elif dr:
        current_location = td_dr.filter(handler__status = 'Emergency Leave').exclude(status = "Deployed")
    else:
        current_location = None

    # if current_location is None:
    #     check_arrival_emrgncy_leave = None
    # else:
    #     check_arrival_emrgncy_leave = CheckArrivalForm(request.POST or None, for_arrival=current_location)

    if current_location:
        check_arrival_emrgncy_leave = CheckArrivalForm(request.POST or None, for_arrival=current_location)
    else:
        check_arrival_emrgncy_leave = None


    events = Dog_Request.objects.filter(team_leader = user)

    year = datetime.now().year
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()

    if request.method == 'POST':
        if maritime_form.is_valid():
            maritime = maritime_form.save(commit = False)
            if ta:
                maritime.location = ta.location
            maritime.save()

        if form.is_valid():
            checks = geoform['point'].value()
            checked = ast.literal_eval(checks)

            toList = list(checked['coordinates'])

            print("Coordinates")
            print(toList)

            lon = Decimal(toList[0])
            lat = Decimal(toList[1])

            f = form.save(commit=False)
            f.longtitude = lon
            f.latitude = lat
            f.sector_type = "Small Event"

            delta = f.start_date - datetime.today().date()

            if delta.days >= 7:
                f.save()
            else:
                messages.success(request, 'Request must be atleast 1 week from today!')

            # location =
            #
            # if user.position == 'Operations' or user.position == 'Administrator':
            #     location.sector_type = "Big Event"
            #     location.status = "Approved"
            # else:
            #     location.sector_type = "Small Event"
            #
            # messages.success(request, 'Event succesfully saved!')
            # return redirect("profiles:team_leader_dashboard")


        if check_arrival.is_valid():

            handlers_arrived_id = check_arrival['team_member'].value()
            # print("Handlers Arrived")
            # print(handlers_arrived_id)

            handlers_arrived = User.objects.filter(pk__in = handlers_arrived_id)

            # NOTE: if this came from leave, transfer or init_dep:
            for handler in handlers_arrived:
                # try:
                deploy = Team_Dog_Deployed.objects.filter(handler = handler).filter(status = "Pending").last()
                
                if deploy:
                    deploy.status = "Deployed"
                    deploy.save()

                    Notification.objects.create(position='Handler', user=handler, notif_type='handler_arrival_to_port',
                                                message="Your arrival to port has been confirmed by your Team Leader.")
                # except: pass

            #Team Leader
            if ta:
                assign_TL(ta)
            messages.success(request, 'Arrival succesfully confirmed')
            return redirect("profiles:team_leader_dashboard")
        else:
            # print(check_arrival.errors)
            pass

        if check_arrival_dr.is_valid():

            handlers_arrived_id = check_arrival_dr['team_member'].value()
            # print("Handlers Arrived")
            # print(handlers_arrived_id)

            handlers_arrived = User.objects.filter(pk__in=handlers_arrived_id)

            for handler in handlers_arrived:
                try:
                    deploy = Team_Dog_Deployed.objects.filter(handler=handler).filter(status = "Pending").last()
                    deploy.status = "Deployed"
                    deploy.save()

                    Notification.objects.create(position='Handler', user=handler, notif_type='handler_arrival_to_request',
                                                message="Your arrival to the location of request has been confirmed by your Team Leader.")
                except:
                    pass

                try:
                    temp_handlers = Temporary_Handler.objects.filter(original = handler).filter(date_returned = None)

                    for temp_handler in temp_handlers:
                        temp_handler.date_returned = datetime.today().date()
                        temp_handler.save()
                except: pass

            # Team Leader

            messages.success(request, 'Arrival succesfully confirmed')
            return redirect("profiles:team_leader_dashboard")
        else:
            # print(check_arrival.errors)
            pass

        if check_arrival_emrgncy_leave.is_valid():

            handlers_arrived_id = check_arrival_emrgncy_leave['team_member'].value()
            # print("Handlers Arrived")
            # print(handlers_arrived_id)

            handlers_arrived = User.objects.filter(pk__in=handlers_arrived_id)

            for handler in handlers_arrived:
                # try:
                temp_handlers = Temporary_Handler.objects.filter(original = handler).filter(date_returned = None)

                for temp_handler in temp_handlers:
                    temp_handler.date_returned = datetime.today().date()
                    temp_handler.save()

                emergency_leaves = Emergency_Leave.objects.filter(handler = handler)#.filter(date_of_return = None)
                print("EMERGENCY LEAVES")
                print(emergency_leaves)
                for leave in emergency_leaves:
                    em= Emergency_Leave.objects.get(id=leave.id)
                    print("leave")
                    print(leave)
                    em.status = "Returned"
                    em.date_of_return =  datetime.today().date()
                    em.save()

                handler.status = "Working"
                handler.save()

                Notification.objects.create(position='Handler', user=handler, notif_type='handler_e_leave_return',
                                            message=str(user.fullname) + ' has confirmed your return from emergency leave.')
                # except:
                #     pass

            # Team Leader

            messages.success(request, 'Arrival succesfully confirmed')
            return redirect("profiles:team_leader_dashboard")
        else:
            # print(check_arrival.errors)
            pass

    cb = None
    try:
        cb = Call_Back_K9.objects.filter(k9__handler=user).last()
    except ObjectDoesNotExist:
        pass

    drf = Daily_Refresher.objects.filter(handler=user).filter(date=datetime.today().date())

    if drf.exists():
        dr = 1
    else:
        dr = 0


    try:
        rro = Replenishment_Request.objects.filter(handler=user).latest('id')
    except ObjectDoesNotExist:
        rro = None

    # print('rr',rro)
    context = {
        'incident_count':incident_count,
        'ta':ta,
        'tdd_count':tdd_count,
        'tdd':tdd,
        'year':year,

        'notif_data':notif_data,
        'count':count,
        'user':user,

        'k9' : k9,
        'form': form,
        'geoform': geoform,
        'geosearch': geosearch,
        'events': events,
        'cb':cb,
        'dr':dr,
        'rro':rro,
        'ki':ki,

        'for_arrival' : for_arrival,
        'check_arrival' : check_arrival,
        'reveal_arrival' : reveal_arrival,
        'reveal_for_arrival_request' : reveal_for_arrival_request,
        'check_arrival_dr' : check_arrival_dr,

        'upcoming_request' : dr,
        'check_arrival_emrgncy_leave' : check_arrival_emrgncy_leave,
        'maritime_form' : maritime_form,
        'temporary_care_k9s' : temporary_care_k9s,
        'current_assignment' : current_assignment,
        'dog_req' : dog_req

    }
    return render (request, 'profiles/team_leader_dashboard.html', context)


# Step 1
# Access this view/function when TL opens dashboard
def check_pre_deployment_items(user):
    all_clear = False
    items_list = [False]

    all_clear = True
    k9 = K9.objects.filter(handler = user).last()

    items_list = []

    collar = False
    vest = False
    leash = False
    shipping_crate = False
    food = False
    vitamins = False
    grooming_kit = False
    first_aid_kit = False
    oral_dextrose = False
    ball = False
    phex = False

    items_list.append(all_clear)

    try:
        checkup = PhysicalExam.objects.filter(dog=k9).latest('id')
        delta = datetime.today().date() - checkup.date
        if checkup.cleared == True and delta.days <= 90: #also checks if last checkup is within 3 months
            phex = True
    except: phex = False
    items_list.append((phex, "Physical Exam"))

    agg = Miscellaneous.objects.filter(miscellaneous__contains = "Collar").aggregate(Sum('quantity'))
    agg = agg['quantity__sum']
    if agg is None:
        agg = 0
    if agg >= 1:
        collar = True
    items_list.append((collar , "Collar"))

    agg = Miscellaneous.objects.filter(miscellaneous__contains = "Vest").aggregate(Sum('quantity'))
    agg = agg['quantity__sum']
    if agg is None:
        agg = 0
    if  agg >= 1:
        vest = True
    items_list.append((vest , "Vest"))

    agg = Miscellaneous.objects.filter(miscellaneous__contains="Leash").aggregate(Sum('quantity'))
    agg = agg['quantity__sum']
    if agg is None:
        agg = 0
    if agg >= 1:
        leash = True
    items_list.append((leash , "Leash"))

    agg = Miscellaneous.objects.filter(miscellaneous__contains="Shipping Crate").aggregate(Sum('quantity'))
    agg = agg['quantity__sum']
    if agg is None:
        agg = 0
    if agg >= 1:
        shipping_crate = True
    items_list.append((shipping_crate , "Shipping Crate"))

    agg = Food.objects.filter(foodtype = "Adult Dog Food").aggregate(Sum('quantity'))
    agg = agg['quantity__sum']
    if agg is None:
        agg = 0
    if agg >= 1:
        food = True
    items_list.append((food , "Dog Food"))

    medicines = Medicine.objects.filter(med_type = "Vitamins")
    agg = Medicine_Inventory.objects.filter(medicine__in = medicines).aggregate(Sum('quantity'))
    agg = agg['quantity__sum']
    if agg is None:
        agg = 0
    if agg >= 1:
        vitamins = True
    items_list.append((vitamins , "Vitamins"))

    agg = Miscellaneous.objects.filter(miscellaneous__contains="Grooming Kit").aggregate(Sum('quantity'))
    agg = agg['quantity__sum']
    if agg is None:
        agg = 0
    if agg >= 1:
        grooming_kit = True
    items_list.append((grooming_kit , "Grooming Kit"))

    agg = Miscellaneous.objects.filter(miscellaneous__contains="First Aid Kit").aggregate(Sum('quantity'))
    agg = agg['quantity__sum']
    if agg is None:
        agg = 0
    if agg >= 1:
        first_aid_kit = True
    items_list.append((first_aid_kit , "First Aid Kit"))

    agg = Miscellaneous.objects.filter(miscellaneous__contains="Oral Dextrose").aggregate(Sum('quantity'))
    agg = agg['quantity__sum']
    if agg is None:
        agg = 0
    if agg >= 1:
        oral_dextrose = True
    items_list.append((oral_dextrose , "Oral Dextrose"))

    agg = Miscellaneous.objects.filter(miscellaneous__contains="Ball").aggregate(Sum('quantity'))
    agg = agg['quantity__sum']
    if agg is None:
        agg = 0
    if agg >= 1:
        ball = True
    items_list.append((ball , "Ball"))

    #Check if items are complete

    check_list = [collar, vest, leash, shipping_crate, food, vitamins, grooming_kit, first_aid_kit, oral_dextrose, ball, phex]

    for item in check_list:
        if item == False:
            all_clear = False

    items_list[0] = all_clear

    return items_list


#Step 2
#Handler confirms items and will be part of the team officially deployed
def confirm_pre_deployment_items(request, k9):

    pre_deployment_items = K9_Pre_Deployment_Items.objects.filter(k9=k9).last()
    pre_deployment_items.status = "Confirmed"
    pre_deployment_items.save()

    subtract_inventory(k9.handler)

    return False

def handler_dashboard(request):

    user = user_session(request)
    form = RequestForm(request.POST or None)
    geoform = GeoForm(request.POST or None)
    geosearch = GeoSearch(request.POST or None)

    emergency_leave_form = EmergencyLeaveForm(request.POST or None)


    dr = 0
    k9 = None
    training_sched = None
    training = None

    pre_deployment_items = False
    all_clear = False
    reveal_items = False

    k9 = None
    ki = None
    try:
        k9 = K9.objects.get(handler=user)
        ki = K9_Incident.objects.filter(Q(incident='Stolen') | Q(incident='Accident') | Q(incident='Lost')).filter(k9=k9).filter(status='Pending').last()

    except:
        k9 = K9.objects.filter(handler=user).last()
    

    upcoming_deployment = None
    current_assignment = None
    current_port = None
    current_request = None

    try:
        current_assignment = Team_Dog_Deployed.objects.filter(k9=k9).filter(date_pulled = None).last()

        if current_assignment.team_assignment is not None:
            current_port = current_assignment.team_assignment
        elif current_assignment.team_requested is not None:
            current_request = current_assignment.team_requested

        upcoming_sched = K9_Schedule.objects.exclude(dog_request = None).exclude(date_start__lte = date.today()).filter(k9 = k9).first()
        if upcoming_sched:
            upcoming_deployment = upcoming_sched.dog_request

    except:
        pass

    # print("Current Port")
    # print(current_port)
    # print("Current Request")
    # print(current_request)

    today = datetime.today()

    k9_schedules = None
    events = None
    show_start = None
    show_end = None

    items_list = []
    if k9 is not None:
        if k9.training_status == "For-Deployment":

            items_list = check_pre_deployment_items(user)
            all_clear = items_list[0]

            del items_list[0]

            # print("Items List")
            # print(items_list)

            pre_deployment_items = K9_Pre_Deployment_Items.objects.filter(k9=k9).last()
            delta = None
            if pre_deployment_items:
                initial_sched = pre_deployment_items.initial_sched

                delta = initial_sched.date_start - today.date()

                if delta.days <= 7 and k9.training_status == "For-Deployment" and pre_deployment_items.status == "Pending": #1 week before deployment
                    reveal_items = True


        # TODO try except for when handler does not yet have a k9
        # TODO try except for when k9s still don't have a skill
        # TODO try except when k9 has finished training

        try:
            training = Training.objects.filter(k9=k9, training=k9.capability).last()
            if training.stage != "Finished Training":
                # print("TRAINING STAGE")
                # print(training.stage)
                training_sched = Training_Schedule.objects.filter(stage=training.stage).filter(k9=k9).last()

                # print("Training Sched")
                # print(training_sched.date_start)
                # print(training_sched.date_end)

            # print("ALL CLEAR")
            # print(all_clear)
            # print("REVEAL ITEMS")
            # print(reveal_items)
        except:
            pass

        drf = Daily_Refresher.objects.filter(handler=user).filter(date=datetime.today().date())

        if drf.exists():
            dr = 1
        else:
            dr = 0

        show_start = False
        show_end = False

        if request.method == 'POST':
            start_training = request.POST.get('start_training')
            end_training = request.POST.get('end_training')

            confirm_deployment = request.POST.get('confirm_deployment')
            if confirm_deployment:
                confirm_pre_deployment_items(request, k9)
                return redirect("profiles:handler_dashboard")

            if start_training:
                # print("START TRAINING VALUE")
                # print(start_training)

                try:
                    training_sched.date_start = today
                    training_sched.save()
                except: pass
            if end_training:
                # print("END TRAINING VALUE")
                # print(end_training)

                try:
                    training_sched.date_end = today
                    training_sched.save()
                except: pass

            if form.is_valid():
                checks = geoform['point'].value()
                checked = ast.literal_eval(checks)

                toList = list(checked['coordinates'])

                lon = Decimal(toList[0])
                lat = Decimal(toList[1])

                f = form.save(commit=False)
                f.longtitude = lon
                f.latitude = lat
                f.save()

                messages.success(request, 'event')
                return redirect("profiles:handler_dashboard")

            if emergency_leave_form.is_valid():
                emergency_leave = emergency_leave_form.save(commit = False)
                emergency_leave.handler = user
                emergency_leave.date_of_leave = today.date()
                emergency_leave.save()

                user.status = "Emergency Leave"
                user.save()
                if current_port:
                    Team_Dog_Deployed.objects.create(team_assignment=current_port, handler=user, k9=k9,
                                                           status="Pending")
                # check_leave_window(True, user)

                Notification.objects.create(position='Administrator', user=None, notif_type='admin_e_leave_request',
                                            message=str(user.fullname) + ' went on an emergency leave.')

                if current_port is not None:
                    Notification.objects.create(position='Team Leader', user=current_port.team_leader, notif_type='TL_e_leave_request',
                                            message=str(user.fullname) + ' went on an emergency leave.')
                if current_request is not None:
                    Notification.objects.create(position='Team Leader', user=current_request.team_leader, notif_type='TL_e_leave_request',
                                                message=str(user.fullname) + ' went on an emergency leave.')



        k9_schedules = K9_Schedule.objects.filter(k9 = k9)
        # print("K9 Schedules")
        # for sched in k9_schedules:
            # print(sched.status)

        try:
            if training_sched.date_start is None and training_sched.date_end is None:
                show_start = True

            elif training_sched.date_start is not None and training_sched.date_end is None:
                show_end = True

            elif training_sched.date_start is not None and training_sched.date_end is not None:
                show_start = True
                show_end = True

            else:
                    pass
        except:
            pass

    cb = None
    try:
        cb = Call_Back_K9.objects.filter(k9__handler=user).last()
    except ObjectDoesNotExist:
        pass

    # cb_handler = None
    # try:
    #     cb_handler = Call_Back_Handler.objects.filter(handler = user).filter(status = "Pending").last()
    # except:
    #     pass

    emergency_leave_count = Emergency_Leave.objects.filter(handler = user).filter(status = "Ongoing").count()
    print("EMERGENCY LEAVE COUNT")
    print(emergency_leave_count)

    # print("Show Start")
    # print(show_start)
    # print("Show End")
    # print(show_end)
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'k9':k9,
        'cb':cb,
        'dr':dr,
        'form': form,
        'geoform': geoform,
        'geosearch': geosearch,
        # 'events': events,
        'today': date.today(),
        'show_start': show_start,
        'show_end': show_end,
        'training_sched' : training_sched,
        'ki' : ki,

        'pre_deployment_item' : pre_deployment_items,
        'reveal_items' : reveal_items,
        'all_clear' : all_clear,
        'items_list' : items_list,

        'k9_schedules' : k9_schedules,
        'current_port' : current_port,
        'current_request' : current_request,
        'upcoming_deployment' : upcoming_deployment,

        'emergency_leave_form' : emergency_leave_form,
        'emergency_leave_count' : emergency_leave_count,
        # 'cb_handler' : cb_handler
    }
    return render (request, 'profiles/handler_dashboard.html', context)

def vet_dashboard(request):

    user = user_session(request)
    today = datetime.today()

    vac_pending = VaccinceRecord.objects.filter(Q(dhppil_cv_1=False) | Q(dhppil_cv_2=False) | Q(dhppil_cv_3=False) | Q(anti_rabies=False) | Q(bordetella_1=False) | Q(bordetella_2=False) | Q(dhppil4_1=False) | Q(dhppil4_2=False)).count()

    #TODO Physical Exam
    checkups = K9_Schedule.objects.filter(status = "Checkup").exclude(date_start__lt=datetime.today().date())

    k9_list = []
    for sched in checkups:
        k9_list.append(sched.k9)

    #TODO show k9 if there are no valid checkups

    k9_exclude_list = [] #Does not need to be
    for k9 in k9_list:
        try:
            checkup = PhysicalExam.objects.filter(dog=k9).last()  # TODO Also check if validity is worth 3 months

            delta = datetime.today().date() - checkup.date
            if checkup.cleared == True and delta.days <= 90: #3 months
                k9_exclude_list.append(k9)
                # print(checkup.cleared)
                # print(delta.days)
        except:
            pass

    #k9 schedule = checkups, checkup list
    checkups = checkups.exclude(k9__in = k9_exclude_list)

    checkup_list = []
    k9_list = []
    for checkup in checkups:
        if checkup.date_start == datetime.today().date():
            checkup_list.append(checkup)
            k9_list.append(checkup.k9)


    checkup_now = len(checkup_list)
    checkup_upcoming = checkups.exclude(k9__in = k9_list).count()
    # print('checkup', checkup_now,checkup_upcoming)

    #k9 to be scheduled for checkup

    #health pending
    h_c = K9_Incident.objects.filter(incident='Sick').filter(status='Pending').count()
    hh =  K9_Incident.objects.filter(incident='Sick').filter(status='Pending')
    th_c = Transaction_Health.objects.filter(status='Pending').exclude(follow_up__in=hh).count()
    health_pending = h_c +th_c
    # pending incidents
    incident =  K9_Incident.objects.filter(incident='Accident').filter(status='Pending').count()

    # Mated K9's
    mated_count = K9_Mated.objects.filter(status='Breeding').count()
    # pregnant K9's
    pregnant_count = K9_Mated.objects.filter(status='Pregnant').count()


    #Initial Vaccinations
    i_vac =  VaccinceRecord.objects.filter(status='Pending')

    #For Adoption
    for_adopt_count =  K9.objects.filter(training_status='For-Adoption').count()

    # for i in i_vac:

    events = K9_Schedule.objects.filter(status = "Checkup")

    #Vaccine Yearly
    vr = VaccinceRecord.objects.filter(deworming_4=True,dhppil_cv_3=True,anti_rabies=True,bordetella_2=True,dhppil4_2=True)

    list_k9 = []

    for v in vr:
        list_k9.append(v.k9.id)

    k9 = K9.objects.exclude(status="Adopted").exclude(status="Dead").exclude(status="Stolen").exclude(status="Lost").filter(id__in=list_k9)

    yearly = []

    for k9 in k9:
        try:
            ar = VaccineUsed.objects.filter(disease__contains='Anti-Rabies').filter(k9=k9).latest('date_vaccinated')
            nxt_ar = ar.date_vaccinated + relativedelta(years=+1)
        except ObjectDoesNotExist:
            nxt_ar = None

        try:
            br = VaccineUsed.objects.filter(disease__contains='Bordetella').filter(k9=k9).latest('date_vaccinated')
            nxt_br = br.date_vaccinated + relativedelta(years=+1)
        except ObjectDoesNotExist:
            nxt_br = None

        try:
            dh = VaccineUsed.objects.filter(disease__contains='DHPPiL4').filter(k9=k9).latest('date_vaccinated')
            nxt_dh = dh.date_vaccinated + relativedelta(years=+1)
        except ObjectDoesNotExist:
           nxt_dh = None

        try:
            dw = VaccineUsed.objects.filter(disease__contains='Deworming').filter(k9=k9).latest('date_vaccinated')
            nxt_dw = dw.date_vaccinated + relativedelta(months=+3)
        except ObjectDoesNotExist:
            nxt_dw = None

        if nxt_ar != None:
            if nxt_ar <= date.today():
                yearly.append('Anti-Rabies')

        if nxt_br != None:
            if nxt_br <= date.today():
                yearly.append('Bordetella')

        if nxt_dh != None:
            if nxt_dh <= date.today():
                yearly.append('DHPPiL4')

        if nxt_dw != None:
            if nxt_dw <= date.today():
                yearly.append('Deworming')


    # print(yearly)

    kd_index = pd.Index(yearly)
    y_values = kd_index.value_counts().keys().tolist()
    y_counts = kd_index.value_counts().tolist()

    # print('value', y_values)
    # print('count', y_counts)

    yearly_list = zip(y_values,y_counts)
    yearly_count = sum(y_counts)

    #preventive health program vaccination
    vr = VaccinceRecord.objects.filter(status='Pending')

    php_vac = []
    for vr in vr:
        #2 weeks
        if vr.deworming_1 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=14:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='1st Deworming')
                php_vac.append('Deworming')
        #4 weeks
        if vr.deworming_2 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=24:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='2nd Deworming')
                dwd = [k9,vu]
                php_vac.append('Deworming')
        #6 weeks
        if vr.deworming_3 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=42:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='3rd Deworming')
                dwd = [k9,vu]
                php_vac.append('Deworming')
        #6 weeks
        if vr.dhppil_cv_1 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=42:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='1st dose DHPPiL+CV Vaccination')
                php_vac.append('DHPPiL+CV')
        #6 weeks
        if vr.heartworm_1 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=42:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='1st Heartworm Prevention')
                php_vac.append('Heartworm')
        #8 weeks
        if vr.bordetella_1 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=56:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='1st dose Bordetella Bronchiseptica Bacterin')
                php_vac.append('Bordetella Bronchiseptica Bacterin')

        #8 weeks
        if vr.tick_flea_1 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=42:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='1st Tick and Flea Prevention')
                php_vac.append('Tick and Flea')


        #9 weeks
        if vr.dhppil_cv_2 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=63:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='2nd dose DHPPiL+CV')
                php_vac.append('DHPPiL+CV')
        #9 weeks
        if vr.deworming_3 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=63:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='4th Deworming')
                php_vac.append('Deworming')

        #10 weeks
        if vr.heartworm_2 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=63:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='2nd Heartworm Prevention')
                php_vac.append('Heartworm')
        #11 weeks
        if vr.bordetella_2 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=63:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='2nd dose Bordetella Bronchiseptica Bacterin')
                php_vac.append('Bordetella Bronchiseptica Bacterin')
        #12 weeks
        if vr.anti_rabies == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=84:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='Anti-Rabies Vaccination')
                php_vac.append('Anti-Rabies')

        #12 weeks
        if vr.tick_flea_2 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=84:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='2nd Tick and Flea Prevention')
                php_vac.append('Tick and Flea')

        #12 weeks
        if vr.dhppil_cv_3 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=84:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='3rd dose DHPPiL+CV Vaccination')
                php_vac.append('DHPPiL+CV')

        #14 weeks
        if vr.heartworm_3 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=98:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='3rd Heartworm Prevention')
                php_vac.append('Heartworm')

        #15 weeks
        if vr.dhppil4_1 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=105:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='1st dose DHPPiL4 Vaccination')
                php_vac.append('DHPPiL4')
        #16 weeks
        if vr.tick_flea_3 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=112:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='3rd Tick and Flea Prevention')
                php_vac.append('Tick and Flea')

        #18 weeks
        if vr.dhppil4_2 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=126:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='2nd dose DHPPiL4 Vaccination')
                php_vac.append('DHPPiL4')

        #18 weeks
        if vr.heartworm_4 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=126:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='4th Heartworm Prevention')
                dwd = [k9,vu]
                php_vac.append('Heartworm')

        #20 weeks
        if vr.tick_flea_4 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=140:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='4th Tick and Flea Prevention')
                php_vac.append('Tick and Flea')
        #22 weeks
        if vr.heartworm_5 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=154:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='5th Heartworm Prevention')
                php_vac.append('Heartworm')

        #24 weeks
        if vr.tick_flea_5 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=168:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='5th Tick and Flea Prevention')
                php_vac.append('Tick and Flea')
        #26 weeks
        if vr.heartworm_6 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=182:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='6th Heartworm Prevention')
                php_vac.append('Heartworm')

        #28 weeks
        if vr.tick_flea_6 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=196:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='6th Tick and Flea Prevention')
                php_vac.append('Tick and Flea')

        #30 weeks
        if vr.heartworm_7 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=210:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='7th Heartworm Prevention')
                php_vac.append('Heartworm')
        #32 weeks
        if vr.tick_flea_7 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=224:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='7th Tick and Flea Prevention')
                php_vac.append('Tick and Flea')

        #34 weeks
        if vr.heartworm_8 == False:
            k9 = K9.objects.get(id=vr.k9.id)
            if k9.age_days >=238:
                vu = VaccineUsed.objects.filter(vaccine_record=vr).get(disease='8th Heartworm Prevention')
                php_vac.append('Heartworm')

    php_vacc = np.sort(php_vac)

    vac_index = pd.Index(php_vacc)
    vac_values = vac_index.value_counts().keys().tolist()
    vac_counts = vac_index.value_counts().tolist()

    vac_list = zip(vac_values,vac_counts)
    vac_count = sum(vac_counts)

    ab = None
    try:
        ab = Actual_Budget.objects.filter(year_budgeted__year=datetime.today().year).last()

        aq = K9.objects.filter(date_created__year=datetime.today().year).count()

        ab_k9 = (ab.k9_needed + ab.k9_breeded) - aq

        if ab_k9 < 0:
            ab_k9 = 0

        ab_total = ab.others_total + ab.kennel_total + ab.vet_supply_total + ab.medicine_total + ab.vac_prev_total + ab.food_milk_total + ab.petty_cash
    except:
        ab_k9 = 0
        ab_total = None

    classify_count = K9.objects.filter(status='Material Dog').filter(training_status='Trained').count()

    current_appointments = K9_Schedule.objects.filter(status="Checkup").exclude(date_start__lt=datetime.today().date())
    k9s_exclude = []
    for item in current_appointments:
        k9s_exclude.append(item.k9)

    cancelled_init_dep = K9_Pre_Deployment_Items.objects.filter(status="Cancelled")
    for item in cancelled_init_dep:
        k9s_exclude.append(item.k9)

    pending_schedule = K9_Schedule.objects.filter(status="Initial Deployment").exclude(k9__in=k9s_exclude).exclude(
        date_start__lt=datetime.today().date()).count()

    unfit_count = K9.objects.filter(fit=False).count()

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'for_adopt_count':for_adopt_count,
        'mated_count':mated_count,
        'pregnant_count':pregnant_count,
        'vac_pending':vac_pending,
        'health_pending':health_pending,
        'incident':incident,
        'events' : events,
        'yearly_list':yearly_list,
        'yearly_count':yearly_count,
        'vac_list':vac_list,
        'vac_count':vac_count,
        'ab_k9':ab_k9,
        'checkup_now':checkup_now,
        'checkup_upcoming':checkup_upcoming,
        'classify_count':classify_count,
        'pending_schedule' : pending_schedule,
        'unfit_count':unfit_count,
    }
    return render (request, 'profiles/vet_dashboard.html', context)

def commander_dashboard(request):
    user = user_session(request)

    area_list = []
    areas = Area.objects.filter(commander = user).last()
    location = Location.objects.filter(area=areas)

    c_list = []
    for l in location:
        c_list.append(l.city)

    loc_u = np.unique(c_list)

    events = Dog_Request.objects.filter(area= areas)


    data = Dog_Request.objects.all()
    data = data.filter(area=areas)

    pending_sched = data.filter(status='Pending').exclude(start_date__lt = datetime.today().date()).count()

    # print(pending_sched)
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'events' : events,
        'areas' : areas,
        'pending_sched' : pending_sched,
    }
    return render (request, 'profiles/commander_dashboard.html', context)

def operations_dashboard(request):
    style = ""
    user = user_session(request)

    form = RequestForm(request.POST or None)

    geoform = GeoForm(request.POST or None)
    geosearch = GeoSearch(request.POST or None)
    width = 650

    events = Dog_Request.objects.filter(sector_type = "Big Event")

    rq = Dog_Request.objects.filter(sector_type = "Big Event").exclude(end_date__lt=datetime.today().date()).count()

    if request.method == 'POST':
        # print(form.errors)
        # form.validate_date()
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
            account = Account.objects.filter(serial_number=serial).last()
            user_in_session = User.objects.filter(id=account.UserID.id).last()


            if location.sector_type != "Disaster":
                if user_in_session.position == 'Operations' or  user_in_session.position == 'Administrator':
                    location.sector_type = "Big Event"
                    location.status = "Approved"
                else:
                    location.sector_type = "Small Event"


            location.save()

            style = "ui green message"
            messages.success(request, 'Request has been successfully Added!')
            return redirect('profiles:operations_dashboard')
        else:
            print(form.errors)
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,

        'form': form,
        'geoform': geoform,
        'geosearch': geosearch,
        'width' :width,

        'events' : events,
        'rq' : rq,
        'style' : style
    }
    return render (request, 'profiles/operations_dashboard.html', context)

def trainer_dashboard(request):
    user = user_session(request)

    k9s_for_grading = []
    train_sched = Training_Schedule.objects.exclude(date_start=None).exclude(date_end=None)

    for item in train_sched:
        if item.k9.training_level == item.stage:
            k9s_for_grading.append(item.k9.id)

    grade = K9.objects.filter(id__in=k9s_for_grading).count()
    unclassified = K9.objects.filter(training_status='Unclassified').count()

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'grade':grade,
        'unclassified':unclassified,
    }
    return render (request, 'profiles/trainer_dashboard.html', context)

def profile(request):

    # first_day = datetime.date.today().replace(day=1)
    # last_day = datetime.date.today().replace(day=calendar.monthrange(datetime.date.today().year, datetime.date.today().month)[1])

    # print(first_day, last_day)
    # phex = PhysicalExam.objects.filter(date_next_exam__range=[first_day, last_day])
    # vac = VaccinceRecord.objects.filter(date_validity__range=[first_day, last_day])
    # list = zip(phex,vac)
    today = datetime.today()

    serial = request.session['session_serial']
    # print(serial)

    account = Account.objects.filter(serial_number=serial).last()
    user = User.objects.filter(id = account.UserID.id).last()
    p_info = Personal_Info.objects.filter(UserID=user).last()
    e_info = Education.objects.filter(UserID=user).last()

    # print(account.UserID.position)

    uform = add_User_form(request.POST or None,  request.FILES or None, instance = user)
    pform = add_personal_form(request.POST or None, instance = p_info)
    eform = add_education_form(request.POST or None, instance = e_info)

    if request.method == 'POST':
        # print(uform.errors)
        if uform.is_valid():
            # print(pform.errors)
            if pform.is_valid():
                # print(eform.errors)
                if eform.is_valid():
                    if uform.status == 'No Longer Employed':
                        uform.partnered = False
                        try:
                            k9 = K9.objects.filter(handler=uform).last()
                            k9.handler = None
                            k9.save()
                        except:
                            pass

                    uform.save()
                    pform.save()
                    eform.save()
                    messages.success(request, 'Your Profile has been successfully Updated!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()

    context={
        # 'phex': phex,
        # 'vac': vac,
        # 'list': list,
        'today': today,
        'uform':uform,
        'pform': pform,
        'eform': eform,
        'user':user,
        'notif_data':notif_data,
        'count':count,
    }
    return render (request, 'profiles/profile.html', context)

def register(request):
    mass_populate_revisited()

    #MAKE USER
    # for i in range(5):
    #     #user,account, education, personal info
    #     user = User.objects.create(position='Handler',rank='MCPO',firstname='Ron'+str(i),lastname='Last'+str(i),middlename='N'+str(i),birthdate=date.today(),gender='Male',civilstatus='Single', citizenship='FILIPINO' ,religion='Roman Catholic', bloodtype='A', status='Working', partnered=True)
        
    #     #k9
    #     k9 = K9.objects.create(name='Lola'+str(i), handler=user, breed='Jack Russel',sex='Female',color='Cream', birth_date=date.today(),source='Procurement',status='Working Dog',training_status='For-Deployment',height=20,weight=20)

    #     print(user, k9)
        
    #MAKE K9
    return render (request, 'profiles/register.html')

def home(request):
    id = request.user.id

    user = User.objects.filter(id =id).last()

    request.session["session_serial"] = request.user.username
    request.session["session_user_position"] = user.position
    request.session["session_id"] = user.id
    request.session["session_username"] = str(user)

    if user.position == 'Team Leader':
        return HttpResponseRedirect('../team-leader-dashboard')
    elif user.position == 'Handler':
        return HttpResponseRedirect('../handler-dashboard')
    elif user.position == 'Veterinarian':
        return HttpResponseRedirect('../vet-dashboard')
    else:
        return HttpResponseRedirect('../dashboard')

def logout(request):
    session_keys = list(request.session.keys())
    for key in session_keys:
        del request.session[key]
    return redirect('profiles:login')

def login(request):

    if request.method == 'POST':
        task_to_dash_dep()
        task_to_dash_um()
        task_to_dash_pq()

        serial = request.POST['serial_number']
        password = request.POST['password']
        # user_auth = authenticate(request, username=serial, password=password)
        # print(password)

        # auth_login(request, user_auth)
        request.session["session_serial"] = serial
        account = Account.objects.filter(serial_number = serial).last()
        user = User.objects.filter(id = account.UserID.id).last()

        request.session["session_user_position"] = user.position
        request.session["session_id"] = user.id
        request.session["partnered"] = user.partnered
        request.session["session_username"] = str(user)

        # print(request.session["partnered"])
        #TRAINOR, OPERATIONS
        if user.position == 'Aministrator':
            return HttpResponseRedirect('../dashboard')
        elif user.position == 'Veterinarian':
            return HttpResponseRedirect('../vet-dashboard')
        elif user.position == 'Team Leader':
            return HttpResponseRedirect('../team-leader-dashboard')
        elif user.position == 'Handler':
            return HttpResponseRedirect('../handler-dashboard')
        elif user.position == 'Commander':
            return HttpResponseRedirect('../commander-dashboard')
        elif user.position == 'Operations':
            return HttpResponseRedirect('../operations-dashboard')
        elif user.position == 'Trainer':
            return HttpResponseRedirect('../trainer-dashboard')

        else:
            return HttpResponseRedirect('../dashboard')

    return render (request, 'profiles/login.html')

def add_User(request):

    form = add_User_form(request.POST, request.FILES)
    style = ""

    if request.method == 'POST':
        # print(form.errors)
        if form.is_valid():
            new_form = form.save()
            formID = new_form.pk
            request.session["session_userid"] = formID

            '''style = "ui green message"
            messages.success(request, 'User has been successfully Added!')'''

            return HttpResponseRedirect('add_personal_form/')

        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title': "Add User Form",
        'form': form,
        'style': style,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }

    return render(request, 'profiles/add_User.html', context)


def add_personal_info(request):
    form = add_personal_form(request.POST)
    style = ""
    if request.method == 'POST':
        # print(form.errors)
        if form.is_valid():
            personal_info = form.save(commit=False)
            UserID = request.session["session_userid"]
            user_s = User.objects.filter(id=UserID).last()
            personal_info.UserID = user_s
            personal_info.save()
            '''style = "ui green message"
            messages.success(request, 'User has been successfully Added!')'''
            form = add_User_form

            return HttpResponseRedirect('add_education/')
        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    user_s = User.objects.filter(id=request.session["session_userid"]).last()
    user_name = str(user_s)
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title': "Add Personal Information for " + user_name,
        'form': form,
        'style': style,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render(request, 'profiles/add_personal_info.html', context)

def add_education(request):
    form = add_education_form(request.POST)
    style = ""
    if request.method == 'POST':

        if form.is_valid():
            personal_info = form.save(commit=False)
            UserID = request.session["session_userid"]
            user_s = User.objects.filter(id=UserID).last()
            personal_info.UserID = user_s
            personal_info.save()
            '''style = "ui green message"
            messages.success(request, 'User has been successfully Added!')'''

            return HttpResponseRedirect('add_user_account/')

        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    user_s = User.objects.filter(id=request.session["session_userid"]).last()
    user_name = str(user_s)
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title': "Add Education Information for " + user_name,
        'form': form,
        'style': style,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render(request, 'profiles/add_education.html', context)


def add_user_account(request):
    form = add_user_account_form(request.POST or None)
    form2 = UserCreationForm(request.POST or None)
    style = ""

    UserID = request.session["session_userid"]
    data = User.objects.filter(id=UserID).last()

    if request.method == 'POST':
        if form.is_valid():
            form = form.save(commit=False)
            form.UserID = data
            form.serial_number = 'O-' + str(data.id)
            # form.save()

            AuthUser.objects.create_user(username=form.serial_number, email=form.email_address, password=form.password,last_name=data.lastname, first_name=data.firstname)

            return HttpResponseRedirect('../../../../user_add_confirmed/')

        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    # NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title': "Add Account Information for " + data.fullname,
        'form': form,
        'style': style,
        'notif_data': notif_data,
        'count': count,
        'user': user,
    }
    return render(request, 'profiles/add_user_account.html', context)

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title': "Add Account Information for " + data.fullname,
        'form': form,
        'style': style,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render(request, 'profiles/add_user_account.html', context)

#Listview format
def user_listview(request):
    user_s = User.objects.all()
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    style = "ui green message"

    if request.method == 'POST':
        date = request.POST.get('date_input')
        status = request.POST.get('status_input')
        handler_id = request.POST.get('id_input')

        u = User.objects.filter(id=handler_id).last()
        u.retire_quit_died = date
        u.partnered = False
        u.assigned = False

        if status == 'Quit':
            u.status = 'No Longer Employed'

        u.save()

        try:
            k = K9.objects.filter(handler=u).last()
            k.handler = None
            k.save()
        except:
            pass

        messages.success(request, 'User status has been updated to '+ u.status +'!')


    context = {
        'Title' : 'User List',
        'style':style,
        'user_s' : user_s,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }

    return render(request, 'profiles/user_list.html', context)

#Detailview format
def user_detailview(request, id):
    user_s = User.objects.filter(id = id).last()
    personal_info = Personal_Info.objects.filter(UserID = id).last()
    education = Education.objects.filter(UserID=id).last()
    account = Account.objects.filter(UserID=id).last()

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title': 'User Details',
        'user_s' : user_s,
        'personal_info': personal_info,
        'education': education,
        'account': account,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }

    return render(request, 'profiles/user_detail.html', context)

#Detailview format
def user_add_confirmed(request):
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render(request, 'profiles/user_add_confirmed.html', context)


def load_event(request):

    id = request.GET.get('event_id')
    # print("ID RECEIVED")
    # print(id)

    dog_request = None
    try:
        dog_request = Dog_Request.objects.filter(id = id).last()
    except: pass

    context = {
        'dog_request' : dog_request
    }

    return render(request, 'profiles/load_event.html', context)

def load_event_handler(request):
    id = request.GET.get('event_id')
    # print("ID RECEIVED")
    # print(id)
    sched = None
    try:
        sched = K9_Schedule.objects.filter(id = id).last()
    except: pass
    context = {
      'sched' : sched
    }

    return render(request, 'profiles/load_event_handler.html', context)


def unconfirmed_pre_req(request):

    pre_dep = K9_Pre_Deployment_Items.objects.filter(status = None)



    return None

class ScheduleView(APIView):
    def get(self, request, format=None):
        user = user_session(request)

        today = datetime.now()
        # print(date.today())

        k9 = K9.objects.get(handler=user)
        sched = K9_Schedule.objects.filter(k9=k9).filter(date_end__gte= today)

        sched_items = []

        for items in sched:
            i = [items.dog_request.location, items.date_start, items.date_end]
            sched_items.append(i)

        data = {
            "sched_items":sched_items,
        }
        return Response(data)

#TODO
class NotificationListView(APIView):

    def get(self, request):
        user_serial = request.session['session_serial']
        user = Account.objects.get(serial_number=user_serial)
        current_user = User.objects.get(id=user.UserID.id)

        #TODO
        if current_user.position == 'Handler':
            k9 = K9.objects.get(handler=current_user)
            notif = Notification.objects.filter(k9=k9)
        else:
            notif = Notification.objects.filter(position=current_user.position)

        serializer = NotificationSerializer(notif, many=True)
        return Response(serializer.data)

    def put(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationDetailView(APIView):
    def get(self, request, id):
        notif = get_object_or_404(Notification, id=id)
        serializer = NotificationSerializer(notif)
        return Response(serializer.data)

    def delete(self, request, id):
        notif = get_object_or_404(Notification, id=id)
        notif.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def update_event(request):

    event = None

    event_id = request.GET.get('event_id')
    event_start = request.GET.get('event_start')
    event_end = request.GET.get('event_end')
    event_title = request.GET.get('event_title')
    event_allDay = request.GET.get('event_allDay')
    event_allDay = event_allDay.capitalize()
    python_date_start = datetime.fromtimestamp(int(event_start))
    if event_end is not None:
        python_date_end = datetime.fromtimestamp(int(event_end))
        # if python_date_start.day == python_date_end.day:
        #     python_date_end = python_date_end + relativedelta.relativedelta(days=1)
    else:
        python_date_end = python_date_start
        #python_date_end = python_date_end + relativedelta.relativedelta(days=1)


    # print("ID : " + event_id)
    # print("TITLE : " + event_title)
    # print("START : " + str(python_date_start))
    # print("END : " + str(python_date_end))
    # print("ALLDAY : " + event_allDay)

    try:
        event = Events.objects.get(id=event_id)
        event.event_name = event_title
        event.start_date = python_date_start
        event.end_date = python_date_end

        event.all_day = event_allDay
        event.save()
    except: pass


    context = {"event": event}

    return render(request, 'module/something.html', context)


class UserView(viewsets.ModelViewSet):
    queryset = AuthUser.objects.all()
    serializer_class = UserSerializer
