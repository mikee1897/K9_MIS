from django.shortcuts import render
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_date
from dateutil.relativedelta import relativedelta
from .models import K9, K9_Past_Owner, K9_Donated, K9_Parent, K9_Quantity, Dog_Breed, K9_Supplier, K9_Litter, K9_Mated
from .forms import add_donated_K9_form, add_donator_form, add_K9_parents_form, add_offspring_K9_form, select_breeder, K9SupplierForm, date_mated_form, HistDateForm, DateForm,DateK9Form
from django.db.models import F
from .forms import add_donated_K9_form, add_donator_form, add_K9_parents_form, add_offspring_K9_form, select_breeder, K9SupplierForm, date_mated_form, add_breed_form
from .models import K9, K9_Past_Owner, K9_Donated, K9_Parent, K9_Quantity, K9_Supplier, K9_Litter
from .models import K9_Mated
from .forms import DateForm
from deployment.models import Incidents, Daily_Refresher, Team_Dog_Deployed, Maritime, Area, Location
from planningandacquiring.models import Proposal_Budget, Proposal_K9,Proposal_Milk_Food, Proposal_Vac_Prev, Proposal_Medicine, Proposal_Vet_Supply, Proposal_Kennel_Supply, Proposal_Others, Actual_Budget, Actual_K9,Actual_Milk_Food, Actual_Vac_Prev, Actual_Medicine, Actual_Vet_Supply, Actual_Kennel_Supply, Actual_Others, Proposal_Training, Actual_Training

from django.db.models import Sum
from training.models import Training, Training_History, Training_Schedule
from profiles.models import Account, User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, inlineformset_factory, modelformset_factory
from django.http import JsonResponse
from django.contrib import messages
from .forms import ReportDateForm, k9_detail_form, SupplierForm, ProcuredK9Form,k9_acquisition_form
from deployment.models import Dog_Request, Team_Assignment

from unitmanagement.models import Health, HealthMedicine, VaccinceRecord, VaccineUsed, Handler_On_Leave, Emergency_Leave
from inventory.models import Food, Food_Subtracted_Trail, Medicine, Medicine_Inventory, Medicine_Subtracted_Trail, Miscellaneous, Miscellaneous_Subtracted_Trail, Food_Received_Trail, Medicine_Received_Trail, Miscellaneous_Received_Trail

from unitmanagement.models import Health, HealthMedicine, VaccinceRecord, VaccineUsed, Notification, Handler_Incident,K9_Incident
from inventory.models import Food, Medicine, Medicine_Inventory, Medicine_Subtracted_Trail, Miscellaneous, Medicine_Received_Trail, Food_Received_Trail, Miscellaneous_Received_Trail, Medicine_Inventory_Count, Medicine_Received_Trail, Food_Inventory_Count, Food_Received_Trail, Miscellaneous_Inventory_Count, Miscellaneous_Received_Trail

from django.db.models.functions import Trunc, TruncMonth, TruncYear, TruncDay
from django.db.models import aggregates, Avg, Count, Min, Sum, Q, Max
import dateutil.parser

from training.models import K9_Adopted_Owner
#from faker import Faker

#statistical imports
from math import *
from decimal import Decimal
from sklearn.metrics import mean_squared_error


from datetime import datetime as dt

from datetime import timedelta

from itertools import chain

from datetime import date
import pandas as pd
import numpy as np

import math

# from faker import Faker
#
# #statistical imports
# from math import *
# from decimal import Decimal
# from sklearn.metrics import mean_squared_error
#
# #graphing imports
# from igraph import *
# import plotly.offline as opy
# import plotly.graph_objs as go
# import plotly.graph_objs.layout as lout
#
# #forecasting imports
# from statsmodels.tsa.ar_model import AR
# from statsmodels.tsa.arima_model import ARMA
# from statsmodels.tsa.arima_model import ARIMA
# from statsmodels.tsa.statespace.sarimax import SARIMAX
# from statsmodels.tsa.holtwinters import SimpleExpSmoothing
# from statsmodels.tsa.holtwinters import ExponentialSmoothing
# from random import random, randint
# from statsmodels.tsa.stattools import adfuller, kpss
# import statsmodels.api as sm

import math
# Create your views here.

def notif(request):
    serial = request.session['session_serial']
    account = Account.objects.get(serial_number=serial)
    user_in_session = User.objects.get(id=account.UserID.id)
    
    if user_in_session.position == 'Veterinarian':
        notif = Notification.objects.filter(position='Veterinarian').order_by('-datetime')
    elif user_in_session.position == 'Handler':
        notif = Notification.objects.filter(user=user_in_session).order_by('-datetime')
    else:
        notif = Notification.objects.filter(position='Administrator').order_by('-datetime')
   
    return notif

def user_session(request):
    serial = request.session['session_serial']
    account = Account.objects.get(serial_number=serial)
    user_in_session = User.objects.get(id=account.UserID.id)
    return user_in_session

def index(request):
    next_year = dt.now().year + 1
    current_year = dt.now().year

    stat = True
    all_k9 = K9.objects.exclude(status="Adopted").exclude(status="Dead").exclude(status="Stolen").exclude(status="Lost")
    print(stat)

    #K9 to be born and die
    k9_breeded = K9_Mated.objects.filter(status='Pregnant')
    print(k9_breeded)
    ny_breeding = [] 
    ny_data = []
    for kb in k9_breeded:
        m = kb.date_mated  + timedelta(days=63)
        if m.year == next_year:
            ny = [kb.mother.breed, kb.mother.litter_no]
            ny_data.append(ny)
            ny_breeding.append(kb.mother.breed)
            #get k9, value, total count by breed
            
    kb_index = pd.Index(ny_breeding)

    b_values = kb_index.value_counts().keys().tolist() #k9 breed to be born
    b_counts = kb_index.value_counts().tolist() #number of k9 to be born by breed

    #Total count of all dogs born next year by breed,
    breed_u = np.unique(ny_breeding)

    p = pd.DataFrame(ny_data, columns=['Breed', 'Litter'])
    h = p.groupby(['Breed']).sum()

    total_born = []  
    total_born_count = []  
    for u in breed_u:
        total_born_count.append(h.loc[u].values[0])
        born = [u,h.loc[u].values[0]]
        total_born.append(born)

    ny_dead = []
    for kd in all_k9:
        b = Dog_Breed.objects.get(breed = kd.breed)
        if (kd.age + 1) >= b.life_span:
            ny_dead.append(kd.breed)
            

    kd_index = pd.Index(ny_dead)

    d_values = kd_index.value_counts().keys().tolist()
    d_counts = kd_index.value_counts().tolist()

    all_k = all_k9.values_list('breed', flat=True).order_by()

    all_ku = np.unique(all_k)

    all_dogs = K9.objects.exclude(status="Adopted").exclude(status="Dead").exclude(status="Stolen").exclude(status="Lost").count()

    all_kk = []
    for a in all_ku:
        c = all_k9.filter(breed=a).count()
        cc = [a,c]
        all_kk.append(cc)

    k9_cy = all_dogs
    k9_ny = all_dogs - sum(d_counts)
    k9_t_ny = k9_cy+50

    difference_k9 = k9_cy - k9_ny
    born_ny=0
    for b in k9_breeded:
        d = Dog_Breed.objects.get(breed=b.mother.breed)
        born_ny = born_ny + d.litter_number

    # born_ny =  sum(total_born_count)

    need_procure_ny = (50 + difference_k9) - born_ny
    if need_procure_ny <= 0:
        need_procure_ny = 0

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)

    context = {

        'notif_data':notif_data,
        'count':count,
        'user':user,

    }

    return render(request, 'planningandacquiring/index.html', context)

def budgeting_list(request):

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)

    pb = Proposal_Budget.objects.all()
    data = []
    for pb in pb:
        ab = Actual_Budget.objects.filter(year_budgeted__year=pb.year_budgeted.year).last()
        x = [pb,ab]
        data.append(x)

    print(data)
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'data': data,
    }
    return render(request, 'planningandacquiring/budget_list.html', context)


def add_procured_k9(request):
    form = SupplierForm(request.POST or None)
    k9_formset = formset_factory(ProcuredK9Form, extra=1, can_delete=True)
    formset = k9_formset(request.POST, request.FILES)
    style = "ui green message"

    try:
        print(request.session['procured'])
    except:
        pass
    if request.method == "POST":
        if form.is_valid():
            supplier_data = form.cleaned_data['supplier']
            supplier = K9_Supplier.objects.get(name=supplier_data)

            if formset.is_valid():
                print("Formset is valid")
                for forms in formset:
                    cd = forms.cleaned_data
                    name = cd.get('name')
                    bday = cd.get('birth_date')
                    sex = cd.get('sex')
                    color = cd.get('color')
                    breed = cd.get('breed')
                    image = cd.get('image')
                    dhpp = cd.get('date_dhhp')
                    rabies = cd.get('date_rabies')
                    bordertella = cd.get('date_bordertela')
                    deworm = cd.get('date_deworm')
                    height = cd.get('height')
                    weight = cd.get('weight')

                    k9 = K9.objects.create(name=name,birth_date=bday,source='Procurement',training_status='Unclassified',sex=sex,color=color, breed=breed,height=height,weight=weight,image=image, supplier=supplier)
                    
                    VaccineUsed.objects.create(k9=k9,disease='DHPPiL4',date_vaccinated=dhpp,done=True)
                    
                    VaccineUsed.objects.create(k9=k9,disease='Anti-Rabies',date_vaccinated=rabies,done=True)
                    
                    VaccineUsed.objects.create(k9=k9,disease='Deworming',date_vaccinated=deworm,done=True)
                    
                    VaccineUsed.objects.create(k9=k9,disease='Bordetella',date_vaccinated=bordertella,done=True)
             
                style = "ui green message"
                messages.success(request, 'Procured K9s has been added!')
                
                return redirect('planningandacquiring:K9_list')
            else:
                print(formset.errors)
                style = "ui red message"
                messages.warning(request, 'Invalid input data!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title' : "Procured K9",
        'form': SupplierForm(),
        # 'formset':k9_formset(),
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'style':style,
        }
    return render (request, 'planningandacquiring/add_procured_k9.html', context)

def add_supplier(request):
    form = K9SupplierForm(request.POST)
    style = ''
    if request.method == 'POST':
        print(form.errors)
        if form.is_valid():
            form.save()

            style = "ui green message"
            messages.success(request, 'Supplier has been added!')
            form = K9SupplierForm()
        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

        form.initial['organization'] = None
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title' : "Add K9 Supplier",
        'texthelp' : "Please input the Supplier information below.",
        'form': form,
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'style':style,
        }
    return render (request, 'planningandacquiring/add_k9_supplier.html', context)

#Form format
def add_donated_K9(request):
    form = add_donated_K9_form(request.POST or None, request.FILES or None)
    style = "ui teal message"
    if request.method == 'POST':
        if form.is_valid():
            k9 = form.save()
            k9.training_status = "Unclassified"
            k9.source = "Procurement"
            k9.save()

            request.session['k9_id'] = k9.id


            return HttpResponseRedirect('confirm_donation/')

        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')
            print(form)

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title' : "Add New K9",
        'form' : form,
        'style': style,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }

    return render(request, 'planningandacquiring/add_donated_K9.html', context)

'''
def add_donator(request):
    form = add_donator_form(request.POST)
    style = "ui teal message"
    if request.method == 'POST':
        if form.is_valid():
            donator= form.save()

            request.session['donator_id'] = donator.id

            return HttpResponseRedirect('confirm_donation/')

        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    context = {
        'Title': "Receive Donated K9",
        'form': form,
        'style': style,
    }

    return render(request, 'planningandacquiring/add_donator.html', context)
'''

def confirm_donation(request):

    k9_id = request.session['k9_id']
    k9= K9.objects.get(id = k9_id)

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title': "Add New K9",
        'k9': k9,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render(request, 'planningandacquiring/confirm_K9_donation.html', context)

def donation_confirmed(request):
    k9_id = request.session['k9_id']

    k9 = K9.objects.get(id=k9_id)
    
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }

    if 'ok' in request.POST:
        VaccinceRecord.objects.create(k9=k9, deworming_1=True, deworming_2=True, deworming_3=True,
                                      deworming_4=True, dhppil_cv_1=True, dhppil_cv_2=True, dhppil_cv_3=True,
                                      heartworm_1=True, heartworm_2=True,
                                      heartworm_3=True, heartworm_4=True, heartworm_5=True, heartworm_6=True,
                                      heartworm_7=True, heartworm_8=True,
                                      anti_rabies=True, bordetella_1=True, bordetella_2=True, dhppil4_1=True,
                                      dhppil4_2=True, tick_flea_1=True,
                                      tick_flea_2=True, tick_flea_3=True, tick_flea_4=True, tick_flea_5=True,
                                      tick_flea_6=True, tick_flea_7=True)

        return render(request, 'planningandacquiring/donation_confirmed.html', context)
    else:
        #delete k9
        k9.delete()

        #NOTIF SHOW
        notif_data = notif(request)
        count = notif_data.filter(viewed=False).count()
        user = user_session(request)
        context = {
            'Title': "Add New K9",
            'form': add_donated_K9_form,
            'notif_data':notif_data,
            'count':count,
            'user':user,
        }
        return render(request, 'planningandacquiring/add_donated_K9.html', context)

def breeding_list(request, id=None):
    
    data1 = K9_Mated.objects.filter(status='Breeding').order_by('-id', '-date_mated')
    data2 = K9_Mated.objects.filter(status='Pregnant').order_by('-id', '-date_mated')
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)

    data_id=id
    d = None
    if data_id!=None:
        d = K9_Mated.objects.get(id=id)
        data1 = K9_Mated.objects.filter(status='Breeding').exclude(id=id).order_by('-id', '-date_mated')
      
   
    type_text = request.GET.get('type')
    if type_text == None:
        type_text = 'mated'

    print('type_text',type_text)

    context = {
        'Title': "Breeding List",
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'type_text':type_text,
        'data1':data1,
        'data2':data2,
        'data_id':data_id,
        'd':d,
        
    }
    return render(request, 'planningandacquiring/breeding_list.html', context)

def confirm_failed_pregnancy(request, id):
    data = K9_Mated.objects.get(id=id) # get k9
    mom = K9.objects.get(id=data.mother.id)
    decision = request.GET.get('decision')
    
    if decision == 'confirm':
        data.status = 'Pregnant'
        mom.training_status = 'Breeding'

        # messages.success(request, 'You have confirmed that ' + str(data.mother) + ' is pregnant.')

    elif decision == 'failed':
        data.status = 'Failed'
        mom.training_status = 'For-Breeding'
        K9_Litter.objects.create(mother=data.mother, father=data.father, litter_no=0)
        
        # messages.success(request, 'You have confirmed that ' + str(data.mother) + ' is not pregnant.')

    data.save()
    mom.save()

    return redirect('profiles:vet_dashboard')

def add_K9_parents(request):
    style = "ui teal message"

    #all in-heat today
    heat = K9.objects.filter(sex="Female").filter(training_status = "For-Breeding").filter(age__gte = 1).filter(age__lte = 6).filter(last_estrus_date=dt.today())

    print(heat)

    #heat today
    momh = []
    sickh = []
    b_arrh = []

    # heat_list = []
    # for heat in heat:
    #     heat_list.append(heat.id)

    #     h = Health.objects.filter(dog=heat).count()
    #     momh.append(heat)
    #     sickh.append(h)

    #     birth = K9_Litter.objects.filter(mother=heat).aggregate(sum=Sum('litter_no'))['sum']
    #     death = K9_Litter.objects.filter(mother=heat).aggregate(sum=Sum('litter_died'))['sum']

    #     if birth != None or death != None:
    #         total = (birth / (birth+death)) * 100
    #     else:
    #         total=100
        
    #     b_arrh.append(int(total))

    # hlist = zip(momh,sickh,b_arrh)
    # for a,b,c in hlist:
    #     print(a,b,c)
        
    mother  = K9.objects.filter(sex="Female").filter(training_status = "For-Breeding").filter(age__gte = 1).filter(age__lte = 6).filter(Q(reproductive_stage = "Estrus") | Q(reproductive_stage = "Proestrus"))
    
    # .exclude(id__in=heat_list)
    
    father = K9.objects.filter(sex="Male").filter(training_status = "For-Breeding").filter(age__gte = 1).filter(age__lte = 6)
    mother_all  = K9.objects.filter(sex="Female").filter(training_status = "For-Breeding").filter(age__gte = 1).filter(age__lte = 6).exclude(Q(reproductive_stage = "Estrus") | Q(reproductive_stage = "Proestrus"))
    
    #table 1
    mom = []
    sick = []
    b_arr = []
    for m in mother:
        h = Health.objects.filter(dog=m).count()
        mom.append(m)
        sick.append(h)

        birth = K9_Litter.objects.filter(mother=m).aggregate(sum=Sum('litter_no'))['sum']
        death = K9_Litter.objects.filter(mother=m).aggregate(sum=Sum('litter_died'))['sum']

        if birth != None or death != None:
            total = (birth / (birth+death)) * 100
        else:
            total=100
        
        b_arr.append(int(total))

    mlist = zip(mom,sick,b_arr)


    mmom = []
    msick = []
    mb_arr = []
    for mm in mother_all:
        h = Health.objects.filter(dog=mm).count()
        mmom.append(mm)
        msick.append(h)

        birth = K9_Litter.objects.filter(mother=mm).aggregate(sum=Sum('litter_no'))['sum']
        death = K9_Litter.objects.filter(mother=mm).aggregate(sum=Sum('litter_died'))['sum']

        if (birth != None or death != None) and (birth != 0 or death != 0):
            total = (birth / (birth+death)) * 100
        else:
            total=100
        
        mb_arr.append(int(total))

    mmlist = zip(mmom,msick,mb_arr)

    dad = []
    dsick = []
    db_arr = []
    for mm in father:
        h = Health.objects.filter(dog=mm).count()
        dad.append(mm)
        dsick.append(h)

        birth = K9_Litter.objects.filter(mother=mm).aggregate(sum=Sum('litter_no'))['sum']
        death = K9_Litter.objects.filter(mother=mm).aggregate(sum=Sum('litter_died'))['sum']

        if birth != None or death != None:
            total = (birth / (birth+death)) * 100
        else:
            total=100
        
        db_arr.append(int(total))

    flist = zip(dad,dsick,db_arr)

     #Belgian Malinois
    bm_m = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Belgian Malinois').filter(sex='Male').count()
    bm_f = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Belgian Malinois').filter(sex='Female').count()
    
    bm_m_edd =  K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Belgian Malinois').filter(capability='EDD').filter(sex='Male').count()
    bm_m_ndd =  K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Belgian Malinois').filter(capability='NDD').filter(sex='Male').count()
    bm_m_sar =  K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Belgian Malinois').filter(capability='SAR').filter(sex='Male').count()

    bm_f_edd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Belgian Malinois').filter(capability='EDD').filter(sex='Female').count()
    bm_f_ndd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Belgian Malinois').filter(capability='NDD').filter(sex='Female').count()
    bm_f_sar = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Belgian Malinois').filter(capability='SAR').filter(sex='Female').count()
    
    #Dutch Sheperd
    ds_m = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Dutch Sheperd').filter(sex='Male').count()
    ds_f = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Dutch Sheperd').filter(sex='Female').count()
    
    ds_m_edd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Dutch Sheperd').filter(capability='EDD').filter(sex='Male').count()
    ds_m_ndd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Dutch Sheperd').filter(capability='NDD').filter(sex='Male').count()
    ds_m_sar = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Dutch Sheperd').filter(capability='SAR').filter(sex='Male').count()

    ds_f_edd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Dutch Sheperd').filter(capability='EDD').filter(sex='Female').count()
    ds_f_ndd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Dutch Sheperd').filter(capability='NDD').filter(sex='Female').count()
    ds_f_sar = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Dutch Sheperd').filter(capability='SAR').filter(sex='Female').count()

    #German Sheperd
    gs_m = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='German Sheperd').filter(sex='Male').count()
    gs_f = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='German Sheperd').filter(sex='Female').count()
    
    gs_m_edd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='German Sheperd').filter(capability='EDD').filter(sex='Male').count()
    gs_m_ndd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='German Sheperd').filter(capability='NDD').filter(sex='Male').count()
    gs_m_sar = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='German Sheperd').filter(capability='SAR').filter(sex='Male').count()

    gs_f_edd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='German Sheperd').filter(capability='EDD').filter(sex='Female').count()
    gs_f_ndd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='German Sheperd').filter(capability='NDD').filter(sex='Female').count()
    gs_f_sar = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='German Sheperd').filter(capability='SAR').filter(sex='Female').count()
    
    
    gr_m = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Golden Retriever').filter(sex='Male').count()
    gr_f = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Golden Retriever').filter(sex='Female').count()
    
    gr_m_edd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Golden Retriever').filter(capability='EDD').filter(sex='Male').count()
    gr_m_ndd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Golden Retriever').filter(capability='NDD').filter(sex='Male').count()
    gr_m_sar = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Golden Retriever').filter(capability='SAR').filter(sex='Male').count()

    gr_f_edd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Golden Retriever').filter(capability='EDD').filter(sex='Female').count()
    gr_f_ndd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Golden Retriever').filter(capability='NDD').filter(sex='Female').count()
    gr_f_sar = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Golden Retriever').filter(capability='SAR').filter(sex='Female').count()
    
    jr_m = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Jack Russel').filter(sex='Male').count()
    jr_f = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Jack Russel').filter(sex='Female').count()
    
    jr_m_edd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Jack Russel').filter(capability='EDD').filter(sex='Male').count()
    jr_m_ndd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Jack Russel').filter(capability='NDD').filter(sex='Male').count()
    jr_m_sar = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Jack Russel').filter(capability='SAR').filter(sex='Male').count()

    jr_f_edd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Jack Russel').filter(capability='EDD').filter(sex='Female').count()
    jr_f_ndd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Jack Russel').filter(capability='NDD').filter(sex='Female').count()
    jr_f_sar = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Jack Russel').filter(capability='SAR').filter(sex='Female').count()
    
    lr_m = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Labrador Retriever').filter(sex='Male').count()
    lr_f = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Labrador Retriever').filter(sex='Female').count()
    
    lr_m_edd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Labrador Retriever').filter(capability='EDD').filter(sex='Male').count()
    lr_m_ndd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Labrador Retriever').filter(capability='NDD').filter(sex='Male').count()
    lr_m_sar = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Labrador Retriever').filter(capability='SAR').filter(sex='Male').count()

    lr_f_edd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Labrador Retriever').filter(capability='EDD').filter(sex='Female').count()
    lr_f_ndd = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Labrador Retriever').filter(capability='NDD').filter(sex='Female').count()
    lr_f_sar = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(breed='Labrador Retriever').filter(capability='SAR').filter(sex='Female').count()

    bm = bm_m+bm_f
    ds = ds_m+ds_f
    gs = gs_m+gs_f
    gr = gr_m+gr_f
    jr = jr_m+jr_f
    lr = lr_m+lr_f
    t_breed = bm+ds+gs+gr+jr+lr

    edd_f = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(capability='EDD').filter(sex='Female').count()
    ndd_f = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(capability='NDD').filter(sex='Female').count()
    sar_f = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(capability='SAR').filter(sex='Female').count()
    
    edd_m = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(capability='EDD').filter(sex='Male').count()
    ndd_m = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(capability='NDD').filter(sex='Male').count()
    sar_m = K9.objects.filter(Q(training_status='For-Breeding')|Q(training_status='Breeding')).filter(capability='SAR').filter(sex='Male').count()

    ndd = ndd_f+ndd_m
    edd = edd_f + edd_m
    sar = sar_f + sar_m

    if request.method == 'POST':
        f = request.POST.get('radiof')
        m = request.POST.get('radiom')

        request.session["mother_id"] = m
        request.session["father_id"] = f

        return redirect('planningandacquiring:confirm_K9_parents')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title': "K9_Breeding",
        'today': dt.today(),
        # 'hlist': hlist,
        'style': style,
        'mlist' : mlist,
        'flist' : flist,
        'mmlist':mmlist,
        'notif_data':notif_data,
        'count':count,
        'user':user,
        
        'ndd':ndd,
        'edd':edd,
        'sar':sar,

        'ndd_f':ndd_f,
        'edd_f':edd_f,
        'sar_f':sar_f,

        'ndd_m':ndd_m,
        'edd_m':edd_m,
        'sar_m':sar_m,

        'bm_m':bm_m,
        'bm_f':bm_f,
        'bm_m_edd':bm_m_edd,
        'bm_m_ndd':bm_m_ndd,
        'bm_m_sar':bm_m_sar,
        'bm_f_edd':bm_f_edd,
        'bm_f_ndd':bm_f_ndd,
        'bm_f_sar':bm_f_sar,


        'ds_m':ds_m,
        'ds_f':ds_f,
        'ds_m_edd':ds_m_edd,
        'ds_m_ndd':ds_m_ndd,
        'ds_m_sar':ds_m_sar,
        'ds_f_edd':ds_f_edd,
        'ds_f_ndd':ds_f_ndd,
        'ds_f_sar':ds_f_sar,

        'gs_m':gs_m,
        'gs_f':gs_f,
        'gs_m_edd':gs_m_edd,
        'gs_m_ndd':gs_m_ndd,
        'gs_m_sar':gs_m_sar,
        'gs_f_edd':gs_f_edd,
        'gs_f_ndd':gs_f_ndd,
        'gs_f_sar':gs_f_sar,

        'gr_m':gr_m,
        'gr_f':gr_f,
        'gr_m_edd':gr_m_edd,
        'gr_m_ndd':gr_m_ndd,
        'gr_m_sar':gr_m_sar,
        'gr_f_edd':gr_f_edd,
        'gr_f_ndd':gr_f_ndd,
        'gr_f_sar':gr_f_sar,

        'jr_m':jr_m,
        'jr_f':jr_f,
        'jr_m_edd':jr_m_edd,
        'jr_m_ndd':jr_m_ndd,
        'jr_m_sar':jr_m_sar,
        'jr_f_edd':jr_f_edd,
        'jr_f_ndd':jr_f_ndd,
        'jr_f_sar':jr_f_sar,

        'lr_m':lr_m,
        'lr_f':lr_f,
        'lr_m_edd':lr_m_edd,
        'lr_m_ndd':lr_m_ndd,
        'lr_m_sar':lr_m_sar,
        'lr_f_edd':lr_f_edd,
        'lr_f_ndd':lr_f_ndd,
        'lr_f_sar':lr_f_sar,

        'bm':bm,
        'ds':ds,
        'gs':gs,
        'gr':gr,
        'jr':jr,
        'lr':lr,
        't_breed':t_breed,
    }

    return render(request, 'planningandacquiring/add_K9_parents.html', context)

def in_heat_change(request):
    if request.method == 'POST':
        id = request.POST.get('id_k9')
        date = parse_date(request.POST.get('date_change'))
        
        k9 = K9.objects.get(id=id)
        k9.last_proestrus_date = date
        k9.save()
        
        return redirect('planningandacquiring:add_K9_parents_form')


def confirm_K9_parents(request):
    form = date_mated_form(request.POST or None)

    form.initial['date_mated'] = dt.today()
    mother_id = request.session["mother_id"]
    father_id = request.session["father_id"]

    mother = K9.objects.get(id=mother_id)
    father = K9.objects.get(id=father_id)

    request.session['date_mated'] = None

    if request.method == 'POST':
        if form.is_valid():
            mated = form.save(commit=False)
            mated.mother = mother
            mated.father = father
            mated.save()

            mother.training_status = 'Breeding'
            mother.save()
            request.session['date_mated'] = mated.id

        # return redirect('planningandacquiring:breeding_list', id=mated.id)
        return redirect('profiles:vet_dashboard')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'mother': mother,
        'father': father,
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'form':form,
    }

    return render(request, 'planningandacquiring/confirm_K9_parents.html', context)

def mating_confirmed(request):
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render(request, 'planningandacquiring/mating_confirmed.html', context)

def K9_parents_confirmed(request):
    mothers = K9.objects.filter(sex="Female")
    fathers = K9.objects.filter(sex="Male")

    mother_list = []
    father_list = []

    for mother in mothers:
        mother_list.append(mother)

    for father in fathers:
        father_list.append(father)

    if 'ok' in request.POST:
        return HttpResponseRedirect('add_K9_offspring_form/')
    else:
        #NOTIF SHOW
        notif_data = notif(request)
        count = notif_data.filter(viewed=False).count()
        user = user_session(request)
        context = {
            'Title': "Receive Donated K9",
            'form': add_K9_parents_form,
            'mothers': mother_list,
            'fathers': father_list,
            'notif_data':notif_data,
            'count':count,
            'user':user,
        }
        return render(request, 'planningandacquiring/add_K9_parents.html', context)

#TODO
#formset
def add_K9_offspring(request, id):
    form = DateK9Form(request.POST or None)
    k9_formset = formset_factory(add_offspring_K9_form, extra=1, can_delete=True)
    formset = k9_formset(request.POST, request.FILES)
    style = ''

    data = K9_Mated.objects.get(id=id)
    data.status = 'Pregnancy Done'
    if data.mother.breed != data.father.breed:
        breed = 'Mixed'
    else:
        breed = data.mother.breed

    k9_count = 0

    
    if request.method == 'POST':
        data.mother.training_status = 'For-Breeding'
        data.save()
        if form.is_valid():
            date = form.cleaned_data['birth_date']

        if formset.is_valid():
            for form in formset:
                k9 = form.save(commit=False)
                k9.source = "Breeding"
                k9.breed = data.mother.breed
                k9.birth_date = date
                k9.save()
                
                #K9 parents create
                K9_Parent.objects.create(mother=data.mother, father=data.father, offspring=k9)

                k9_count = k9_count+1

            died =  request.POST.get('litter_died')
            K9_Litter.objects.create(mother=data.mother, father=data.father, litter_no=int(k9_count), litter_died=int(died))
            
            #Mom
            mom = K9.objects.get(id=data.mother.id)
            mom.training_status='For-Breeding'
            mom.save()
            #Dad
            dad = K9.objects.get(id=data.father.id)
            dad.save()

            data.save()
            messages.success(request, 'You have added k9 offspring!')
            return HttpResponseRedirect('../breeding_list/?type=pregnant')
        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')


    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title': "Receive Donated K9",
        'form': form,
        # 'formset': k9_formset(),
        'style': style,
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'data':data,
    }

    return render(request, 'planningandacquiring/add_K9_offspring.html', context)

def breeding_k9_confirmed(request):
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render(request, 'planningandacquiring/breeding_confirmed.html', context)

def confirm_breeding(request):
    offspring_id = request.session['offspring_id']
    mother_id = request.session['mother_id']
    father_id = request.session['father_id']

    offspring = K9.objects.get(id=offspring_id)
    mother = K9.objects.get(id=mother_id)
    father = K9.objects.get(id=father_id)

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title': "Receive Donated K9",
        'offspring': offspring,
        'mother': mother,
        'father': father,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }

    return render(request, 'planningandacquiring/confirm_breeding.html', context)

def breeding_confirmed(request):
    offspring_id = request.session['offspring_id']
    mother_id = request.session['mother_id']
    father_id = request.session['father_id']

    offspring = K9.objects.get(id=offspring_id)
    mother = K9.objects.get(id=mother_id)
    father = K9.objects.get(id=father_id)

    if 'ok' in request.POST:
        k9_parent = K9_Parent(offspring = offspring, mother = mother, father = father)
        k9_parent.save()

        cvr = VaccinceRecord.objects.create(k9=offspring)
        VaccineUsed.objects.create(vaccine_record=cvr, disease='deworming_1')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='deworming_2')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='deworming_3')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='dhppil_cv_1')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='heartworm_1')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='bordetella_1')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='tick_flea_1')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='dhppil_cv_2')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='deworming_4')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='heartworm_2')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='bordetella_2')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='anti_rabies')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='tick_flea_2')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='dhppil_cv_3')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='heartworm_3')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='dhppil4_1')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='tick_flea_3')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='dhppil4_2')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='heartworm_4')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='tick_flea_4')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='heartworm_5')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='tick_flea_5')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='heartworm_6')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='tick_flea_6')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='heartworm_7')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='tick_flea_7')
        VaccineUsed.objects.create(vaccine_record=cvr, disease='heartworm_8')


        #NOTIF SHOW
        notif_data = notif(request)
        count = notif_data.filter(viewed=False).count()
        context={
            'notif_data':notif_data,
            'count':count,
        }

        return render(request, 'planningandacquiring/breeding_confirmed.html', context)
    else:
        #delete offspring
        offspring.delete()

        mothers = K9.objects.filter(sex="Female")
        fathers = K9.objects.filter(sex="Male")

        mother_list = []
        father_list = []

        for mother in mothers:
            mother_list.append(mother)

        for father in fathers:
            father_list.append(father)

        #NOTIF SHOW
        notif_data = notif(request)
        count = notif_data.filter(viewed=False).count()
        user = user_session(request)
        context = {
            'Title': "Receive Donated K9",
            'form': add_K9_parents_form,
            'mothers': mother_list,
            'fathers': father_list,
            'notif_data':notif_data,
            'count':count,
            'user':user,
        }
        return render(request, 'planningandacquiring/add_K9_parents.html', context)


#Listview format
def K9_listview(request):

    k9 = K9.objects.all() #Sample Query
    style = 'ui green message' #CSS values

    #//Backend Code//
    
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)

    #Variables to be used in templates
    context = {
        'Title' : 'K9 List',
        'k9' : k9,
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'style':style,
    }

    #Access Template
    return render(request, 'planningandacquiring/K9_list.html', context)

#Detailview format
def K9_detailview(request, id):
    k9 = K9.objects.get(id = id)
    form = k9_detail_form(request.POST or None, request.FILES or None, instance=k9)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, 'K9 Details Updated!')

            if k9.training_status == 'For-Deployment' or k9.training_status == 'For-Breeding':
                k9.training_status = request.POST.get('radio')
                k9.save()

            return redirect('planningandacquiring:K9_detail', id = k9.id)

        # if 'change_training_status' in request.POST:
        #     print(request.POST.get('radio'))
        #     k9.training_status = request.POST.get('radio')
        #     k9.save()
        #     messages.success(request, 'K9 is now ' + k9.training_status + '!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    try:
        parent = K9_Parent.objects.get(offspring=k9)
    except K9_Parent.DoesNotExist:
        context = {
            'Title': 'K9 Details',
            'k9' : k9,
            'notif_data':notif_data,
            'count':count,
            'user':user,
            'form':form,
        }
    else:
        parent_exist = 1
        context = {
            'Title': 'K9 Details',
            'k9': k9,
            'parent': parent,
            'parent_exist': parent_exist,
            'notif_data':notif_data,
            'count':count,
            'user':user,
            'form':form,
        }

    return render(request, 'planningandacquiring/K9_detail.html', context)

def add_breed(request):
    form = add_breed_form(request.POST)
    style = ""
    if request.method == 'POST':
        if form.is_valid():
            breed = form.save()
            breed.save()
            style = "ui green message"
            messages.success(request, 'Breed has been successfully Added!')

        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title': "Add Breed",
        'form': form,
        'style': style,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    print(form)
    return render(request, 'planningandacquiring/add_breed.html', context)


def breed_listview(request):
    breed = Dog_Breed.objects.all()

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title': 'Breed List',
        'breed': breed,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }

    return render(request, 'planningandacquiring/view_breed.html', context)


################# BUDGETING ###################
def budgeting_detail(request, id):
    pb = Proposal_Budget.objects.get(id=id)
    pk9 = Proposal_K9.objects.filter(proposal=pb)
    mf = Proposal_Milk_Food.objects.filter(proposal=pb)
    vp = Proposal_Vac_Prev.objects.filter(proposal=pb)
    pm = Proposal_Medicine.objects.filter(proposal=pb)
    pvs = Proposal_Vet_Supply.objects.filter(proposal=pb)
    pks = Proposal_Kennel_Supply.objects.filter(proposal=pb)
    po = Proposal_Others.objects.filter(proposal=pb)
    pt = Proposal_Training.objects.filter(proposal=pb)
    total_k9 = pb.k9_current + pb.k9_needed + pb.k9_breeded

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    
    try: 
        ab = Actual_Budget.objects.get(year_budgeted__year=pb.year_budgeted.year)
        amf = Actual_Milk_Food.objects.filter(proposal=ab)
        ak9 = Actual_K9.objects.filter(proposal=ab)
        avp = Actual_Vac_Prev.objects.filter(proposal=ab)
        am = Actual_Medicine.objects.filter(proposal=ab)
        avs = Actual_Vet_Supply.objects.filter(proposal=ab)
        aks = Actual_Kennel_Supply.objects.filter(proposal=ab)
        ao = Actual_Others.objects.filter(proposal=ab)
        at = Actual_Training.objects.filter(proposal=ab)
        total_new = ab.k9_current + ab.k9_needed + ab.k9_breeded

    except ObjectDoesNotExist:
        ab = None
        ak9 = None
        amf = None
        avp = None
        am = None
        avs = None
        aks = None
        ao = None
        at = None
        total_new = 0


    # print('Proposed Budget: ',pb.year_budgeted.year)
    # print('Actual Budget: ',Actual_Budget.objects.get(year_budgeted__year=pb.year_budgeted.year))

    if request.method == 'POST':
        lump_sum = request.POST.get('lump_sum')
        lump_sum = Decimal(lump_sum)
        
        petty_cash = 0
        food_milk_total = 0
        k9_total = 0
        k9_quantity = 0
        vac_prev_total = 0
        medicine_total = 0
        vet_supply_total = 0
        kennel_total = 0
        others_total = 0
        training_total = 0
        training_count = 0
        grand_total = 0
        if ab:
            ab2 = Actual_Budget.objects.get(year_budgeted__year=ab.year_budgeted.year)
        else:
            ab2 = None

        print('LUMP SUM', lump_sum)
        
        if ab2:
            amf = Actual_Milk_Food.objects.filter(proposal=ab2).delete()
            ak9 = Actual_K9.objects.filter(proposal=ab2).delete()
            avp = Actual_Vac_Prev.objects.filter(proposal=ab2).delete()
            am = Actual_Medicine.objects.filter(proposal=ab2).delete()
            avs = Actual_Vet_Supply.objects.filter(proposal=ab2).delete()
            aks = Actual_Kennel_Supply.objects.filter(proposal=ab2).delete()
            ao = Actual_Others.objects.filter(proposal=ab2).delete()
            at = Actual_Training.objects.filter(proposal=ab2).delete()

            print('Actual Budger this year Exist')

            for data in pt:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = pb.k9_breeded
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                training_count = training_count + pb.k9_breeded
                training_total = training_total + quantity_budget    
                Actual_Training.objects.create(proposal=ab2,quantity=quantity_num,total=quantity_budget)

            for data in mf:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = np.ceil(int(budget_amount / data.price))
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                food_milk_total = food_milk_total + quantity_budget
                Actual_Milk_Food.objects.create(proposal=ab2,item=data.item, price=data.price, quantity=quantity_num,total=quantity_budget)
            
            for data in vp:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = np.ceil(int(budget_amount / data.price))
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                vac_prev_total  = vac_prev_total  + quantity_budget
                Actual_Vac_Prev.objects.create(proposal=ab2,item =data.item, price=data.price, quantity=quantity_num,total=quantity_budget)

            for data in pm:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = np.ceil(int(budget_amount / data.price))
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                medicine_total  = medicine_total  + quantity_budget
                Actual_Medicine.objects.create(proposal=ab2,item =data.item, price=data.price, quantity=quantity_num,total=quantity_budget)

            for data in pvs:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = np.ceil(int(budget_amount / data.price))
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                vet_supply_total = vet_supply_total + quantity_budget
                Actual_Vet_Supply.objects.create(proposal=ab2,item =data.item, price=data.price, quantity=quantity_num,total=quantity_budget)
                
            for data in pks:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = np.ceil(int(budget_amount / data.price))
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                kennel_total = kennel_total + quantity_budget
                Actual_Kennel_Supply.objects.create(proposal=ab2,item =data.item, price=data.price, quantity=quantity_num,total=quantity_budget)

            for data in po:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = np.ceil(int(budget_amount / data.price))
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                others_total = others_total + quantity_budget
                Actual_Others.objects.create(proposal=ab2,item =data.item, price=data.price, quantity=quantity_num,total=quantity_budget)

                
            temp_grand_total = food_milk_total + vac_prev_total + medicine_total + vet_supply_total + kennel_total + others_total + training_total

            petty_cash = lump_sum - temp_grand_total

            print('Petty Cash before K9: ', petty_cash)
            for data in pk9:
                price = data.price + 18000
                quantity = data.quantity
                if petty_cash >= price:
                    quantity_num = np.ceil(int(petty_cash/price))
                    if quantity_num > quantity:
                        quantity_num = quantity

                    quantity_budget = round(Decimal(quantity_num) * Decimal(price), 2)
                    petty_cash = petty_cash - quantity_budget
                    training_total = training_total + Decimal(quantity_num*18000)
                    training_count = training_count + quantity_num

                    k9_t=Decimal(data.price) * Decimal(quantity_num)
                    Actual_K9.objects.create(proposal=ab2,item=data.item, price=data.price, quantity=quantity_num,total=k9_t)

                    at_temp = Actual_Training.objects.get(proposal=ab2)
                    at_temp.quantity = at_temp.quantity + quantity_num
                    at_temp.total = at_temp.total + Decimal(quantity_num*18000)
                    at_temp.save()
                    k9_quantity = k9_quantity+quantity_num
                    k9_total = k9_total + k9_t
                else:
                    print('PETTY CASH-NO K9 PROCURED for this BREED', data, petty_cash)

            ab2.k9_needed = k9_quantity
            ab2.save()
            grand_total = food_milk_total + vac_prev_total + medicine_total + vet_supply_total + kennel_total + others_total + training_total + petty_cash + k9_total
            total_new = ab2.k9_current+ab2.k9_needed+ab2.k9_breeded
            print('K9 Total', k9_total)
        else:
            ab2 = Actual_Budget.objects.create(k9_current=pb.k9_current,k9_breeded=pb.k9_breeded,date_created=dt.today(),year_budgeted=pb.year_budgeted)

            print('No Actual Budger this year Exist')


            for data in pt:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = pb.k9_breeded
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                training_count = training_count + pb.k9_breeded
                training_total = training_total + quantity_budget    
                Actual_Training.objects.create(proposal=ab2,quantity=quantity_num,total=quantity_budget)

            for data in mf:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = np.ceil(int(budget_amount / data.price))
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                food_milk_total = food_milk_total + quantity_budget
                Actual_Milk_Food.objects.create(proposal=ab2,item=data.item, price=data.price, quantity=quantity_num,total=quantity_budget)
            
            for data in vp:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = np.ceil(int(budget_amount / data.price))
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                vac_prev_total = vac_prev_total + quantity_budget
                Actual_Vac_Prev.objects.create(proposal=ab2,item =data.item, price=data.price, quantity=quantity_num,total=quantity_budget)

            for data in pm:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = np.ceil(int(budget_amount / data.price))
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                medicine_total = medicine_total + quantity_budget
                Actual_Medicine.objects.create(proposal=ab2,item =data.item, price=data.price, quantity=quantity_num,total=quantity_budget)

                
            for data in pvs:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = np.ceil(int(budget_amount / data.price))
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                vet_supply_total = vet_supply_total   + quantity_budget
                Actual_Vet_Supply.objects.create(proposal=ab2,item =data.item, price=data.price, quantity=quantity_num,total=quantity_budget)
                
            for data in pks:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = np.ceil(int(budget_amount / data.price))
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                kennel_total = kennel_total + quantity_budget
                Actual_Kennel_Supply.objects.create(proposal=ab2,item =data.item, price=data.price, quantity=quantity_num,total=quantity_budget)

            for data in po:
                budget_amount = round(data.percent * lump_sum, 2)
                quantity_num = np.ceil(int(budget_amount / data.price))
                quantity_budget = round(Decimal(quantity_num) * Decimal(data.price), 2)
                others_total = others_total + quantity_budget
                Actual_Others.objects.create(proposal=ab2,item =data.item, price=data.price, quantity=quantity_num,total=quantity_budget)

                
            temp_grand_total = food_milk_total + vac_prev_total + medicine_total + vet_supply_total + kennel_total + others_total + training_total
            
            petty_cash = lump_sum - temp_grand_total

            print('Petty Cash before K9: ', petty_cash)
            for data in pk9:
                price = data.price + 18000
                quantity = data.quantity
                if petty_cash >= price:
                    quantity_num = np.ceil(int(petty_cash/price))
                    if quantity_num > quantity:
                        quantity_num = quantity

                    quantity_budget = round(Decimal(quantity_num) * Decimal(price), 2)
                    petty_cash = petty_cash - quantity_budget
                    training_total = training_total + Decimal(quantity_num*18000)
                    training_count = training_count + quantity_num

                    k9_t= Decimal(data.price) * Decimal(quantity_num)
                    Actual_K9.objects.create(proposal=ab2,item=data.item, price=data.price, quantity=quantity_num,total=k9_t)

                    at_temp = Actual_Training.objects.get(proposal=ab2)
                    at_temp.quantity = at_temp.quantity + quantity_num
                    at_temp.total = at_temp.total + Decimal(quantity_num*18000)
                    at_temp.save()

                    k9_quantity = k9_quantity+quantity_num
                    k9_total = k9_total + k9_t
                else:
                    print('PETTY CASH-NO K9 PROCURED for this BREED', data, petty_cash)

            print('K9 Total', k9_total)
            grand_total = food_milk_total + vac_prev_total + medicine_total + vet_supply_total + kennel_total + others_total + training_total + petty_cash + k9_total
            
            ab2.k9_needed= k9_quantity
            ab2.k9_total= k9_total
            ab2.food_milk_total=food_milk_total
            ab2.vac_prev_total=vac_prev_total
            ab2.medicine_total=medicine_total
            ab2.vet_supply_total=vet_supply_total
            ab2.kennel_total=kennel_total
            ab2.others_total=others_total
            ab2.training_total=training_total
            ab2.train_count=training_total
            ab2.petty_cash=petty_cash
            ab2.grand_total=grand_total
            ab2.save()

            total_new = ab2.k9_current+ab2.k9_needed+ab2.k9_breeded

        return redirect('planningandacquiring:budgeting_detail', id = id)

    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'pb':pb,
        'pk9':pk9,
        'mf':mf,
        'vp':vp,
        'pm':pm,
        'pvs':pvs,
        'pks':pks,
        'po':po,
        'pt':pt,
        'total_k9':total_k9,
        'ab':ab,
        'ak9':ak9,
        'amf':amf,
        'avp':avp,
        'am':am,
        'avs':avs,
        'aks':aks,
        'ao':ao,
        'at':at,
        'total_new':total_new,
    }
    return render(request, 'planningandacquiring/budgeting_detail.html', context)

def breed_list(request):
    breed = Dog_Breed.objects.all()

    # NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'Title': 'Breed List',
        'breed': breed,
        'notif_data': notif_data,
        'count': count,
        'user': user,
    }

    return render(request, 'planningandacquiring/breed_list.html', context)

def breed_detail(request, id):
    breed = Dog_Breed.objects.get(id=id)

    form = add_breed_form(request.POST or None, request.FILES or None, instance=breed)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, 'Breed Details Updated!')

            return redirect('planningandacquiring:breed_detail', id=breed.id)

    # NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)

    context = {
        'Title': 'Breed List',
        'breed': breed,
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }
    return render(request, 'planningandacquiring/breed_detail.html', context)


################# END BUDGETING ###################

def k9_performance_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/k9_performance_date.html', context)


def ajax_k9_performance_report(request):
    data = []
    to_date = None
    from_date = None
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        dog = Daily_Refresher.objects.filter(date__range=[from_date, to_date]).values('k9').order_by("k9__name").distinct()

        for d in dog:
            for key, value in d.items(): 
                if key == 'k9':
                    pp = Daily_Refresher.objects.filter(k9__id=value).filter(date__range=[from_date, to_date]).aggregate(sum=Sum('port_plant'))['sum']
                    pf = Daily_Refresher.objects.filter(k9__id=value).filter(date__range=[from_date, to_date]).aggregate(sum=Sum('port_find'))['sum']
                    bp = Daily_Refresher.objects.filter(k9__id=value).filter(date__range=[from_date, to_date]).aggregate(sum=Sum('building_plant'))['sum']
                    bf = Daily_Refresher.objects.filter(k9__id=value).filter(date__range=[from_date, to_date]).aggregate(sum=Sum('building_find'))['sum']
                    vp = Daily_Refresher.objects.filter(k9__id=value).filter(date__range=[from_date, to_date]).aggregate(sum=Sum('vehicle_plant'))['sum']
                    vf = Daily_Refresher.objects.filter(k9__id=value).filter(date__range=[from_date, to_date]).aggregate(sum=Sum('vehicle_find'))['sum']
                    bgp = Daily_Refresher.objects.filter(k9__id=value).filter(date__range=[from_date, to_date]).aggregate(sum=Sum('baggage_plant'))['sum']
                    bgf = Daily_Refresher.objects.filter(k9__id=value).filter(date__range=[from_date, to_date]).aggregate(sum=Sum('baggage_find'))['sum']
                    op = Daily_Refresher.objects.filter(k9__id=value).filter(date__range=[from_date, to_date]).aggregate(sum=Sum('others_plant'))['sum']
                    of = Daily_Refresher.objects.filter(k9__id=value).filter(date__range=[from_date, to_date]).aggregate(sum=Sum('others_find'))['sum']
                    r = Daily_Refresher.objects.filter(k9__id=value).filter(date__range=[from_date, to_date]).aggregate(avg=Avg('rating'))['avg']
                    
                    k9 = K9.objects.get(id=value)
                    dt = [k9,k9.capability,pf,pp,bf,bp,vf,vp,bgf,bgp,of,op,round(r,2)]
                    data.append(dt)
    except:
        pass
    user = user_session(request)
    context = {
        'data':data,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/k9_performance_report.html', context)

def fou_accomplishment_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/fou_accomplishment_date.html', context)
    
def ajax_fou_accomplishment_report(request):
    data = []
    to_date = None
    from_date = None
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        acc = Handler_Incident.objects.filter(date__range=[from_date, to_date]).values('handler').order_by("handler__fullname").distinct()
        
        for acc in acc:
            for key, value in acc.items():
                print(key,value)  
                if key == 'handler':
                    rp = Handler_Incident.objects.filter(handler__id=value).filter(date__range=[from_date, to_date]).filter(status='Done').filter(incident='Rescued People').count()
                    ma = Handler_Incident.objects.filter(handler__id=value).filter(date__range=[from_date, to_date]).filter(status='Done').filter(incident='Made an Arrest').count()
                    pp = Handler_Incident.objects.filter(handler__id=value).filter(date__range=[from_date, to_date]).filter(status='Done').filter(incident='Poor Performance').count()
                    v = Handler_Incident.objects.filter(handler__id=value).filter(date__range=[from_date, to_date]).filter(status='Done').filter(incident='Violation').count()
                    h = User.objects.get(id=value)
                    pos = rp+ma
                    neg = pp+v
                    a = [h,rp,ma,pp,v,neg,pos]
                    print(a)
                    data.append(a)
    except:
        pass
    user = user_session(request)
    context = {
        'data':data,
        'from_date':from_date,
        'to_date':to_date,
        'user':user,
    }

    return render(request, 'planningandacquiring/fou_accomplishment_report.html', context)
    
def training_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/training_date.html', context)
    
def ajax_training_report(request):
    data = []
    to_date = None
    from_date = None

    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')
        t = Training.objects.filter(stage='Finished Training').filter(date_finished__range=[from_date, to_date]).values('k9').order_by('k9__name').distinct()
        
        # print(t)
        for t in t:
            date_all = 0
            for key, value in t.items():  
                if key == 'k9':
                    th = Training_History.objects.get(k9__id=value)
                    ts = Training_Schedule.objects.filter(k9__id=value)
                    t = Training.objects.filter(k9__id=value).get(stage='Finished Training')
                    # print(th.handler, th.date)

                    for ts in ts:
                        if ts.stage == 'Stage 0':
                            pass
                        else:
                            # print(ts.k9 ,ts.stage, ts.date_start.date(), ts.date_end.date())
                            result = ts.date_end.date() - ts.date_start.date()
                            date_all = date_all + result.days

            date_mon = int(date_all/30)
            a = [th.k9, th.k9.breed, th.handler, date_all, date_mon, t.grade]
            data.append(a)
            # print(a)
                   
                                
    except:
        pass
    user = user_session(request)
    context = {
        'data':data,
        'from_date':from_date,
        'to_date':to_date,
        'user':user,
    }

    return render(request, 'planningandacquiring/training_report.html', context)

def training_summary_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/training_summary_date.html', context)
    
def ajax_training_summary_report(request):
    edd_data = []
    ndd_data = []
    sar_data = []
    data = []

    edd_total = 0
    ndd_total = 0
    sar_total = 0
    to_date = None
    from_date = None

    passed=0
    failed=0
    total=0
    user = user_session(request)
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        t = Training.objects.filter(Q(stage='Finished Training') | Q(stage__contains='Failed')).filter(date_finished__range=[from_date, to_date]).values('k9').distinct().order_by('grade')
        
        dog = []
        # print("training count", t)
        for t in t:
            for key, value in t.items():  
                if key == 'k9':
                    k9 = K9.objects.get(id=value)
                    a = [k9,k9.breed,k9.capability, k9.trained]
                    dog.append(a)
        edd_=[]

        db = Dog_Breed.objects.all().values('breed').distinct()
        
        edd_breed=[]
        edd_passed= []
        edd_failed = []

        ndd_breed=[]
        ndd_passed= []
        ndd_failed = []

        sar_breed=[]
        sar_passed= []
        sar_failed = []

        for d in db:
            for key, value in d.items(): 
                if key=='breed':
                    for (n, (item1,item2,item3,item4)) in enumerate(dog):
                        # print(item1,item2,item3,item4)
                        if item2 == value and item3 == 'EDD':
                            if item2 in edd_breed:
                                i = edd_breed.index(item2)
                                if item4 == 'Trained':
                                    edd_passed[i] = edd_passed[i]+1
                                else:
                                    edd_failed[i] = edd_failed[i]+1
                                
                            else:
                                #add breed
                                edd_breed.append(item2)
                                edd_failed.append(0)
                                edd_passed.append(0)
                                
                                i = edd_breed.index(item2)
                                if item4 == 'Trained':
                                    edd_passed[i] = edd_passed[i]+1
                                else:
                                    edd_failed[i] = edd_failed[i]+1

                        elif item2 == value and item3 == 'NDD':
                            if item2 in ndd_breed:
                                i = ndd_breed.index(item2)
                                if item4 == 'Trained':
                                    ndd_passed[i] = ndd_passed[i]+1
                                else:
                                    ndd_failed[i] = ndd_failed[i]+1
                                
                            else:
                                #add breed
                                ndd_breed.append(item2)
                                ndd_failed.append(0)
                                ndd_passed.append(0)
                                
                                i = ndd_breed.index(item2)
                                if item4 == 'Trained':
                                    ndd_passed[i] = ndd_passed[i]+1
                                else:
                                    ndd_failed[i] = ndd_failed[i]+1

                        elif item2 == value and item3 == 'SAR':
                            if item2 in sar_breed:
                                i = sar_breed.index(item2)
                                if item4 == 'Trained':
                                    sar_passed[i] = sar_passed[i]+1
                                else:
                                    sar_failed[i] = sar_failed[i]+1
                                
                            else:
                                #add breed
                                sar_breed.append(item2)
                                sar_failed.append(0)
                                sar_passed.append(0)
                                
                                i = sar_breed.index(item2)
                                if item4 == 'Trained':
                                    sar_passed[i] = sar_passed[i]+1
                                else:
                                    sar_failed[i] = sar_failed[i]+1


        # print('EDD', edd_breed, edd_passed, edd_failed)
        # print('NDD', ndd_breed, ndd_passed, ndd_failed)
        # print('SAR', sar_breed, sar_passed, sar_failed)

        edd_data = []
        edd_total = sum(edd_passed) + sum(edd_failed)
        for breed in edd_breed:
            i = edd_breed.index(breed)
            t = edd_passed[i]+edd_failed[i]
            a = [breed,edd_passed[i],edd_failed[i],t]
            edd_data.append(a)
        
        ndd_data = []
        ndd_total = sum(ndd_passed) + sum(ndd_failed)
        for breed in ndd_breed:
            i = ndd_breed.index(breed)
            t = ndd_passed[i]+ndd_failed[i]
            a = [breed,ndd_passed[i],ndd_failed[i],t]
            ndd_data.append(a)

        sar_data = []
        sar_total = sum(sar_passed) + sum(sar_failed)
        for breed in sar_breed:
            i = sar_breed.index(breed)
            t = sar_passed[i]+sar_failed[i]
            a = [breed,sar_passed[i],sar_failed[i],t]
            sar_data.append(a)

        edd_f = Training.objects.filter(stage__contains='Failed').filter(k9__capability="EDD").filter(date_finished__range=[from_date, to_date]).count()

        edd_p = Training.objects.filter(stage__contains='Finished Training').filter(k9__capability="EDD").filter(date_finished__range=[from_date, to_date]).count()

        ndd_f = Training.objects.filter(stage__contains='Failed').filter(k9__capability="NDD").filter(date_finished__range=[from_date, to_date]).count()

        ndd_p = Training.objects.filter(stage__contains='Finished Training').filter(k9__capability="NDD").filter(date_finished__range=[from_date, to_date]).count()       
        
        sar_f = Training.objects.filter(stage__contains='Failed').filter(k9__capability="SAR").filter(date_finished__range=[from_date, to_date]).count()

        sar_p = Training.objects.filter(stage__contains='Finished Training').filter(k9__capability="SAR").filter(date_finished__range=[from_date, to_date]).count()       
        
        failed = edd_f + ndd_f + sar_f
        passed = edd_p + ndd_p + sar_p
        total = failed + passed

        edd_t = ['EDD', edd_p, edd_f, edd_p+edd_f]
        ndd_t = ['NDD', ndd_p, ndd_f, ndd_p+ndd_f]
        sar_t = ['SAR', sar_p, sar_f, sar_p+sar_f]
        total_t = ['TOTAL', passed, failed, total]
        
        data.append(edd_t)
        data.append(ndd_t)
        data.append(sar_t)
    except:
        pass

    context = {
        'edd_data':edd_data,
        'ndd_data':ndd_data,
        'sar_data':sar_data,
        'edd_total':edd_total,
        'ndd_total':ndd_total,
        'sar_total':sar_total,
        'data':data,
        'from_date':from_date,
        'to_date':to_date,
        'passed':passed,
        'failed':failed,
        'total':total,
        'user':user
    }

    return render(request, 'planningandacquiring/training_summary_report.html', context)

def aor_summary_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/aor_summary_date.html', context)
    
def ajax_aor_summary_report(request):
    data_arr = []
    to_date = None
    from_date = None
    
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')
        area_val = []

        dr = Dog_Request.objects.filter(start_date__range=[from_date, to_date]).values('area').order_by('area__name').distinct()
        
        for data in dr:
            for key, value in data.items():
                if key == 'area':
                    area_val.append(value)

        inc = Incidents.objects.filter(date__range=[from_date, to_date]).values('location__area').order_by('location__area__name').distinct()

        for data in inc:
            for key, value in data.items():
                if key == 'location__area':
                    area_val.append(value)

        # mar = Maritime.objects.filter(datetime__range=[from_date, to_date]).values('location__area').distinct().order_by('location__area__name')

        # for data in mar:
        #     for key, value in data.items():
        #         if key == 'location__area':
        #             area_val.append(value)

        area_val= pd.unique(area_val)
        print(area_val)
        for id_area in area_val:
            a = Area.objects.get(id=id_area)
            # b = Maritime.objects.filter(location__area=a).filter(datetime__range=[from_date, to_date]).aggregate(avg=Avg('passenger_count'))['avg']
            edd = Incidents.objects.filter(location__area=a).filter(date__range=[from_date, to_date]).filter(type='Explosives Related').count()
            ndd = Incidents.objects.filter(location__area=a).filter(date__range=[from_date, to_date]).filter(type='Narcotics Related').count()
            sar = Incidents.objects.filter(location__area=a).filter(date__range=[from_date, to_date]).filter(type='Search and Rescue Related').count()
            big = Dog_Request.objects.filter(area=a).filter(start_date__range=[from_date, to_date]).filter(sector_type='Big Event').count()
            small = Dog_Request.objects.filter(area=a).filter(start_date__range=[from_date, to_date]).filter(sector_type='Small Event').count()
            
            # if b == None:
            #     b = 0
            print('1 AREA', ndd)
            x = [a,big,small,edd,ndd,sar]
            data_arr.append(x)

        print(data_arr)
    
    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/aor_summary_report.html', context)

def port_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/port_date.html', context)
    
def ajax_port_report(request):
    data_arr = []
    area_arr = []
    to_date = None
    from_date = None
    
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')
        print("DATE",to_date,from_date)
        area_val = []
        arr_val = []

        inc = Incidents.objects.filter(date__range=[from_date, to_date]).values('location__area').order_by('location__area__name').distinct()

        # print('INC', inc)
        
        for data in inc:
            for key, value in data.items():
                if key == 'location__area':
                    area_val.append(value)

        mar = Maritime.objects.filter(date__range=[from_date, to_date]).values('location__area').order_by('location__area__name').distinct()

        # print('MAR', mar)
        for data in mar:
            for key, value in data.items():
                if key == 'location__area':
                    area_val.append(value)

        area_val= pd.unique(area_val)
       
        print('AREA', area_val)
        for id_area in area_val:
            a = Area.objects.get(id=id_area)
            area_arr.append(a)
            l= Location.objects.filter(area=a).order_by('place').values_list('id', flat=True)
            l = list(l)
            
            arr = []
            b = Maritime.objects.filter(location__in=l).filter(date__range=[from_date, to_date]).order_by('location__place')
            # print('MARITIME LOC', b)
            for b in b:
                arr.append(b.location.id)
            
            c = Incidents.objects.filter(location__in=l).filter(date__range=[from_date, to_date]).order_by('location__place')
            for c in c:
                arr.append(c.location.id) 

            arr = pd.unique(arr)
            # print('Location',l)
            # print('ARR',arr)
            for data in arr:
                l = Location.objects.get(id=data)
                m = Maritime.objects.filter(date__range=[from_date, to_date]).filter(location=l).aggregate(avg=Avg('passenger_count'))['avg']
                edd = Incidents.objects.filter(date__range=[from_date, to_date]).filter(location=l).filter(type='Explosives Related').count()
                ndd = Incidents.objects.filter(date__range=[from_date, to_date]).filter(location=l).filter(type='Narcotics Related').count()
                sar = Incidents.objects.filter(date__range=[from_date, to_date]).filter(location=l).filter(type='Search and Rescue Related').count()
                oth = Incidents.objects.filter(date__range=[from_date, to_date]).filter(location=l).filter(type='Others').count()

                ta = Team_Assignment.objects.filter(location=l).last()
                #Maritime
                if m == None:
                    m=0

                #Team Assignment and Team Leader
                if ta == None:
                    ta_team = "Not Assigned"
                    ta_leader = "Not Assigned"
                else:
                    ta_team = ta.team
                    ta_leader = ta.team_leader

                if ta_team == None:
                    ta_team = "Not Assigned"
                if ta_leader == None:
                    ta_leader = "Not Assigned"

                edd_dep = Team_Dog_Deployed.objects.filter(team_assignment=ta).filter(date_added__range=[from_date, to_date]).filter(k9__capability='EDD').count()

                ndd_dep = Team_Dog_Deployed.objects.filter(team_assignment=ta).filter(date_added__range=[from_date, to_date]).filter(k9__capability='NDD').count()

                sar_dep = Team_Dog_Deployed.objects.filter(team_assignment=ta).filter(date_added__range=[from_date, to_date]).filter(k9__capability='SAR').count()


                x = [l,ta_team,int(np.ceil(m)),edd,ndd,sar,oth,edd_dep,ndd_dep,sar_dep]
                # print('TEST', x)
                data_arr.append(x)

        # print('Area', area_arr)
        # print('DATA',data_arr)
    
    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'area_arr':area_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/port_report.html', context)

def k9_request_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/k9_request_date.html', context)
    
def ajax_k9_request_report(request):
    data_arr = None
    to_date = None
    from_date = None
    
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')
      
        data_arr = Dog_Request.objects.filter(start_date__range=[from_date, to_date]).filter(status='Done').order_by('event_name')

        # for data in data_arr:
        #     print(data.event_name)

    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/k9_request_report.html', context)

def fou_acc_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/fou_acc_date.html', context)
    
def ajax_fou_acc_report(request):
    data_arr = None
    to_date = None
    from_date = None
    
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        data_arr = Handler_Incident.objects.filter(date__range=[from_date, to_date]).filter(status='Done').order_by('handler__fullname')
        
    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/fou_acc_report.html', context)

def k9_incident_summary_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/k9_incident_summary_date.html', context)
    
def ajax_k9_incident_summary_report(request):
    data_arr = None
    arr_val = []
    to_date = None
    from_date = None
    
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        data_arr = K9_Incident.objects.filter(date__range=[from_date, to_date]).order_by('k9__name')

        b = K9_Incident.objects.filter(date__range=[from_date, to_date]).filter(incident='Sick').count()
        c = K9_Incident.objects.filter(date__range=[from_date, to_date]).filter(incident='Accident').count()
        d = K9_Incident.objects.filter(date__range=[from_date, to_date]).filter(incident='Missing').count()
        e = K9_Incident.objects.filter(date__range=[from_date, to_date]).filter(incident='Lost').count()
        f =  K9_Incident.objects.filter(date__range=[from_date, to_date]).filter(incident='Stolen').count() 

        arr_val.append(['Sick', b])      
        arr_val.append(['Accident', c])      
        # arr_val.append(['Missing', d])   
        arr_val.append(['Lost', e])      
        arr_val.append(['Stolen', f])      
         
    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'data1':arr_val,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/k9_incident_summary_report.html', context)

def k9_breeding_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/k9_breeding_date.html', context)
    
def ajax_k9_breeding_report(request):
    data_arr = []
    arr_val = []
    to_date = None
    from_date = None
    
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')
 
        m =  K9_Litter.objects.filter(date__range=[from_date, to_date]).values('mother__breed').distinct().order_by('mother__breed')
        
        val = []
        for data in m:
            for key, value in data.items():
                if key == 'mother__breed':
                    val.append(value)

        val = np.unique(val)
        # print(val)
        for data in val:
            birth = K9_Litter.objects.filter(date__range=[from_date, to_date]).filter(mother__breed=data).aggregate(sum=Sum('litter_no'))['sum']
            
            died = K9_Litter.objects.filter(date__range=[from_date, to_date]).filter(mother__breed=data).aggregate(sum=Sum('litter_died'))['sum']

            if birth == None:
                birth = 0
            if died == None:
                died = 0
            
            res = birth - died

            a = [data,died,res]
            arr_val.append(a)


        data_arr = K9_Litter.objects.filter(date__range=[from_date, to_date]).order_by('date','mother','father')
                
        print(arr_val)

    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'data1':arr_val,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/k9_breeding_report.html', context)

def health_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/health_date.html', context)
    
def ajax_health_report(request):
    data_arr = []
    arr_val = []
    to_date = None
    from_date = None
    
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        arr_val = Health.objects.filter(date__range=[from_date, to_date]).filter(status='Done').order_by('date','dog__name')
        for data in arr_val:
            hm = HealthMedicine.objects.filter(health=data)
            data_arr.append([data,hm])

        # print(data_arr)

    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'data1':arr_val,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/health_report.html', context)

def inventory_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/inventory_date.html', context)
    
def ajax_inventory_report(request):
    data_arr = []
    arr_val = []
    arr_val2 = []
    arr_val3 = []
    to_date = None
    from_date = None
    
    mst_cost=0
    fst_cost=0
    misc_cost=0
    total=0
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        mst = Medicine_Subtracted_Trail.objects.filter(date_subtracted__range=[from_date, to_date]).values('inventory').order_by('inventory').distinct()
        for data in mst:
            for key,value in data.items():
                if key == 'inventory':
                    a = Medicine_Inventory.objects.get(id=value)
                    b = Medicine_Subtracted_Trail.objects.filter(date_subtracted__range=[from_date, to_date]).filter(inventory=value).aggregate(sum=Sum('quantity'))['sum']
                    c = a.medicine.price * b 

                    x = [a, a.medicine.uom, a.medicine.price, b, c]
                    arr_val.append(x)
                    mst_cost = mst_cost+c

        fst = Food_Subtracted_Trail.objects.filter(date_subtracted__range=[from_date, to_date]).values('inventory').order_by('inventory').distinct()
        
        for data in fst:
            for key,value in data.items():
                if key == 'inventory':
                    a = Food.objects.get(id=value)
                    b = Food_Subtracted_Trail.objects.filter(date_subtracted__range=[from_date, to_date]).filter(inventory=value).aggregate(sum=Sum('quantity'))['sum']
                    c = a.price * b 
                    
                    x = [a, a.unit, a.price, b, c]
                    arr_val2.append(x)
                    fst_cost=fst_cost+c

        miscst = Miscellaneous_Subtracted_Trail.objects.filter(date_subtracted__range=[from_date, to_date]).values('inventory').order_by('inventory').distinct()
        
        for data in miscst:
            for key,value in data.items():
                if key == 'inventory':
                    a = Miscellaneous.objects.get(id=value)
                    b = Miscellaneous_Subtracted_Trail.objects.filter(date_subtracted__range=[from_date, to_date]).filter(inventory=value).aggregate(sum=Sum('quantity'))['sum']
                    c = a.price * b 
                    
                    x = [a, a.uom, a.price, b, c]
                    arr_val3.append(x)
                    misc_cost=misc_cost+c

        total = mst_cost+fst_cost+misc_cost
        print(total)
    except:
        pass
    user = user_session(request)
    context = {
        'total':total,
        'mst_cost':mst_cost,
        'fst_cost':fst_cost,
        'misc_cost':misc_cost,
        'data':data_arr,
        'data1':arr_val,
        'data2':arr_val2,
        'data3':arr_val3,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/inventory_report.html', context)

def physical_count_med_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/physical_count_med_date.html', context)
    
def ajax_physical_count_med_report(request):
    data_arr = []
    to_date = None
    from_date = None
  
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        orderbyList = ['date_counted', 'time']
        data_arr = Medicine_Inventory_Count.objects.filter(date_counted__range=[from_date, to_date]).order_by(*orderbyList)

    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/physical_count_med_report.html', context)

def physical_count_misc_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/physical_count_misc_date.html', context)
    
def ajax_physical_count_misc_report(request):
    data_arr = []
    to_date = None
    from_date = None
  
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        orderbyList = ['date_counted', 'time']
        data_arr = Miscellaneous_Inventory_Count.objects.filter(date_counted__range=[from_date, to_date]).order_by(*orderbyList)
    
    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/physical_count_misc_report.html', context)
    
def physical_count_food_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/physical_count_food_date.html', context)
    
def ajax_physical_count_food_report(request):
    data_arr = []
    to_date = None
    from_date = None
    user = user_session(request)
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        orderbyList = ['date_counted', 'time']
        data_arr = Food_Inventory_Count.objects.filter(date_counted__range=[from_date, to_date]).order_by(*orderbyList)
        
    except:
        pass

    context = {
        'data':data_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/physical_count_food_report.html', context)

def received_med_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }
    return render(request, 'planningandacquiring/received_med_date.html', context)
    
def ajax_received_med_report(request):
    data_arr = []
    to_date = None
    from_date = None

    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        orderbyList = ['date_received', 'time']
        data_arr = Medicine_Received_Trail.objects.filter(date_received__range=[from_date, to_date]).order_by(*orderbyList)

    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/received_med_report.html', context)

def received_misc_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/received_misc_date.html', context)
    
def ajax_received_misc_report(request):
    data_arr = []
    to_date = None
    from_date = None
  
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        orderbyList = ['date_received', 'time']
        data_arr = Miscellaneous_Received_Trail.objects.filter(date_received__range=[from_date, to_date]).order_by(*orderbyList)
    
    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/received_misc_report.html', context)
    
def received_food_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/received_food_date.html', context)
    
def ajax_received_food_report(request):
    data_arr = []
    to_date = None
    from_date = None
  
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        orderbyList = ['date_received', 'time']
        data_arr = Food_Received_Trail.objects.filter(date_received__range=[from_date, to_date]).order_by(*orderbyList)
        
    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/received_food_report.html', context)

def on_leave_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/on_leave_date.html', context)

def ajax_on_leave_report(request):
    data_arr = []
    to_date = None
    from_date = None

    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')
      
        hl = Handler_On_Leave.objects.filter(date_from__range=[from_date, to_date]).filter(status='Approved').values('handler').order_by('handler__fullname').distinct()
        el = Emergency_Leave.objects.filter(date_of_leave__range=[from_date, to_date]).filter(status='Returned').values('handler').order_by('handler__fullname').distinct()
      
        val_arr=[]
        for data in hl:
            for key, value in data.items():
                if key == 'handler':
                    val_arr.append(value)

        for data in el:
            for key, value in data.items():
                if key == 'handler':
                    val_arr.append(value)

        val_arr = pd.unique(val_arr)
    
        for data in val_arr:
            handler = User.objects.get(id=data)
            # print(handler)
         
            hll = Handler_On_Leave.objects.filter(date_from__range=[from_date, to_date]).filter(handler=handler).filter(status='Approved').aggregate(sum=Sum('duration'))['sum']
            ell = Emergency_Leave.objects.filter(date_of_leave__range=[from_date, to_date]).filter(handler=handler).filter(status='Returned').aggregate(sum=Sum('duration'))['sum']
            if ell == None:
                ell = 0
            if hll == None:
                hll=0

            x = [handler,hll,ell, hll+ell]
            # print(hl,el)
            data_arr.append(x)

        # print(data_arr)
    except:
        print('EXCEPT')

    user = user_session(request)
    context = {
        'data':data_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/on_leave_report.html', context)

def demand_supply_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/demand_supply_date.html', context)
    
def ajax_demand_supply_report(request):
    data_arr = []
    to_date = None
    from_date = None
    edd= None
    ndd= None
    sar= None
    edd_train= None
    ndd_train= None
    sar_train= None
    dif_edd= None
    dif_ndd= None
    dif_sar= None
    total_demand= None
    total_supply= None
    total_dif= None
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        edd = Team_Assignment.objects.filter(date_added__range=[from_date, to_date]).aggregate(sum=Sum('EDD_demand'))['sum']
        ndd = Team_Assignment.objects.filter(date_added__range=[from_date, to_date]).aggregate(sum=Sum('NDD_demand'))['sum']
        sar = Team_Assignment.objects.filter(date_added__range=[from_date, to_date]).aggregate(sum=Sum('SAR_demand'))['sum']
        
        if not edd:
            edd = 0
        if not ndd:
            ndd = 0
        if not sar:
            sar = 0
      

        edd_train = Training.objects.filter(date_finished__range=[from_date, to_date]).filter(k9__trained='Trained').filter(k9__capability='EDD').exclude(Q(k9__status='Material Dog') | Q(k9__status='Adopted') | Q(k9__status='Retired') | Q(k9__status='Dead') | Q(k9__status='Stolen') | Q(k9__status='Lost')).count()

        ndd_train = Training.objects.filter(date_finished__range=[from_date, to_date]).filter(k9__trained='Trained').filter(k9__capability='NDD').exclude(Q(k9__status='Material Dog') | Q(k9__status='Adopted') | Q(k9__status='Retired') | Q(k9__status='Dead') | Q(k9__status='Stolen') | Q(k9__status='Lost')).count()

        sar_train = Training.objects.filter(date_finished__range=[from_date, to_date]).filter(k9__trained='Trained').filter(k9__capability='SAR').exclude(Q(k9__status='Material Dog') | Q(k9__status='Adopted') | Q(k9__status='Retired') | Q(k9__status='Dead') | Q(k9__status='Stolen') | Q(k9__status='Lost')).count()
        
        dif_edd = edd_train - edd
        dif_ndd = ndd_train - ndd
        dif_sar = sar_train - sar

        total_demand = edd + ndd + sar
        total_supply = edd_train + ndd_train + sar_train
        total_dif = total_supply - total_demand

    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
        'edd': edd,
        'ndd': ndd,
        'sar': sar,
        'edd_train': edd_train,
        'ndd_train': ndd_train,
        'sar_train': sar_train,
        'dif_edd': dif_edd,
        'dif_ndd': dif_ndd,
        'dif_sar': dif_sar,
        'total_demand': total_demand,
        'total_supply': total_supply,
        'total_dif': total_dif,
    }

    return render(request, 'planningandacquiring/demand_supply_report.html', context)

def supplier_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/supplier_date.html', context)
    
def ajax_supplier_report(request):
    data_arr = []
    grand_arr = []
    to_date = None
    from_date = None
  
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')

        #SUPPLIER
        sup = K9.objects.filter(date_created__range=[from_date, to_date]).filter(source='Procurement').exclude(supplier=None).values('supplier').distinct().order_by('supplier__name')
        
        
        val_arr =[]
        for sup in sup:
            for key,value in sup.items():
                # print(key, value)
                if key == 'supplier':        
                    val_arr.append(value)

        val_arr =  pd.unique(val_arr)
        # print('SUPPLIER', val_arr)
        for val in val_arr:
            supplier = K9_Supplier.objects.get(id=val)
            # print('sup', supplier)
            breed = K9.objects.filter(supplier=supplier).filter(date_created__range=[from_date, to_date]).values('breed').distinct().order_by('breed')
            
            arr1 =[]
            for breed in breed:
                for key,value in breed.items():
                    if key == 'breed':
                        arr1.append(value)

            arr1 = pd.unique(arr1)
            # print('ARR1',arr1)

            arr2 = []

            for arr in arr1:
                trained = K9.objects.filter(supplier=supplier).filter(breed=arr).filter(date_created__range=[from_date, to_date]).filter(trained='Trained').count()

                failed = K9.objects.filter(supplier=supplier).filter(breed=arr).filter(date_created__range=[from_date, to_date]).filter(trained='Failed').count()

                on_training = K9.objects.filter(supplier=supplier).filter(breed=arr).filter(date_created__range=[from_date, to_date]).filter(trained=None).count()
                
                total = trained + failed + on_training    
                a = [arr,trained,failed,on_training,total,supplier]
                arr2.append(a)

            # print('ARR2',arr2)
            
            g_trained = K9.objects.filter(supplier=supplier).filter(date_created__range=[from_date, to_date]).filter(trained='Trained').count()

            g_failed = K9.objects.filter(supplier=supplier).filter(date_created__range=[from_date, to_date]).filter(trained='Failed').count()

            g_on_training = K9.objects.filter(supplier=supplier).filter(date_created__range=[from_date, to_date]).filter(trained=None).count()

            grand_total = g_trained + g_failed + g_on_training
            y = [supplier,g_trained,g_failed,g_on_training,grand_total]
            grand_arr.append(y)

            first = arr2[0]
            arr2.remove(arr2[0])
            x = (supplier, arr2, len(arr1),first)
            data_arr.append(x)

        # print('DATA ARR', data_arr)
    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'grand_arr':grand_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/supplier_report.html', context)

def adoption_date(request):
    form = ReportDateForm(request.POST or None)

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)

     
    #     # for i in range(10):
    # K9.objects.create(name='Lola'+str(i), handler=user, breed='Jack Russel',sex='Female',color='Cream', birth_date=date.today(),source='Procurement',status='Working Dog',training_status='For-Deployment',height=20,weight=20)
    context = {
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'form': form,
    }

    return render(request, 'planningandacquiring/adoption_date.html', context)
    
def ajax_adoption_report(request):
    data_arr = []
    to_date = None
    from_date = None
  
    try:
        to_date = request.GET.get('date_to')
        from_date = request.GET.get('date_from')
       
        data_arr = K9_Adopted_Owner.objects.filter(date_adopted__range=[from_date, to_date]).order_by('date_adopted', 'last_name')
      
    except:
        pass
    user = user_session(request)
    context = {
        'data':data_arr,
        'from_date':from_date,
        'to_date':to_date,
        'user': user,
    }

    return render(request, 'planningandacquiring/adoption_report.html', context)

################# END OF REPORT ##################
###################################### AJAX LOAD FUNCTIONS ##################################################
def load_supplier(request):

    supplier = None

    try:
        supplier_id = request.GET.get('supplier')
        supplier = K9_Supplier.objects.get(id=supplier_id)
    except:
        pass
    context = {
        'supplier': supplier,
    }

    return render(request, 'planningandacquiring/supplier_data.html', context)

def load_k9_reco(request):

    h_count_arr = []
    k9_arr = []
    b_arr = []
    #TODO check
    try:
        id = request.GET.get('id')
        k9 = K9.objects.get(id=id)
       
        try:
            kp = K9_Parent.objects.filter(mother=k9)
            k9_o = K9_Parent.objects.get(offspring=k9)

            kp_id=[]
            for k in kp:
                kp_id.append(k.offspring.id)
            
            k9_m = K9_Parent.objects.filter(mother=k9_o.mother)
            k9_f = K9_Parent.objects.filter(father=k9_o.father)
            
            for m in k9_m:
                kp_id.append(m.offspring.id)

            for f in k9_f:
                kp_id.append(f.offspring.id)
        except ObjectDoesNotExist:
            kp_id = None

        # print(kp_id)

        if kp_id != None:
            k9_data = K9.objects.filter(sex="Male").filter(training_status = "For-Breeding").filter(breed=k9.breed).filter(capability=k9.capability).filter(age__gte= 1).exclude(id__in=kp_id).order_by('-litter_no')
        else:
            k9_data = K9.objects.filter(sex="Male").filter(training_status = "For-Breeding").filter(breed=k9.breed).filter(capability=k9.capability).filter(age__gte= 1).order_by('-litter_no')
        
        # print(k9_data)
        for k in k9_data:
            h_count = Health.objects.filter(dog=k).count()
            h_count_arr.append(h_count)   
            k9_arr.append(k)

            birth = K9_Litter.objects.filter(father=k).aggregate(sum=Sum('litter_no'))['sum']
            death = K9_Litter.objects.filter(father=k).aggregate(sum=Sum('litter_died'))['sum']

            if birth != None or death != None:
                total = (birth / (birth+death)) * 100
            else:
                total=100
            
            b_arr.append(int(total))

    except:
        pass

    flist = zip(k9_arr,h_count_arr, b_arr)

    context = {
        'k9': k9,
        'flist':flist,
    }

    return render(request, 'planningandacquiring/breeding_reco_data.html', context)
    
def load_health(request):

    health = None
    k9 = None
    try:
        k9 = request.GET.get('k9')
        k9_id = request.GET.get('id')
        health = Health.objects.filter(dog__id=k9_id) 
    except:
        pass

    context = {
        'health': health,
        'k9': k9,
    }

    return render(request, 'planningandacquiring/health_data.html', context)

def load_form(request):
    formset = None
    try:
        num = request.GET.get('num')
        # print(num)
        k9_formset = formset_factory(add_offspring_K9_form, extra=int(num), can_delete=False)
        formset = k9_formset(request.POST, request.FILES)
    except:
        pass

    context = {
        'formset': k9_formset(),
    }

    return render(request, 'planningandacquiring/offspring_form_data.html', context)

def load_form_procured(request):
    formset = None
    formset2 = None
    try:
        num = request.GET.get('num')
        num = int(num)
        k9_formset = formset_factory(ProcuredK9Form, extra=num, can_delete=False)
        formset = k9_formset(request.POST, request.FILES)

    except:
        pass

    context = {
        'formset': k9_formset(),
    }

    return render(request, 'planningandacquiring/procured_form_data.html', context)

def load_budget_data(request):
    breed = None
    try:
        breed_id = request.GET.get('id')
        db = Dog_Breed.objects.get(id=breed_id)
      
    except:
        pass

    data = {
        'breed':db.id,
        'value':db.value,
    }

    return JsonResponse(data)

def budgeting(request):

    #K9 and FOOD
    k9_puppy = K9.objects.filter(age__lt=1).count()
    k9_adult = K9.objects.filter(age__gte=1).count()

    fm_st = Food_Subtracted_Trail.objects.filter(inventory__foodtype='Milk').count()
    pdf_st = Food_Subtracted_Trail.objects.filter(inventory__foodtype='Puppy Dog Food').count()
    adf_st = Food_Subtracted_Trail.objects.filter(inventory__foodtype='Adult Dog Food').count()
    
    misc_st = Miscellaneous.objects.all().count()

    #VACCINE
    ar_st = Medicine.objects.filter(immunization='Anti-Rabies').count()
    bbb_st = Medicine.objects.filter(immunization='Bordetella Bronchiseptica Bacterin').count()
    dw_st = Medicine.objects.filter(immunization='Deworming').count()
    dh4_st = Medicine.objects.filter(immunization='DHPPiL4').count()
    dhc_st = Medicine.objects.filter(immunization='DHPPiL+CV').count()
    hw_st = Medicine.objects.filter(immunization='Heartworm').count()
    tt_st = Medicine.objects.filter(immunization='Tick and Flea').count()

    #BREED
    bm_st = Dog_Breed.objects.filter(breed = "Belgian Malinois").count()
    ds_st = Dog_Breed.objects.filter(breed = "Dutch Sheperd").count()
    gs_st = Dog_Breed.objects.filter(breed = "German Sheperd").count()
    gr_st = Dog_Breed.objects.filter(breed = "Golden Retriever").count()
    jr_st = Dog_Breed.objects.filter(breed = "Jack Russel").count()
    lr_st = Dog_Breed.objects.filter(breed = "Labrador Retriever").count()

    
    breed_st = False
    if bm_st > 0 and ds_st > 0 and gs_st > 0 and gr_st > 0 and jr_st > 0 and lr_st > 0:
        breed_st = True

    #Double check
    dfood = False
    if k9_adult > 0 and adf_st > 0:
        dfood = True
    else:
        dfood = False

    if k9_puppy > 0 and pdf_st > 0 and fm_st > 0:
        dfood = True
    elif k9_puppy <= 0 and pdf_st > 0 or fm_st > 0:
        dfood = True
    elif k9_puppy <= 0 and pdf_st <= 0 or fm_st <= 0:
        dfood = False

    # print(dfood, breed_st, misc_st, ar_st, bbb_st, dw_st, dh4_st, dhc_st, hw_st, tt_st, fm_st, pdf_st, adf_st)
    generate = False
    if breed_st == True and dfood == True and misc_st > 0 and ar_st > 0 and bbb_st > 0 and dw_st > 0 and dh4_st > 0 and dhc_st > 0 and hw_st > 0 and tt_st > 0 and fm_st > 0 and pdf_st > 0 and adf_st > 0:
        generate = True

    # print('K9', k9_st)
    # print('Breed', breed_st)
    # print('Food Subtract Trail', f_st)
    # print('Medicine Subtract Trail', med_st)
    # print('Miscellaous Subtract Trail', misc_st)
    # print('Medicine', ar_st, bbb_st, dw_st, dh4_st, dhc_st, hw_st, tt_st)

    # print('Food', dfood)
    # print('Generate', generate)

    #INITIALIZE
    k9_formset = formset_factory(k9_acquisition_form, extra=1, can_delete=True)
    formset = k9_formset(request.POST, request.FILES)
    next_year = dt.now().year + 1
    current_year = dt.now().year
    need_procure_ny = 0
    k9_cy = 0
    k9_ny = 0
    born_ny = 0
    dead_list = 0
    total_k9 = 0
    NDD_count = 0
    EDD_count = 0
    SAR_count = 0
    NDD_demand = 0
    EDD_demand = 0
    SAR_demand = 0
    sar = 0
    ndd = 0
    edd = 0
    #??
    puppy_current = 0
    adult_current = 0
    total_milk_needed = 0
    total_puppy_food  = 0
    total_adult_food  = 0
    milk_quantity = 0
    milk_quantity_total = 0
    puppy_quantity = 0
    puppy_quantity_total = 0
    adult_quantity = 0
    adult_quantity_total = 0
    #SHOW BUDGET FORM
    if generate == True:
        all_k9 = K9.objects.exclude(status="Adopted").exclude(status="Dead").exclude(status="Stolen").exclude(status="Lost")
        
        #K9 to be born and die
        k9_breeded = K9_Mated.objects.filter(status='Pregnant')
        # print(k9_breeded)
        ny_breeding = [] 
        ny_data = []
        for kb in k9_breeded:
            m = kb.date_mated  + timedelta(days=63)
            if m.year == next_year:
                ny = [kb.mother.breed, kb.mother.litter_no]
                ny_data.append(ny)
                ny_breeding.append(kb.mother.breed)
                #get k9, value, total count by breed
            
        kb_index = pd.Index(ny_breeding)

        b_values = kb_index.value_counts().keys().tolist() #k9 breed to be born
        b_counts = kb_index.value_counts().tolist() #number of k9 to be born by breed

        #Total count of all dogs born next year by breed,
        breed_u = np.unique(ny_breeding)

        p = pd.DataFrame(ny_data, columns=['Breed', 'Litter'])
        h = p.groupby(['Breed']).sum()

        total_born = []  
        total_born_count = []  
        for u in breed_u:
            total_born_count.append(h.loc[u].values[0])
            born = [u,h.loc[u].values[0]]
            total_born.append(born)

        ny_dead = []
        for kd in all_k9:
            b = Dog_Breed.objects.filter(sex='Male').get(breed = kd.breed)
            if (kd.age + 1) >= b.life_span:
                ny_dead.append(kd.breed)
            

        kd_index = pd.Index(ny_dead)
        #TODO
        # dead values and count
        d_values = kd_index.value_counts().keys().tolist()
        d_counts = kd_index.value_counts().tolist()

        if d_values:
            dead_list = zip(d_values,d_counts)
        else:
            dead_list=None

        all_k = all_k9.values_list('breed', flat=True).order_by()

        all_ku = np.unique(all_k)

        all_dogs = K9.objects.exclude(status="Adopted").exclude(status="Dead").exclude(status="Stolen").exclude(status="Lost").count()

        all_kk = []
        for a in all_ku:
            c = all_k9.filter(breed=a).count()
            cc = [a,c]
            all_kk.append(cc)

        k9_cy = all_dogs
        k9_ny = all_dogs - sum(d_counts)
        k9_t_ny = k9_cy+50

        difference_k9 = k9_cy - k9_ny
        born_ny=0
        for b in k9_breeded:
            d = Dog_Breed.objects.filter(sex='Female').get(breed=b.mother.breed)
            born_ny = born_ny + d.litter_number

        
        NDD_count = K9.objects.filter(capability='NDD').exclude(status="Adopted").exclude(status="Dead").exclude(status="Stolen").exclude(status="Lost").count()
        EDD_count = K9.objects.filter(capability='EDD').exclude(status="Adopted").exclude(status="Dead").exclude(status="Stolen").exclude(status="Lost").count()
        SAR_count = K9.objects.filter(capability='SAR').exclude(status="Adopted").exclude(status="Dead").exclude(status="Stolen").exclude(status="Lost").count()

        NDD_demand = list(Team_Assignment.objects.aggregate(Sum('NDD_demand')).values())[0]
        EDD_demand = list(Team_Assignment.objects.aggregate(Sum('EDD_demand')).values())[0]
        SAR_demand = list(Team_Assignment.objects.aggregate(Sum('SAR_demand')).values())[0]

        if not NDD_demand:
            NDD_demand = 0
        if not EDD_demand:
            EDD_demand = 0
        if not SAR_demand:
            SAR_demand = 0

        sar = Dog_Breed.objects.filter(skill_recommendation='SAR').filter(sex='Male')
        ndd = Dog_Breed.objects.filter(skill_recommendation='NDD').filter(sex='Male')
        edd = Dog_Breed.objects.filter(skill_recommendation='EDD').filter(sex='Male')

        if request.method == "POST":
            
            need_procure_ny =  int(request.POST.get('id_need'))
            procured_total =  Decimal(request.POST.get('id_need_total'))
            total_k9_next_year = need_procure_ny + k9_ny + born_ny

            # print('TOTAL K9', total_k9_next_year)

            ###### START OF LOAD BUDGET ######
            # GET NEEDED DOG FOOD
            puppy_current = all_k9.filter(age__lt=1).count()
            adult_current = all_k9.filter(age__gte=1).count()
            total_milk_needed = (born_ny + puppy_current) * 21
            total_puppy_food  = (((born_ny + puppy_current) * 15) * 9) / 20
            total_adult_food  = (adult_current + need_procure_ny) * 12

            # print('NEEDED DOG FOOD',total_milk_needed,total_puppy_food,total_adult_food)

            #GET CURRENT DOG FOOD
            current_milk = Food.objects.filter(foodtype='Milk').aggregate(sum=Sum('quantity'))['sum']
            current_puppy_food = Food.objects.filter(foodtype='Puppy Dog Food').aggregate(sum=Sum('quantity'))['sum']
            current_adult_food = Food.objects.filter(foodtype='Adult Dog Food').aggregate(sum=Sum('quantity'))['sum']

            # print('CURRENT DOG FOOD',current_milk,current_puppy_food,current_adult_food)

            #GET DOG FOOD MOST USED QUANTITY
            #MILK
            milk_item = Food_Subtracted_Trail.objects.filter(inventory__foodtype='Milk').filter(date_subtracted__year=current_year).values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity')[0]

            m_item = None # milk item most used
            if milk_item:
                for key, value in milk_item.items(): 
                    if key == 'inventory':
                        m_item = value

                m_item = Food.objects.get(id=m_item)

            #PUPPY DOG FOOD
            puppy_item = Food_Subtracted_Trail.objects.filter(inventory__foodtype='Puppy Dog Food').filter(date_subtracted__year=current_year).values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity')[0]

            p_item = None # puppy food item most used
            if puppy_item:
                for key, value in puppy_item.items(): 
                    if key == 'inventory':
                        p_item = value
                p_item = Food.objects.get(id=p_item)

            #ADULT DOG FOOD
            adult_item = Food_Subtracted_Trail.objects.filter(inventory__foodtype='Adult Dog Food').filter(date_subtracted__year=current_year).values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity')[0]
            
            a_item = None # Adult food item most used
            if adult_item:
                for key, value in adult_item.items(): 
                    if key == 'inventory':
                        a_item = value
                a_item = Food.objects.get(id=a_item)
            
            food_arr = []
            if total_milk_needed>0:
                if m_item:  
                # CALCULATE PRICE AND TOTAL OF DOG FOOD
                    # milk needed = total_milk_needed , current = current_milk 
                    # needed - current * price
                    milk_quantity = total_milk_needed - current_milk
                    if milk_quantity < 0:
                        milk_quantity = 0
                    print('M ITEM',total_milk_needed,current_milk)
                    milk_quantity_total = int(np.ceil(milk_quantity)) * m_item.price
                    # print('MILK', m_item, milk_quantity, milk_quantity_total)
                    if milk_quantity_total > 0:
                        food_arr.append([m_item,milk_quantity,milk_quantity_total])

            if total_puppy_food>0:
                if p_item:
                    #puppy food needed = total_puppy_food , current = current_puppy_food 
                    puppy_quantity = total_puppy_food - current_puppy_food
                    if puppy_quantity < 0:
                        puppy_quantity = 0
                    puppy_quantity_total = int(np.ceil(puppy_quantity)) * p_item.price
                    # print('PUPPY FOOD', p_item, puppy_quantity, puppy_quantity_total)
                    if puppy_quantity_total > 0:
                        food_arr.append([p_item,int(puppy_quantity),puppy_quantity_total])

            if total_adult_food > 0:
                if a_item:
                    #adult food needed = total_adult_food , current = current_adult_food 
                    adult_quantity = total_adult_food - current_adult_food
                    if adult_quantity < 0:
                        adult_quantity = 0
                    adult_quantity_total = int(np.ceil(adult_quantity)) * a_item.price
                    # print('ADULT FOOD', a_item,adult_quantity, adult_quantity_total)
                    if adult_quantity_total > 0:
                        food_arr.append([a_item,int(adult_quantity),adult_quantity_total])

            mrt = Medicine_Received_Trail.objects.filter(expiration_date__year=next_year).filter(status='Pending').values('inventory').annotate(sum = Sum('quantity'))

            med_item_id = []
            med_item_q = []
            for m in mrt: 
                for key,value in m.items():
                    if key == 'inventory':
                        med_item_id.append(value)
                    else:
                        med_item_q.append(value)

            zip_a = zip(med_item_id, med_item_q)

            # Medicine that has expirations next year
            ny_med = []
            cy_med = [] 
            eny_ar_count = 0
            eny_bbb_count = 0
            eny_dw_count = 0
            eny_dcv_count = 0
            eny_dc4_count = 0
            eny_hw_count = 0
            eny_tf_count = 0
            
            for a,b in zip_a:  
                c = Medicine_Inventory.objects.get(id=a)
                x = [c, (c.quantity - b)]
                z = [c, c.quantity]
                ny_med.append(x)
                cy_med.append(z)

                if c.medicine.immunization == 'Anti-Rabies':
                    eny_ar_count = eny_ar_count + b
                elif c.medicine.immunization == 'Bordetella Bronchiseptica Bacterin':
                    eny_bbb_count = eny_bbb_count + b
                elif c.medicine.immunization == 'Deworming':
                    eny_dw_count = eny_dw_count + b
                elif c.medicine.immunization == 'DHPPiL+CV':
                    eny_dcv_count = eny_dcv_count + b
                elif c.medicine.immunization == 'DHPPiL4':
                    eny_dc4_count = eny_dc4_count + b
                elif c.medicine.immunization == 'Heartworm':
                    eny_hw_count = eny_hw_count + b
                elif c.medicine.immunization == 'Tick and Flea':
                    eny_tf_count = eny_tf_count + b

            #get all medicine used in the current year exclude vaccine
            mst_cy = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).exclude(inventory__medicine__med_type='Vaccine').exclude(inventory__medicine__med_type='Preventive').values('inventory').distinct()
            mst_ny = []
            np_arr = np.array(ny_med)
            for mst in mst_cy:
                for key,value in mst.items():
                    if key == 'inventory':
                        c = Medicine_Inventory.objects.get(id=value)
                        if c in np_arr:
                            for (n, (item1, item2)) in enumerate(ny_med):
                                if c == item1:
                                    a = [c, item2, c.medicine.price]
                                    mst_ny.append(a)
                        else:
                            a = [c, c.quantity, c.medicine.price]
                            mst_ny.append(a)

            #med needed to procure next year and total
            b_ny_med = [] #buy next year medicine
            total_medicine = 0
            for (n, (item1, item2, item3)) in enumerate(mst_ny):
                ms = Medicine_Subtracted_Trail.objects.filter(inventory=item1).aggregate(sum=Sum('quantity'))['sum']
                r = ms / k9_cy
                r = r * (k9_ny+born_ny+need_procure_ny) - item2

                if np.ceil(r) > 0:
                    s = Decimal(np.ceil(r)) * Decimal(item3)
                    ss = round(s, 2)
                    b = [item1,int(np.ceil(r)),ss]
                    b_ny_med.append(b)
                    total_medicine = total_medicine+ss

            vac_arr = []

            # CALCULATE Vaccine 
            # ANTI-RABIES Calculation
            ar_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='Anti-Rabies').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

            if ar_item == None:
                ar_item = Medicine_Received_Trail.objects.filter(date_received__year=current_year).filter(inventory__medicine__immunization='Anti-Rabies').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

            if ar_item == None:
                ar_item = Medicine.objects.filter(immunization='Anti-Rabies').last()

            if type(ar_item).__name__ == 'dict':
                for key, value in ar_item.items():
                    if key == 'inventory':
                        ar_item = value

                ar_item = Medicine_Inventory.objects.get(id=ar_item).medicine.id
                ar_item = Medicine.objects.get(id=ar_item) 

            ar_current = Medicine_Inventory.objects.filter(medicine__immunization='Anti-Rabies').aggregate(sum=Sum('quantity'))['sum']

            ar_quantity = (total_k9_next_year * 1) - ar_current
            if ar_quantity < 0:
                ar_quantity = 0
            ar_total = round(int(np.ceil(ar_quantity)) * ar_item.price,2)
            # print(ar_item, ar_quantity, ar_total)
            if ar_total>0:
                vac_arr.append([ar_item,ar_quantity,ar_total])

            #BORDERTELLA CALCULATION
            bbb_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='Bordetella Bronchiseptica Bacterin').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()
            if bbb_item == None:
                bbb_item = Medicine_Received_Trail.objects.filter(date_received__year=current_year).filter(inventory__medicine__immunization='Bordetella Bronchiseptica Bacterin').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()
            
            if bbb_item == None:
                bbb_item = Medicine.objects.filter(immunization='Bordetella Bronchiseptica Bacterin').last()

            if type(bbb_item).__name__ == 'dict':
                for key, value in bbb_item.items():
                    if key == 'inventory':
                        bbb_item = value

                bbb_item = Medicine_Inventory.objects.get(id=bbb_item).medicine.id
                bbb_item = Medicine.objects.get(id=bbb_item)  


            bbb_current = Medicine_Inventory.objects.filter(medicine__immunization='Bordetella Bronchiseptica Bacterin').aggregate(sum=Sum('quantity'))['sum']

            mandatory_bbb1 = VaccinceRecord.objects.filter(bordetella_1=False).filter(k9__in=all_k9).count()
            mandatory_bbb2 = VaccinceRecord.objects.filter(bordetella_2=False).filter(k9__in=all_k9).count()

            bbb_quantity = (mandatory_bbb1 + mandatory_bbb2 + born_ny) - bbb_current
            if bbb_quantity < 0:
                bbb_quantity = 0
            bbb_total = round(int(np.ceil(bbb_quantity)) * bbb_item.price,2)
            # print(bbb_item, bbb_quantity, bbb_total)
            if bbb_total>0:
                vac_arr.append([bbb_item,bbb_quantity,bbb_total])

            #DHPPIL+CV CALCULATION
            dhcv_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='DHPPiL+CV').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

            if dhcv_item == None:
                dhcv_item = Medicine_Received_Trail.objects.filter(date_received__year=current_year).filter(inventory__medicine__immunization='DHPPiL+CV').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

            if type(dhcv_item).__name__ == 'dict':
                for key, value in dhcv_item.items():
                    if key == 'inventory':
                        dhcv_item = value

                dhcv_item = Medicine_Inventory.objects.get(id=dhcv_item).medicine.id
                dhcv_item = Medicine.objects.get(id=dhcv_item) 

            
            if dhcv_item == None:
                dhcv_item = Medicine.objects.filter(immunization='DHPPiL+CV').last()

            dhcv_current = Medicine_Inventory.objects.filter(medicine__immunization='DHPPiL+CV').aggregate(sum=Sum('quantity'))['sum']

            mandatory_dhcv1 = VaccinceRecord.objects.filter(dhppil_cv_1=False).filter(k9__in=all_k9).count()
            mandatory_dhcv2 = VaccinceRecord.objects.filter(dhppil_cv_1=False).filter(k9__in=all_k9).count()
            mandatory_dhcv3 = VaccinceRecord.objects.filter(dhppil_cv_1=False).filter(k9__in=all_k9).count()

            dhcv_quantity = (mandatory_dhcv1 + mandatory_dhcv2 + mandatory_dhcv3 + born_ny) - dhcv_current
            if dhcv_quantity < 0:
                dhcv_quantity = 0
            dhcv_total = round(int(np.ceil(dhcv_quantity)) * dhcv_item.price,2)
            # print(dhcv_item, dhcv_quantity, dhcv_total)
            if dhcv_total>0:
                vac_arr.append([dhcv_item,dhcv_quantity,dhcv_total])

            #DHPPiL4 CALCULATION
            dh4_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='DHPPiL4').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

            if dh4_item == None:
                dh4_item = Medicine_Received_Trail.objects.filter(date_received__year=current_year).filter(inventory__medicine__immunization='DHPPiL4').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()
            
            if dh4_item == None:
                dh4_item = Medicine.objects.filter(immunization='DHPPiL4').last()

            if type(dh4_item).__name__ == 'dict':
                for key, value in dh4_item.items():
                    if key == 'inventory':
                        dh4_item = value

                dh4_item = Medicine_Inventory.objects.get(id=dh4_item).medicine.id
                dh4_item = Medicine.objects.get(id=dh4_item)

            dh4_current = Medicine_Inventory.objects.filter(medicine__immunization='DHPPiL4').aggregate(sum=Sum('quantity'))['sum']

            mandatory_dh41 = VaccinceRecord.objects.filter(dhppil4_1=False).filter(k9__in=all_k9).count()
            mandatory_dh42 = VaccinceRecord.objects.filter(dhppil4_2=False).filter(k9__in=all_k9).count()

            dh4_quantity = (mandatory_dh41 + mandatory_dh42 + born_ny) - dhcv_current
            if dh4_quantity < 0:
                dh4_quantity = 0
            dh4_total = round(int(np.ceil(dh4_quantity)) * dh4_item.price,2)
            # print(dh4_item, dh4_quantity, dh4_total)
            if dh4_total>0:
                vac_arr.append([dh4_item,dh4_quantity,dh4_total])

            #DEWORM CALCULATION
            dw_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='Deworming').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

            if dw_item == None:
                dw_item = Medicine_Received_Trail.objects.filter(date_received__year=current_year).filter(inventory__medicine__immunization='Deworming').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

            if type(dw_item).__name__ == 'dict':
                for key, value in dw_item.items():
                    if key == 'inventory':
                        dw_item = value

                dw_item = Medicine_Inventory.objects.get(id=dw_item).medicine.id
                dw_item = Medicine.objects.get(id=dw_item)
            
            if dw_item == None:
                dw_item = Medicine.objects.filter(immunization='Deworming').last()

            dw_current = Medicine_Inventory.objects.filter(medicine__immunization='Deworming').aggregate(sum=Sum('quantity'))['sum']

            mandatory_dw1 = VaccinceRecord.objects.filter(deworming_1=False).filter(k9__in=all_k9).count()
            mandatory_dw2 = VaccinceRecord.objects.filter(deworming_2=False).filter(k9__in=all_k9).count()
            mandatory_dw3 = VaccinceRecord.objects.filter(deworming_3=False).filter(k9__in=all_k9).count()
            mandatory_dw4 = VaccinceRecord.objects.filter(deworming_4=False).filter(k9__in=all_k9).count()
            yearly_dw = VaccinceRecord.objects.filter(Q(deworming_1=True)&Q(deworming_2=True)&Q(deworming_3=True)&Q(deworming_4=True)).filter(k9__in=all_k9).count() * 4

            dw_quantity = (mandatory_dw1 + mandatory_dw2 + mandatory_dw3 + mandatory_dw4) + yearly_dw + (born_ny *4) + (need_procure_ny * 4)- dw_current
            if dw_quantity < 0:
                dw_quantity = 0
            dw_total = round(int(np.ceil(dw_quantity)) * dw_item.price,2)
            # print(dw_item, dw_quantity, dw_total)
            if dw_total>0:
                vac_arr.append([dw_item,dw_quantity,dw_total])

            #HEARTWORM CALCULATION
            hw_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='Heartworm').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()
            
            if hw_item == None:
                hw_item = Medicine.objects.filter(immunization='Heartworm').last()
            
            if type(hw_item).__name__ == 'dict':
                for key, value in hw_item.items():
                    if key == 'inventory':
                        hw_item = value

                hw_item = Medicine_Inventory.objects.get(id=hw_item).medicine.id
                hw_item = Medicine.objects.get(id=hw_item)  


            hw_current = Medicine_Inventory.objects.filter(medicine__immunization='Heartworm').aggregate(sum=Sum('quantity'))['sum']

            mandatory_hw1 = VaccinceRecord.objects.filter(heartworm_1=False).filter(k9__in=all_k9).count()
            mandatory_hw2 = VaccinceRecord.objects.filter(heartworm_2=False).filter(k9__in=all_k9).count()
            mandatory_hw3 = VaccinceRecord.objects.filter(heartworm_3=False).filter(k9__in=all_k9).count()
            mandatory_hw4 = VaccinceRecord.objects.filter(heartworm_4=False).filter(k9__in=all_k9).count()
            mandatory_hw5 = VaccinceRecord.objects.filter(heartworm_5=False).filter(k9__in=all_k9).count()
            mandatory_hw6 = VaccinceRecord.objects.filter(heartworm_6=False).filter(k9__in=all_k9).count()
            mandatory_hw7 = VaccinceRecord.objects.filter(heartworm_7=False).filter(k9__in=all_k9).count()
            mandatory_hw8 = VaccinceRecord.objects.filter(heartworm_8=False).filter(k9__in=all_k9).count()
            yearly_hw = VaccinceRecord.objects.filter(Q(heartworm_1=True)&Q(heartworm_2=True)&Q(heartworm_3=True)&Q(heartworm_4=True)&Q(heartworm_5=True)&Q(heartworm_6=True)&Q(heartworm_7=True)&Q(heartworm_8=True)).filter(k9__in=all_k9).count() * 12

            hw_quantity = (mandatory_hw1 + mandatory_hw2 + mandatory_hw3 + mandatory_hw4 + mandatory_hw5 + mandatory_hw6 + mandatory_hw7 + mandatory_hw8) + yearly_hw + (born_ny *8) + (need_procure_ny * 12) - hw_current
            if hw_quantity < 0:
                hw_quantity = 0
            hw_total = round(int(np.ceil(hw_quantity)) * hw_item.price, 2)
            # print(hw_item, hw_quantity, hw_total)
            if hw_total>0:
                vac_arr.append([hw_item,hw_quantity,hw_total])

            #TICK AND FLEE CALCULATION
            tft_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='Tick and Flea').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

            if tft_item == None:
                tft_item = Medicine_Received_Trail.objects.filter(date_received__year=current_year).filter(inventory__medicine__immunization='Tick and Flea').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()
            
            if tft_item == None:
                tft_item = Medicine.objects.filter(immunization='Tick and Flea').last()

            if type(tft_item).__name__ == 'dict':
                for key, value in tft_item.items(): 
                    if key == 'inventory':
                        tft_item = value

                tft_item = Medicine_Inventory.objects.get(id=tft_item).medicine.id
                tft_item = Medicine.objects.get(id=tft_item)

            tft_current = Medicine_Inventory.objects.filter(medicine__immunization='Tick and Flea').aggregate(sum=Sum('quantity'))['sum']

            mandatory_tft1 = VaccinceRecord.objects.filter(tick_flea_1=False).filter(k9__in=all_k9).count()
            mandatory_tft2 = VaccinceRecord.objects.filter(tick_flea_2=False).filter(k9__in=all_k9).count()
            mandatory_tft3 = VaccinceRecord.objects.filter(tick_flea_3=False).filter(k9__in=all_k9).count()
            mandatory_tft4 = VaccinceRecord.objects.filter(tick_flea_4=False).filter(k9__in=all_k9).count()
            mandatory_tft5 = VaccinceRecord.objects.filter(tick_flea_5=False).filter(k9__in=all_k9).count()
            mandatory_tft6 = VaccinceRecord.objects.filter(tick_flea_6=False).filter(k9__in=all_k9).count()
            mandatory_tft7 = VaccinceRecord.objects.filter(tick_flea_7=False).filter(k9__in=all_k9).count()
            
            yearly_tft = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='Tick and Flea').aggregate(sum=Sum('quantity'))['sum']

            if yearly_tft == None:
                yearly_tft = 0

            m_tft = mandatory_tft1 + mandatory_tft2 + mandatory_tft3 + mandatory_tft4 + mandatory_tft5 + mandatory_tft6 + mandatory_tft7
            
            if yearly_tft < m_tft:
                tft_quantity = m_tft
            else:
                tft_quantity = yearly_tft

            if tft_quantity < 0:
                tft_quantity = 0
            tft_total = round(int(np.ceil(tft_quantity)) * tft_item.price, 2)

            # print("TFT", tft_item)
            if tft_total>0:
                vac_arr.append([tft_item,tft_quantity,tft_total])

            #MISCELLANOUS VET SUPPLY CALCULATION
            vet_item = Miscellaneous_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__misc_type='Vet Supply').values('inventory').annotate(quantity=Sum('quantity')).order_by('inventory')

            vet_arr = []
            vet_total = 0
            if vet_item != None:    
                vet_np_arr =np.array(vet_item)

                for data in vet_np_arr:
                    for key, value in data.items(): 
                        if key == 'inventory':
                            a = Miscellaneous.objects.get(id=value)
                        else:
                            b = value
                            c = round(b * a.price,2)
                    vet_arr.append([a,b,c])
                    vet_total = vet_total + c

            # print('VET', vet_arr)

            #MISCELLANOUS KENNEL SUPPLY CALCULATION
            ken_item = Miscellaneous_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__misc_type='Kennel Supply').values('inventory').annotate(quantity=Sum('quantity')).order_by('inventory')

            ken_arr = []
            ken_total = 0
            if ken_item != None:    
                ken_np_arr =np.array(ken_item)

                for data in ken_np_arr:
                    for key, value in data.items(): 
                        if key == 'inventory':
                            a = Miscellaneous.objects.get(id=value)
                        else:
                            b = value
                            c = round(b * a.price, 2)
                    ken_arr.append([a,b,c])
                    ken_total = ken_total + c
        
            # print('KENNEL', ken_arr)

            #MISCELLANOUS OTHERS CALCULATION
            other_item = Miscellaneous_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__misc_type='Others').values('inventory').annotate(quantity=Sum('quantity')).order_by('inventory')

            other_arr = []
            other_total = 0
            if other_item != None:    
                other_np_arr =np.array(other_item)

                for data in other_np_arr:
                    for key, value in data.items(): 
                        if key == 'inventory':
                            a = Miscellaneous.objects.get(id=value)
                        else:
                            b = value
                            c = round(b * a.price, 2)
                    other_arr.append([a,b,c])
                    other_total = other_total + c

            # print('OTHERS', other_arr)

            # TRAINING CALCULATION
            train_k9 = (born_ny + need_procure_ny)
            training_total = round(Decimal(train_k9 * 18000), 2)
            # print('TRAINING AMOUNT', training_total)

            total_food = milk_quantity_total + puppy_quantity_total + adult_quantity_total
            vac_total = ar_total + bbb_total + dhcv_total + dh4_total + dw_total + hw_total + tft_total
            if vac_total == 0:
                vac_total = None

            total_amount = procured_total+training_total+other_total+ken_total+vet_total+total_medicine+vac_total+total_food
            total_amount = round(total_amount,2)

            ###### END OF LOAD BUDGET ######
            
            try:
                pb = Proposal_Budget.objects.get(date_created__year=dt.today().year)
                pb.k9_current = k9_ny
                pb.k9_needed = need_procure_ny
                pb.k9_breeded = born_ny
                pb.food_milk_total = total_food
                pb.vac_prev_total = vac_total
                pb.medicine_total = total_medicine
                pb.vet_supply_total = vet_total
                pb.kennel_total = ken_total
                pb.others_total = other_total
                pb.training_total = training_total
                pb.train_count = train_k9
                pb.grand_total = total_amount
                pb.date_created = dt.today()
                pb.k9_total = procured_total
                pb.save()

                Proposal_Milk_Food.objects.filter(proposal=pb).delete()
                Proposal_Vac_Prev.objects.filter(proposal=pb).delete()
                Proposal_Medicine.objects.filter(proposal=pb).delete()
                Proposal_Vet_Supply.objects.filter(proposal=pb).delete()
                Proposal_Kennel_Supply.objects.filter(proposal=pb).delete()
                Proposal_Others.objects.filter(proposal=pb).delete()
                Proposal_K9.objects.filter(proposal=pb).delete()
                Proposal_Training.objects.filter(proposal=pb).delete()

                #K9 Acquisition
                if formset.is_valid():
                    for form in formset:
                        if form.is_valid():
                            f=form.save(commit=False)
                            f.percent = Decimal(f.total/total_amount)
                            f.proposal=pb
                            f.save()

                for data in food_arr:
                    percentage = Decimal(data[2]/total_amount)
                    Proposal_Milk_Food.objects.create(item=data[0], price=data[0].price,quantity=data[1], total=data[2],percent=percentage,proposal=pb)

                for data in vac_arr:
                    percentage = Decimal(data[2]/total_amount)
                    item_id = Medicine.objects.get(id=data[0].id)
                    item = Medicine_Inventory.objects.get(medicine=item_id)
                    Proposal_Vac_Prev.objects.create(item=item, price=data[0].price,quantity=data[1], total=data[2],percent=percentage,proposal=pb)
                
                for data in b_ny_med:
                    percentage = Decimal(data[2]/total_amount)
                    Proposal_Medicine.objects.create(item=data[0], price=data[0].medicine.price,quantity=data[1], total=data[2],percent=percentage,proposal=pb)

                for data in vet_arr:
                    percentage = Decimal(data[2]/total_amount)
                    Proposal_Vet_Supply.objects.create(item=data[0], price=data[0].price,quantity=data[1], total=data[2],percent=percentage,proposal=pb)

                for data in ken_arr:
                    percentage = Decimal(data[2]/total_amount)
                    Proposal_Kennel_Supply.objects.create(item=data[0], price=data[0].price,quantity=data[1], total=data[2],percent=percentage,proposal=pb)
                
                for data in other_arr:
                    percentage = Decimal(data[2]/total_amount)
                    Proposal_Others.objects.create(item=data[0], price=data[0].price,quantity=data[1], total=data[2],percent=percentage,proposal=pb)

                percentage = Decimal(training_total/total_amount)
                Proposal_Training.objects.create(quantity=train_k9, total=training_total,percent=percentage,proposal=pb)

                return redirect('planningandacquiring:budgeting_detail', pb.id)

            except:
                pb = Proposal_Budget.objects.create(k9_current=k9_ny,k9_needed=need_procure_ny,k9_breeded=born_ny,k9_total=procured_total,food_milk_total=total_food,vac_prev_total=vac_total,medicine_total=total_medicine,vet_supply_total=vet_total,kennel_total=ken_total,others_total=other_total,training_total=training_total,grand_total=total_amount,train_count=train_k9,date_created=dt.today(),year_budgeted=dt.today().year)

                #K9 Acquisition
                if formset.is_valid():
                    for form in formset:
                        if form.is_valid():
                            f=form.save(commit=False)
                            f.percent = Decimal(f.total/total_amount)
                            f.proposal=pb
                            f.save()

                for data in food_arr:
                    percentage = Decimal(data[2]/total_amount)
                    Proposal_Milk_Food.objects.create(item=data[0], price=data[0].price,quantity=data[1], total=data[2],percent=percentage,proposal=pb)

                for data in vac_arr:
                    percentage = Decimal(data[2]/total_amount)
                    item_id = Medicine.objects.get(id=data[0].id)
                    item = Medicine_Inventory.objects.get(medicine=item_id)
                    Proposal_Vac_Prev.objects.create(item=item, price=data[0].price,quantity=data[1], total=data[2],percent=percentage,proposal=pb)
                
                
                for data in b_ny_med:
                    percentage = Decimal(data[2]/total_amount)
                    Proposal_Medicine.objects.create(item=data[0], price=data[0].medicine.price,quantity=data[1], total=data[2],percent=percentage,proposal=pb)

                for data in vet_arr:
                    percentage = Decimal(data[2]/total_amount)
                    Proposal_Vet_Supply.objects.create(item=data[0], price=data[0].price,quantity=data[1], total=data[2],percent=percentage,proposal=pb)

                for data in ken_arr:
                    percentage = Decimal(data[2]/total_amount)
                    Proposal_Kennel_Supply.objects.create(item=data[0], price=data[0].price,quantity=data[1], total=data[2],percent=percentage,proposal=pb)
                
                for data in other_arr:
                    percentage = Decimal(data[2]/total_amount)
                    Proposal_Others.objects.create(item=data[0], price=data[0].price,quantity=data[1], total=data[2],percent=percentage,proposal=pb)

                percentage = Decimal(training_total/total_amount)
                Proposal_Training.objects.create(quantity=train_k9, total=training_total,percent=percentage,proposal=pb)
                
                return redirect('planningandacquiring:budgeting_detail', pb.id)
                    
        else:
            pass

    #LAST YEAR BUDGET
    this_year = next_year - 1
    try:
        abb = Actual_Budget.objects.get(year_budgeted__year=this_year)
    except:
        abb = None


    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'abb':abb,
        'formset':k9_formset(),
        'today':dt.today(),
        'generate':generate,
        'next_year':next_year,
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'k9_cy': k9_cy,
        'k9_ny': k9_ny,
        'born_ny': born_ny,
        'dead_list':dead_list,
        'total_k9': born_ny+k9_ny,
        'NDD_count':NDD_count,
        'EDD_count':EDD_count,
        'SAR_count':SAR_count,
        'NDD_demand':NDD_demand,
        'EDD_demand':EDD_demand,
        'SAR_demand':SAR_demand,
        'sar':sar,
        'ndd':ndd,
        'edd':edd,
    }
    return render (request, 'planningandacquiring/budgeting.html', context)

def load_budget(request):
    puppy_current = 0
    adult_current = 0
    total_milk_needed = 0
    total_puppy_food  = 0
    total_adult_food  = 0
    milk_quantity = 0
    milk_quantity_total = 0
    puppy_quantity = 0
    puppy_quantity_total = 0
    adult_quantity = 0
    adult_quantity_total = 0

    procured_total = round(Decimal(request.GET.get('p_amount')),2)
    need_procure_ny =  int(request.GET.get('p_count'))
    k9_ny =  int(request.GET.get('k9_ny'))
    born_ny =  int(request.GET.get('born_ny'))
    total_k9_next_year = need_procure_ny + k9_ny + born_ny
    all_k9 = K9.objects.exclude(status="Adopted").exclude(status="Dead").exclude(status="Stolen").exclude(status="Lost")
    
    k9_cy = all_k9.count()
    next_year = dt.now().year + 1
    current_year = dt.now().year

    #get k9 born next year
    k9_born_next_year = K9_Mated.objects.filter(status='Pregnant')
    born_ny = 0 #BORN K9 VARIABLE COUNT
    for data in k9_born_next_year:
        m = data.date_mated  + timedelta(days=63)
        if m.year == next_year:
            breed = Dog_Breed.objects.filter(breed=data.mother.breed).get(sex='Female')
            born_ny += int(breed.litter_number)

    #get k9 died next year
    dead_breed_ny = [] 
    for data in all_k9:
        b = Dog_Breed.objects.filter(breed = data.breed)[0]
        if (data.age + 1) >= b.life_span:
            dead_breed_ny.append(data.breed)

    kb_index = pd.Index(dead_breed_ny)

    b_values = kb_index.value_counts().keys().tolist() #k9 breed to be born
    b_counts = kb_index.value_counts().tolist() #number of k9 to be born by breed

    dead_k9_list = zip(b_values,b_counts) #DEAD BREED K9 LIST

    # GET NEEDED DOG FOOD
    puppy_current = all_k9.filter(age__lt=1).count()
    adult_current = all_k9.filter(age__gte=1).count()
    total_milk_need = (born_ny + puppy_current) * 21
    total_puppy_food  = (((born_ny + puppy_current) * 15) * 9) / 20
    total_adult_food  = (adult_current + need_procure_ny) * 12
   
    # print('NEEDED DOG FOOD',total_milk_needed,total_puppy_food,total_adult_food)

    #GET CURRENT DOG FOOD
    current_milk = Food.objects.filter(foodtype='Milk').aggregate(sum=Sum('quantity'))['sum']
    current_puppy_food = Food.objects.filter(foodtype='Puppy Dog Food').aggregate(sum=Sum('quantity'))['sum']
    current_adult_food = Food.objects.filter(foodtype='Adult Dog Food').aggregate(sum=Sum('quantity'))['sum']

    # print('CURRENT DOG FOOD',current_milk,current_puppy_food,current_adult_food)

    #GET DOG FOOD MOST USED QUANTITY
    #MILK
    milk_item = Food_Subtracted_Trail.objects.filter(inventory__foodtype='Milk').filter(date_subtracted__year=current_year).values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity')[0]

    m_item = None # milk item most used
    if milk_item:
        for key, value in milk_item.items(): 
            if key == 'inventory':
                m_item = value

        m_item = Food.objects.get(id=m_item)

    #PUPPY DOG FOOD
    puppy_item = Food_Subtracted_Trail.objects.filter(inventory__foodtype='Puppy Dog Food').filter(date_subtracted__year=current_year).values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity')[0]

    p_item = None # puppy food item most used
    if puppy_item:
        for key, value in puppy_item.items(): 
            if key == 'inventory':
                p_item = value
        p_item = Food.objects.get(id=p_item)

    #ADULT DOG FOOD
    adult_item = Food_Subtracted_Trail.objects.filter(inventory__foodtype='Adult Dog Food').filter(date_subtracted__year=current_year).values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity')[0]
    
    a_item = None # Adult food item most used
    if adult_item:
        for key, value in adult_item.items(): 
            if key == 'inventory':
                a_item = value
        a_item = Food.objects.get(id=a_item)
        
    food_arr = []

    if total_milk_needed>0:
        if m_item:  
            # CALCULATE PRICE AND TOTAL OF DOG FOOD
            # milk needed = total_milk_needed , current = current_milk 
            # needed - current * price
            milk_quantity = total_milk_needed - current_milk
            if milk_quantity < 0:
                milk_quantity = 0
            print('M ITEM',total_milk_needed,current_milk)
            milk_quantity_total = int(np.ceil(milk_quantity)) * m_item.price
            # print('MILK', m_item, milk_quantity, milk_quantity_total)
            if adult_quantity_total > 0:
                food_arr.append([m_item,milk_quantity,milk_quantity_total])

    if total_puppy_food>0:
        if p_item:
            #puppy food needed = total_puppy_food , current = current_puppy_food 
            puppy_quantity = total_puppy_food - current_puppy_food
            if puppy_quantity < 0:
                puppy_quantity = 0
            puppy_quantity_total = int(np.ceil(puppy_quantity)) * p_item.price
            # print('PUPPY FOOD', p_item, puppy_quantity, puppy_quantity_total)
            if puppy_quantity_total > 0:
                food_arr.append([p_item,int(puppy_quantity),puppy_quantity_total])

    if total_adult_food > 0:
        if a_item:
            #adult food needed = total_adult_food , current = current_adult_food 
            adult_quantity = total_adult_food - current_adult_food
            if adult_quantity < 0:
                adult_quantity = 0
            adult_quantity_total = int(np.ceil(adult_quantity)) * a_item.price
            # print('ADULT FOOD', a_item,adult_quantity, adult_quantity_total)
            if adult_quantity_total > 0:
                food_arr.append([a_item,int(adult_quantity),adult_quantity_total])

    mrt = Medicine_Received_Trail.objects.filter(expiration_date__year=next_year).filter(status='Pending').values('inventory').annotate(sum = Sum('quantity'))

    med_item_id = []
    med_item_q = []
    for m in mrt: 
        for key,value in m.items():
            if key == 'inventory':
                med_item_id.append(value)
            else:
                med_item_q.append(value)

    zip_a = zip(med_item_id, med_item_q)

    # Medicine that has expirations next year
    ny_med = []
    cy_med = [] 
    eny_ar_count = 0
    eny_bbb_count = 0
    eny_dw_count = 0
    eny_dcv_count = 0
    eny_dc4_count = 0
    eny_hw_count = 0
    eny_tf_count = 0
    
    for a,b in zip_a:  
        c = Medicine_Inventory.objects.get(id=a)
        x = [c, (c.quantity - b)]
        z = [c, c.quantity]
        ny_med.append(x)
        cy_med.append(z)

        if c.medicine.immunization == 'Anti-Rabies':
            eny_ar_count = eny_ar_count + b
        elif c.medicine.immunization == 'Bordetella Bronchiseptica Bacterin':
            eny_bbb_count = eny_bbb_count + b
        elif c.medicine.immunization == 'Deworming':
            eny_dw_count = eny_dw_count + b
        elif c.medicine.immunization == 'DHPPiL+CV':
            eny_dcv_count = eny_dcv_count + b
        elif c.medicine.immunization == 'DHPPiL4':
            eny_dc4_count = eny_dc4_count + b
        elif c.medicine.immunization == 'Heartworm':
            eny_hw_count = eny_hw_count + b
        elif c.medicine.immunization == 'Tick and Flea':
            eny_tf_count = eny_tf_count + b

    #get all medicine used in the current year exclude vaccine
    mst_cy = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).exclude(inventory__medicine__med_type='Vaccine').exclude(inventory__medicine__med_type='Preventive').values('inventory').distinct()
    mst_ny = []
    np_arr = np.array(ny_med)
    for mst in mst_cy:
        for key,value in mst.items():
            if key == 'inventory':
                c = Medicine_Inventory.objects.get(id=value)
                if c in np_arr:
                    for (n, (item1, item2)) in enumerate(ny_med):
                        if c == item1:
                            a = [c, item2, c.medicine.price]
                            mst_ny.append(a)
                else:
                    a = [c, c.quantity, c.medicine.price]
                    mst_ny.append(a)

    #med needed to procure next year and total
    b_ny_med = [] #buy next year medicine
    total_medicine = 0
    for (n, (item1, item2, item3)) in enumerate(mst_ny):
        ms = Medicine_Subtracted_Trail.objects.filter(inventory=item1).aggregate(sum=Sum('quantity'))['sum']
        r = ms / k9_cy
        r = r * (k9_ny+born_ny+need_procure_ny) - item2

        if np.ceil(r) > 0:
            s = Decimal(np.ceil(r)) * Decimal(item3)
            ss = round(s, 2)
            b = [item1,int(np.ceil(r)),ss]
            b_ny_med.append(b)
            total_medicine = total_medicine+ss
        
    print('MEDICINE', b_ny_med, total_medicine)

    vac_arr = []
    # CALCULATE Vaccine 
    # ANTI-RABIES Calculation
    ar_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='Anti-Rabies').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

    if ar_item == None:
        ar_item = Medicine_Received_Trail.objects.filter(date_received__year=current_year).filter(inventory__medicine__immunization='Anti-Rabies').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

    if ar_item == None:
        ar_item = Medicine.objects.filter(immunization='Anti-Rabies').last()

    if type(ar_item).__name__ == 'dict':
        for key, value in ar_item.items():
            if key == 'inventory':
                ar_item = value

        ar_item = Medicine_Inventory.objects.get(id=ar_item).medicine.id
        ar_item = Medicine.objects.get(id=ar_item) 

    ar_current = Medicine_Inventory.objects.filter(medicine__immunization='Anti-Rabies').aggregate(sum=Sum('quantity'))['sum']

    ar_quantity = (total_k9_next_year * 1) - ar_current
    if ar_quantity < 0:
        ar_quantity = 0
    ar_total = round(int(np.ceil(ar_quantity)) * ar_item.price,2)

    if ar_total>0:
        vac_arr.append([ar_item,ar_quantity,ar_total])

    # print(ar_item, ar_quantity, ar_total)

    #BORDERTELLA CALCULATION
    bbb_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='Bordetella Bronchiseptica Bacterin').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

    if bbb_item == None:
        bbb_item = Medicine_Received_Trail.objects.filter(date_received__year=current_year).filter(inventory__medicine__immunization='Bordetella Bronchiseptica Bacterin').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()
    
    if bbb_item == None:
        bbb_item = Medicine.objects.filter(immunization='Bordetella Bronchiseptica Bacterin').last()

    if type(bbb_item).__name__ == 'dict':
        for key, value in bbb_item.items():
            if key == 'inventory':
                bbb_item = value

        bbb_item = Medicine_Inventory.objects.get(id=bbb_item).medicine.id
        bbb_item = Medicine.objects.get(id=bbb_item)  


    bbb_current = Medicine_Inventory.objects.filter(medicine__immunization='Bordetella Bronchiseptica Bacterin').aggregate(sum=Sum('quantity'))['sum']

    mandatory_bbb1 = VaccinceRecord.objects.filter(bordetella_1=False).filter(k9__in=all_k9).count()
    mandatory_bbb2 = VaccinceRecord.objects.filter(bordetella_2=False).filter(k9__in=all_k9).count()

    bbb_quantity = (mandatory_bbb1 + mandatory_bbb2 + born_ny) - bbb_current
    if bbb_quantity < 0:
        bbb_quantity = 0
    bbb_total = round(int(np.ceil(bbb_quantity)) * bbb_item.price,2)
    print('BB',bbb_total)
    # print(bbb_item, bbb_quantity, bbb_total)

    if bbb_total > 0:
        vac_arr.append([bbb_item,bbb_quantity,bbb_total])

    print('BBB',bbb_item,bbb_quantity,bbb_total)
    #DHPPIL+CV CALCULATION
    dhcv_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='DHPPiL+CV').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()
  
    if dhcv_item == None:
        dhcv_item = Medicine_Received_Trail.objects.filter(date_received__year=current_year).filter(inventory__medicine__immunization='DHPPiL+CV').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

    if type(dhcv_item).__name__ == 'dict':
        for key, value in dhcv_item.items():
            if key == 'inventory':
                dhcv_item = value

        dhcv_item = Medicine_Inventory.objects.get(id=dhcv_item).medicine.id
        dhcv_item = Medicine.objects.get(id=dhcv_item) 

    if dhcv_item == None:
        dhcv_item = Medicine.objects.filter(immunization='DHPPiL+CV').last()

    dhcv_current = Medicine_Inventory.objects.filter(medicine__immunization='DHPPiL+CV').aggregate(sum=Sum('quantity'))['sum']

    mandatory_dhcv1 = VaccinceRecord.objects.filter(dhppil_cv_1=False).filter(k9__in=all_k9).count()
    mandatory_dhcv2 = VaccinceRecord.objects.filter(dhppil_cv_1=False).filter(k9__in=all_k9).count()
    mandatory_dhcv3 = VaccinceRecord.objects.filter(dhppil_cv_1=False).filter(k9__in=all_k9).count()

    dhcv_quantity = (mandatory_dhcv1 + mandatory_dhcv2 + mandatory_dhcv3 + born_ny) - dhcv_current
    if dhcv_quantity < 0:
        dhcv_quantity = 0
    dhcv_total = round(int(np.ceil(dhcv_quantity)) * dhcv_item.price,2)
    # print(dhcv_item, dhcv_quantity, dhcv_total)
    if dhcv_total>0:
        vac_arr.append([dhcv_item,dhcv_quantity,dhcv_total])

    #DHPPiL4 CALCULATION
    dh4_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='DHPPiL4').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

    if dh4_item == None:
        dh4_item = Medicine_Received_Trail.objects.filter(date_received__year=current_year).filter(inventory__medicine__immunization='DHPPiL4').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()
    
    if dh4_item == None:
        dh4_item = Medicine.objects.filter(immunization='DHPPiL4').last()

    if type(dh4_item).__name__ == 'dict':
        for key, value in dh4_item.items():
            if key == 'inventory':
                dh4_item = value

        dh4_item = Medicine_Inventory.objects.get(id=dh4_item).medicine.id
        dh4_item = Medicine.objects.get(id=dh4_item)

    dh4_current = Medicine_Inventory.objects.filter(medicine__immunization='DHPPiL4').aggregate(sum=Sum('quantity'))['sum']

    mandatory_dh41 = VaccinceRecord.objects.filter(dhppil4_1=False).filter(k9__in=all_k9).count()
    mandatory_dh42 = VaccinceRecord.objects.filter(dhppil4_2=False).filter(k9__in=all_k9).count()

    dh4_quantity = (mandatory_dh41 + mandatory_dh42 + born_ny) - dhcv_current
    if dh4_quantity < 0:
        dh4_quantity = 0
    dh4_total = round(int(np.ceil(dh4_quantity)) * dh4_item.price,2)
    # print(dh4_item, dh4_quantity, dh4_total)
    if dh4_total >0:
        vac_arr.append([dh4_item,dh4_quantity,dh4_total])

    #DEWORM CALCULATION
    dw_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='Deworming').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

    if dw_item == None:
        dw_item = Medicine_Received_Trail.objects.filter(date_received__year=current_year).filter(inventory__medicine__immunization='Deworming').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

    if type(dw_item).__name__ == 'dict':
        for key, value in dw_item.items():
            if key == 'inventory':
                dw_item = value

        dw_item = Medicine_Inventory.objects.get(id=dw_item).medicine.id
        dw_item = Medicine.objects.get(id=dw_item)
    
    if dw_item == None:
        dw_item = Medicine.objects.filter(immunization='Deworming').last()

    dw_current = Medicine_Inventory.objects.filter(medicine__immunization='Deworming').aggregate(sum=Sum('quantity'))['sum']

    mandatory_dw1 = VaccinceRecord.objects.filter(deworming_1=False).filter(k9__in=all_k9).count()
    mandatory_dw2 = VaccinceRecord.objects.filter(deworming_2=False).filter(k9__in=all_k9).count()
    mandatory_dw3 = VaccinceRecord.objects.filter(deworming_3=False).filter(k9__in=all_k9).count()
    mandatory_dw4 = VaccinceRecord.objects.filter(deworming_4=False).filter(k9__in=all_k9).count()
    yearly_dw = VaccinceRecord.objects.filter(Q(deworming_1=True)&Q(deworming_2=True)&Q(deworming_3=True)&Q(deworming_4=True)).filter(k9__in=all_k9).count() * 4

    dw_quantity = (mandatory_dw1 + mandatory_dw2 + mandatory_dw3 + mandatory_dw4) + yearly_dw + (born_ny *4) + (need_procure_ny * 4)- dw_current
    if dw_quantity < 0:
        dw_quantity = 0
    dw_total = round(int(np.ceil(dw_quantity)) * dw_item.price,2)
    # print(dw_item, dw_quantity, dw_total)
    if dw_total>0:
        vac_arr.append([dw_item,dw_quantity,dw_total])

    #HEARTWORM CALCULATION
    hw_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='Heartworm').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()
    
    if hw_item == None:
        hw_item = Medicine.objects.filter(immunization='Heartworm').last()
    
    if type(hw_item).__name__ == 'dict':
        for key, value in hw_item.items():
            if key == 'inventory':
                hw_item = value

        hw_item = Medicine_Inventory.objects.get(id=hw_item).medicine.id
        hw_item = Medicine.objects.get(id=hw_item)  


    hw_current = Medicine_Inventory.objects.filter(medicine__immunization='Heartworm').aggregate(sum=Sum('quantity'))['sum']

    mandatory_hw1 = VaccinceRecord.objects.filter(heartworm_1=False).filter(k9__in=all_k9).count()
    mandatory_hw2 = VaccinceRecord.objects.filter(heartworm_2=False).filter(k9__in=all_k9).count()
    mandatory_hw3 = VaccinceRecord.objects.filter(heartworm_3=False).filter(k9__in=all_k9).count()
    mandatory_hw4 = VaccinceRecord.objects.filter(heartworm_4=False).filter(k9__in=all_k9).count()
    mandatory_hw5 = VaccinceRecord.objects.filter(heartworm_5=False).filter(k9__in=all_k9).count()
    mandatory_hw6 = VaccinceRecord.objects.filter(heartworm_6=False).filter(k9__in=all_k9).count()
    mandatory_hw7 = VaccinceRecord.objects.filter(heartworm_7=False).filter(k9__in=all_k9).count()
    mandatory_hw8 = VaccinceRecord.objects.filter(heartworm_8=False).filter(k9__in=all_k9).count()
    yearly_hw = VaccinceRecord.objects.filter(Q(heartworm_1=True)&Q(heartworm_2=True)&Q(heartworm_3=True)&Q(heartworm_4=True)&Q(heartworm_5=True)&Q(heartworm_6=True)&Q(heartworm_7=True)&Q(heartworm_8=True)).filter(k9__in=all_k9).count() * 12

    hw_quantity = (mandatory_hw1 + mandatory_hw2 + mandatory_hw3 + mandatory_hw4 + mandatory_hw5 + mandatory_hw6 + mandatory_hw7 + mandatory_hw8) + yearly_hw + (born_ny *8) + (need_procure_ny * 12) - hw_current
    if hw_quantity < 0:
        hw_quantity = 0
    hw_total = round(int(np.ceil(hw_quantity)) * hw_item.price, 2)
    # print(hw_item, hw_quantity, hw_total)
    if hw_total>0:
        vac_arr.append([hw_item,hw_quantity,hw_total])

    #TICK AND FLEE CALCULATION
    tft_item = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='Tick and Flea').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()

    if tft_item == None:
        tft_item = Medicine_Received_Trail.objects.filter(date_received__year=current_year).filter(inventory__medicine__immunization='Tick and Flea').values('inventory').annotate(quantity=Sum('quantity')).order_by('-quantity').first()
    
    if tft_item == None:
        tft_item = Medicine.objects.filter(immunization='Tick and Flea').last()

    if type(tft_item).__name__ == 'dict':
        for key, value in tft_item.items(): 
            if key == 'inventory':
                tft_item = value

        tft_item = Medicine_Inventory.objects.get(id=tft_item).medicine.id
        tft_item = Medicine.objects.get(id=tft_item)

    tft_current = Medicine_Inventory.objects.filter(medicine__immunization='Tick and Flea').aggregate(sum=Sum('quantity'))['sum']

    mandatory_tft1 = VaccinceRecord.objects.filter(tick_flea_1=False).filter(k9__in=all_k9).count()
    mandatory_tft2 = VaccinceRecord.objects.filter(tick_flea_2=False).filter(k9__in=all_k9).count()
    mandatory_tft3 = VaccinceRecord.objects.filter(tick_flea_3=False).filter(k9__in=all_k9).count()
    mandatory_tft4 = VaccinceRecord.objects.filter(tick_flea_4=False).filter(k9__in=all_k9).count()
    mandatory_tft5 = VaccinceRecord.objects.filter(tick_flea_5=False).filter(k9__in=all_k9).count()
    mandatory_tft6 = VaccinceRecord.objects.filter(tick_flea_6=False).filter(k9__in=all_k9).count()
    mandatory_tft7 = VaccinceRecord.objects.filter(tick_flea_7=False).filter(k9__in=all_k9).count()
    
    yearly_tft = Medicine_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__medicine__immunization='Tick and Flea').aggregate(sum=Sum('quantity'))['sum']

    if yearly_tft == None:
        yearly_tft = 0

    m_tft = mandatory_tft1 + mandatory_tft2 + mandatory_tft3 + mandatory_tft4 + mandatory_tft5 + mandatory_tft6 + mandatory_tft7
    
    if yearly_tft < m_tft:
        tft_quantity = m_tft
    else:
        tft_quantity = yearly_tft

    if tft_quantity < 0:
        tft_quantity = 0
    tft_total = round(int(np.ceil(tft_quantity)) * tft_item.price, 2)
    # print("TFT", tft_item)
    if tft_total>0:
        vac_arr.append([tft_item,tft_quantity,tft_total])

    #MISCELLANOUS VET SUPPLY CALCULATION
    vet_item = Miscellaneous_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__misc_type='Vet Supply').values('inventory').annotate(quantity=Sum('quantity')).order_by('inventory')

    vet_arr = []
    vet_total = 0
    if vet_item != None:    
        vet_np_arr =np.array(vet_item)

        for data in vet_np_arr:
            for key, value in data.items(): 
                if key == 'inventory':
                    a = Miscellaneous.objects.get(id=value)
                else:
                    b = value
                    c = round(b * a.price,2)
            vet_arr.append([a,b,c])
            vet_total = vet_total + c

    # print('VET', vet_arr)

    #MISCELLANOUS KENNEL SUPPLY CALCULATION
    ken_item = Miscellaneous_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__misc_type='Kennel Supply').values('inventory').annotate(quantity=Sum('quantity')).order_by('inventory')

    ken_arr = []
    ken_total = 0
    if ken_item != None:    
        ken_np_arr =np.array(ken_item)

        for data in ken_np_arr:
            for key, value in data.items(): 
                if key == 'inventory':
                    a = Miscellaneous.objects.get(id=value)
                else:
                    b = value
                    c = round(b * a.price, 2)
            ken_arr.append([a,b,c])
            ken_total = ken_total + c
   
    # print('KENNEL', ken_arr)

    #MISCELLANOUS OTHERS CALCULATION
    other_item = Miscellaneous_Subtracted_Trail.objects.filter(date_subtracted__year=current_year).filter(inventory__misc_type='Others').values('inventory').annotate(quantity=Sum('quantity')).order_by('inventory')

    other_arr = []
    other_total = 0
    if other_item != None:    
        other_np_arr =np.array(other_item)

        for data in other_np_arr:
            for key, value in data.items(): 
                if key == 'inventory':
                    a = Miscellaneous.objects.get(id=value)
                else:
                    b = value
                    c = round(b * a.price, 2)
            other_arr.append([a,b,c])
            other_total = other_total + c

    # print('OTHERS', other_arr)

    # TRAINING CALCULATION
    train_k9 = (born_ny + need_procure_ny)
    training_total = round(Decimal(train_k9 * 18000), 2)
    # print('TRAINING AMOUNT', training_total)

    total_food = milk_quantity_total + puppy_quantity_total + adult_quantity_total
    vac_total = ar_total + bbb_total + dhcv_total + dh4_total + dw_total + hw_total + tft_total
    print('VAC',ar_total,bbb_total,dhcv_total,dh4_total,dw_total,hw_total,tft_total)
    if vac_total == 0:
        vac_total = None

    total_amount = procured_total+training_total+other_total+ken_total+vet_total+total_medicine+vac_total+total_food
    total_amount = round(total_amount,2)
    context = {
        'procured_total': procured_total,
        'food_arr':food_arr,
        'total_food': total_food,
        'b_ny_med': b_ny_med,
        'total_medicine': total_medicine,
        'vac_arr':vac_arr,
        'vac_total':vac_total,
        'vet_arr':vet_arr,
        'vet_total': vet_total,
        'ken_arr': ken_arr,
        'ken_total': ken_total,
        'other_arr':other_arr,
        'other_total': other_total,
        'train_k9':train_k9,
        'training_total': training_total,
        'total_amount': total_amount,
    }

    return render(request, 'planningandacquiring/budget_data.html', context)
