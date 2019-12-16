from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory, inlineformset_factory
from django.db.models import aggregates
from django.contrib import messages
from django.http import JsonResponse

from planningandacquiring.models import K9, K9_Parent, K9_Quantity, Dog_Breed
from profiles.models import User, Account, Personal_Info
from unitmanagement.models import Notification
from .models import K9_Genealogy, K9_Handler
from unitmanagement.models import Handler_K9_History
from training.models import Training, K9_Adopted_Owner, Training_Schedule
from .forms import TestForm, add_handler_form, assign_handler_form
from planningandacquiring.forms import add_donator_form
from training.forms import adoption_K9_form
from training.forms import TrainingUpdateForm, SerialNumberForm,ClassifySkillForm, RecordForm, DateForm
import datetime
from deployment.models import Team_Assignment, Daily_Refresher
from django.db.models import Sum
from decimal import Decimal
from django.db.models import Q

import itertools


from collections import OrderedDict

#graphing imports
import igraph
from igraph import *
import plotly.offline as opy
import plotly.graph_objs as go
import plotly.graph_objs.layout as lout

#print(pd.__version__) #Version retrieved is not correct
def notif(request):
    serial = request.session['session_serial']
    account = Account.objects.get(serial_number=serial)
    user_in_session = User.objects.get(id=account.UserID.id)
    
    if user_in_session.position == 'Veterinarian':
        notif = Notification.objects.filter(position='Veterinarian').order_by('-datetime')
    elif user_in_session.position == 'Handler':
        notif = Notification.objects.filter(position='Handler').order_by('-datetime')
    else:
        notif = Notification.objects.filter(position='Administrator').order_by('-datetime')
   
    return notif

def user_session(request):
    serial = request.session['session_serial']
    account = Account.objects.get(serial_number=serial)
    user_in_session = User.objects.get(id=account.UserID.id)
    return user_in_session

def index(request):
    return render (request, 'training/index.html')

#TODO :: SAVE FORM and FORMSET
def adoption_form(request):
    k9_formset = formset_factory(adoption_K9_form,can_delete=False)
    formset = k9_formset(request.POST, request.FILES)

    style = "ui green message"
    if request.method == "POST":
        fname = request.POST.get('fname')
        mname = request.POST.get('mname')
        lname = request.POST.get('lname')
        address = request.POST.get('address')

        if formset.is_valid():
            for form in formset:
                print(address)
                print(form.cleaned_data['k9'])
                k9_id=form.cleaned_data['k9']
                k9 = K9.objects.get(id=k9_id.id)
                file_adopt=form.cleaned_data['file_adopt']
                K9_Adopted_Owner.objects.create(k9=k9,first_name=fname,middle_name=mname,last_name=lname,address=address,date_adopted=datetime.datetime.now(),file_adopt=file_adopt)
                k9.training_status = "Adopted"
                k9.status = "Adopted"
                k9.save()
           
            messages.success(request, 'K9s has been adopted')
            return redirect('training:adoption_form')
   
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        # 'title': data,
        'style': style,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render (request, 'training/adoption_form.html', context) 
   
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title': "Adoption Form",
        'form': form,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render (request, 'training/adoption_form.html', context)

def confirm_adoption(request, id):
    # data = K9.objects.get(id=id) # get k9
    # no = 0#request.session['no_id']
    # new_owner = K9_Adopted_Owner.objects.get(id=no)
    # if request.method == "POST":
    #     if 'ok' in request.POST:
    #         print('ok')
    #         data.training_status = 'Adopted'
    #         data.save()
    #         return redirect('training:adoption_confirmed')
    #     else:
    #         print('not ok')
    #         new_owner.delete()
    #         return redirect('training:adoption_form', id = data.id)
    
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        # 'title': data,
        # 'data': data,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render (request, 'training/confirm_adoption.html', context)

def adoption_list(request):
    for_adoption = K9.objects.filter(training_status='For-Adoption')
    adopted = K9_Adopted_Owner.objects.filter(k9__training_status='Adopted').filter(date_returned=None)
    
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title': 'Adoption List',
        'for_adoption': for_adoption,
        'adopted': adopted,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }

    return render (request, 'training/for_adoption_list.html', context)

def adoption_details(request, id):
    data = K9_Adopted_Owner.objects.filter(id=id).last()
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title': data.k9,
        'data': data,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render (request, 'training/adoption_details.html', context)

def load_adoption(request):
    data = None
    try:
        id = request.GET.get('id')
        data = K9_Adopted_Owner.objects.filter(k9__id=id).latest('date_adopted')
    except:
        pass

    context = {
        'data': data,
    }

    return render(request, 'training/adoption_data.html', context)

def k9_returned(request, id):
    reason = request.POST.get('reason')
    k9 = K9.objects.get(id=id)
    k9.training_status='For-Adoption'

    owner = K9_Adopted_Owner.objects.filter(k9=k9).latest('date_adopted')
    owner.date_returned = datetime.datetime.now()
    owner.reason = reason
    
    owner.save()
    k9.save()

    style = "ui yellow message"
    messages.success(request, str(k9.name) + ' has been returned by ' + str(owner))
        
    return redirect('training:adoption_list')


def unified_graph():
    k9_set = K9.objects.all()

    breeds = []

    sar_count_male = []
    ndd_count_male = []
    edd_count_male = []

    sar_count_female = []
    ndd_count_female = []
    edd_count_female = []

    skills = ['SAR', 'NDD', 'EDD']

    for k9 in k9_set:
        breeds.append(k9.breed)

    breeds = list(set(breeds))

    loop = 0
    for breed in breeds:
        SAR = K9.objects.filter(sex='Male', breed=breed, capability="SAR").count()
        NDD = K9.objects.filter(sex='Male', breed=breed, capability="NDD").count()
        EDD = K9.objects.filter(sex='Male', breed=breed, capability="EDD").count()

        sar_count_male.append(SAR)
        ndd_count_male.append(NDD)
        edd_count_male.append(EDD)

        loop += 1

    for breed in breeds:
        SAR = K9.objects.filter(sex='Female', breed=breed, capability="SAR").count()
        NDD = K9.objects.filter(sex='Female', breed=breed, capability="NDD").count()
        EDD = K9.objects.filter(sex='Female', breed=breed, capability="EDD").count()

        sar_count_female.append(SAR)
        ndd_count_female.append(NDD)
        edd_count_female.append(EDD)
        loop += 1

    sar_breed = []
    ndd_breed = []
    edd_breed = []
    for breed in breeds:
        sar_breed.append("SAR - " + str(breed))
        ndd_breed.append("NDD - " + str(breed))
        edd_breed.append("EDD - " + str(breed))

    print("K9 COUNT")
    print(str(k9_set.count()))
    print("X")
    print(sar_breed)
    print(ndd_breed)
    print(edd_breed)
    print("MALE")
    print(sar_count_male)
    print(ndd_count_male)
    print(edd_count_male)
    print("FEMALE")
    print(sar_count_female)
    print(ndd_count_female)
    print(edd_count_female)


    ctr = 0
    # SAR
    # for breed in breeds:
    # Tig 3 per breed

    sar_male = go.Bar(
        x=sar_breed,
        y=sar_count_male,
        name='Male'
    )
    ctr += 1
    sar_female = go.Bar(
        x=sar_breed,
        y=sar_count_female,
        name='Female'
    )
    ctr += 1

    # NDD
    # for breed in breeds:
    # Tig 3 per breed
    ndd_male = go.Bar(
        x=ndd_breed,
        y=ndd_count_male,
        name='Male'
    )
    ctr += 1
    ndd_female = go.Bar(
        x=ndd_breed,
        y=ndd_count_female,
        name='Female'
    )
    ctr += 1

    # EDD
    # for breed in breeds:
    # Tig 3 per breed
    edd_male = go.Bar(
        x=edd_breed,
        y=edd_count_male,
        name='Male'
    )
    ctr += 1
    edd_female = go.Bar(
        x=edd_breed,
        y=edd_count_female,
        name='Female'
    )
    ctr += 1

    data = [sar_male, sar_female, ndd_male, ndd_female, edd_male, edd_female]

    layout = go.Layout(
        title="K9 Count by Skill, Breed and Gender",
        barmode='stack'
    )

    fig = go.Figure(data=data, layout=layout)
    graph = opy.plot(fig, auto_open=False, output_type='div')

    return graph

def classify_k9_list(request):

    k9s_for_grading = []
    train_sched = Training_Schedule.objects.exclude(date_start = None).exclude(date_end = None)

    for item in train_sched:
        if item.k9.training_level == item.stage:
            k9s_for_grading.append(item.k9.id)

    # print(k9s_for_grading)

    data_unclassified = K9.objects.filter(training_status="Unclassified").filter(status="Material Dog")
    data_classified = K9.objects.filter(training_status="Classified").filter(status="Material Dog").filter(handler = None)
    data_ontraining = K9.objects.filter(training_status="On-Training").filter(status="Material Dog").filter(pk__in = k9s_for_grading)
    data_trained = K9.objects.filter(training_status="Trained").filter(status="Material Dog")

    NDD_count = K9.objects.filter(capability='NDD').count()
    EDD_count = K9.objects.filter(capability='EDD').count()
    SAR_count = K9.objects.filter(capability='SAR').count()

    NDD_demand = list(Team_Assignment.objects.aggregate(Sum('NDD_demand')).values())[0]
    EDD_demand = list(Team_Assignment.objects.aggregate(Sum('EDD_demand')).values())[0]
    SAR_demand = list(Team_Assignment.objects.aggregate(Sum('SAR_demand')).values())[0]

    if not NDD_demand:
        NDD_demand = 0
    if not EDD_demand:
        EDD_demand = 0
    if not SAR_demand:
        SAR_demand = 0

    type_text = request.GET.get('type')

    if type_text == None:
        type_text = 'unclassified'

    style = 'ui blue message'

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title': 'K9 Classification',
        'type_text': type_text,
        'data_unclassified': data_unclassified,
        'data_classified': data_classified,
        'data_ontraining': data_ontraining,
        'data_trained': data_trained,
        'EDD_count': EDD_count,
        'NDD_count': NDD_count,
        'SAR_count': SAR_count,
        'NDD_demand': NDD_demand,
        'EDD_demand': EDD_demand,
        'SAR_demand': SAR_demand,
        'notif_data':notif_data,
        'count':count,
        'user':user,
        'style':style,
    }
    return render (request, 'training/classify_k9_list.html', context)

def assign_k9_duty(request, id=None):
    active4 = ' active'
    if request.method == 'POST':
        data = K9.objects.get(id=id) # get k9
        height = request.POST.get('height')
        weight = request.POST.get('weight')

        if 'deploy' in request.POST:
            data.training_status = 'For-Deployment'

        else:
            data.training_status = 'For-Breeding'

        data.height =height
        data.weight = weight
        data.serial_number ='SN-' + str(data.id) +'-'+str(datetime.datetime.now().year)
        data.status = 'Working Dog'
        data.save()

        style = "ui green message"
        messages.success(request, data.name + ' has been assigned ' + data.training_status)
        messages.info(request, 'Trained')
        return redirect('unitmanagement:trained_list')

def view_graphs(request, id):
    k9_id = request.session['k9_id']

    method_arrays = []

    skill_count_between_breeds_desc = ""
    skill_percentage_between_sexes_desc = ""
    skill_count_ratio_desc = ""
    skills_from_gender_desc = ""
    skills_in_general = ""

    method_arrays.append(skill_count_between_breeds(k9_id))
    #method_arrays.append(skill_percentage_between_sexes(k9_id))
    #method_arrays.append(skill_count_ratio())

    tree = genealogy(k9_id)
    genes = K9_Genealogy.objects.filter(zero=k9_id)
    if genes:
        #method_arrays.append(skills_from_gender(k9_id))
        method_arrays.append(skill_in_general(k9_id))

    SAR_graph = []
    NDD_graph = []
    EDD_graph = []

    sar_description = []
    ndd_description = []
    edd_description = []

    ctr = 0
    for array in method_arrays:
        #Check if atleast one of the data has a score
        if method_arrays[ctr][1] == 1 or method_arrays[ctr][2] == 1 or method_arrays[ctr][3] == 1:
            #Save graph to the corresponding skill array
            if method_arrays[ctr][1] == 1:
                SAR_graph.append(method_arrays[ctr][0])
                str = "SAR is recommended because "
                sar_description.append(str + method_arrays[ctr][4])
            if method_arrays[ctr][2] == 1:
                NDD_graph.append(method_arrays[ctr][0])
                str = "NDD is recommended because "
                ndd_description.append(str + method_arrays[ctr][4])
            if method_arrays[ctr][3] == 1:
                EDD_graph.append(method_arrays[ctr][0])
                str = "EDD is recommended because "
                edd_description.append(str + method_arrays[ctr][4])

        ctr += 1

    #Check if skills are supported data, otherwise all of them are recommended
    graphs = ""
    descriptions = ""
    title = ""
    if SAR_graph or NDD_graph or EDD_graph:
        if id == 0:
            if SAR_graph:
                graphs = SAR_graph
                descriptions = sar_description
            else:
                graphs = ["There is no available data to support this skill!"]
            title = "Search and Rescue"
        elif id == 1:
            if NDD_graph:
                graphs = NDD_graph
                descriptions = ndd_description
            else:
                graphs = ["There is no available data to support this skill!"]
            title = "Narcotics Detection Dogs"
        elif id == 2:
            if EDD_graph:
                graphs = EDD_graph
                descriptions = edd_description
            else:
                graphs = ["There is no available data to support this skill!"]
            title = "Explosives Detection Dogs"
    elif not SAR_graph and not NDD_graph and not EDD_graph:
        graphs = ["All skills have no supporting data, pick any of the skills provided"]
        if id == 0:
            title = "Search and Rescue"
        elif id == 1:
            title = "Narcotics Detection Dogs"
        elif id == 2:
            title = "Explosives Detection Dogs"

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {'graphs': graphs,
               'descriptions': descriptions,
               'title': title,
               'notif_data':notif_data,
                'count':count,
                'user':user,
               }

    return render(request, 'training/view_graph.html', context)

def Average(lst):
    average = sum(lst) / len(lst)
    average = round(average, 1)
    return average

#TODO Restrict Viable dogs to be trained for those who are 6 months old
def classify_k9_select(request, id):
    form = ClassifySkillForm(request.POST)
    request.session['k9_id'] = id
    data = K9.objects.get(id=id)
    title = data.name
    style = ""

    #TODO change this
    NDD_count = K9.objects.filter(capability='NDD').count()
    EDD_count = K9.objects.filter(capability='EDD').count()
    SAR_count = K9.objects.filter(capability='SAR').count()
    
    NDD_demand = list(Team_Assignment.objects.aggregate(Sum('NDD_demand')).values())[0]
    EDD_demand = list(Team_Assignment.objects.aggregate(Sum('EDD_demand')).values())[0]
    SAR_demand = list(Team_Assignment.objects.aggregate(Sum('SAR_demand')).values())[0]

    if not NDD_demand:
        NDD_demand = 0
    if not EDD_demand:
        EDD_demand = 0
    if not SAR_demand:
        SAR_demand = 0

    NDD_deployed = list(Team_Assignment.objects.aggregate(Sum('NDD_deployed')).values())[0]
    EDD_deployed = list(Team_Assignment.objects.aggregate(Sum('EDD_deployed')).values())[0]
    SAR_deployed = list(Team_Assignment.objects.aggregate(Sum('SAR_deployed')).values())[0]
    
    if not NDD_deployed:
        NDD_deployed = 0
    if not EDD_deployed:
        EDD_deployed = 0
    if not SAR_deployed:
        SAR_deployed = 0

    NDD_assigned = K9.objects.filter(capability='NDD').exclude(assignment='None').count()
    EDD_assigned = K9.objects.filter(capability='EDD').exclude(assignment='None').count()
    SAR_assigned = K9.objects.filter(capability='SAR').exclude(assignment='None').count()

    try:
        NDD_difference = NDD_demand - NDD_deployed
    except:
        NDD_difference = 0

    try:
        EDD_difference = EDD_demand - EDD_deployed
    except:
        EDD_difference = 0

    try:
        SAR_difference = SAR_demand - SAR_deployed
    except:
        SAR_difference = 0


    # {{skill}} K9s assigned / {{skill}} K9s
    # {{assigned}}/{{demand-deployed}}
    # Total {{skill}} K9s Required: {{demand}} >>Note might not mean much if K9s on hand is insufficient, might stick with total count | BUT, demand/deployed usually dictates the priority
    # Total {{skil}} K9s Deployed: {{deployed}}

    trait_score = [0, 0, 0]
    dog_trait = Dog_Breed.objects.all()

    select_trait = None
    for trait in dog_trait:
        if trait.breed == data.breed:
            select_trait = trait

    if select_trait is not None:
        if select_trait.skill_recommendation == "SAR" or select_trait.skill_recommendation2 == "SAR" or select_trait.skill_recommendation3 == "SAR":
            trait_score[0] = 1
        if select_trait.skill_recommendation == "NDD" or select_trait.skill_recommendation2 == "NDD" or select_trait.skill_recommendation2 == "EDD":
            trait_score[1] = 1
        if select_trait.skill_recommendation == "EDD" or select_trait.skill_recommendation2 == "EDD" or select_trait.skill_recommendation3 == "EDD":
            trait_score[2] = 1

    method_arrays = []

    BREED = (
        ('Belgian Malinois', 'Belgian Malinois'),
        ('Dutch Sheperd', 'Dutch Sheperd'),
        ('German Sheperd', 'German Sheperd'),
        ('Golden Retriever', 'Golden Retriever'),
        ('Jack Russel', 'Jack Russel'),
        ('Labrador Retriever', 'Labrador Retriever'),
        ('Mixed', 'Mixed'),
    )


    records = Training.objects.exclude(grade = "No Grade Yet").exclude(grade = None).filter(k9__breed__contains = data.breed).filter(stage = "Finished Training")


    SAR_list = []
    NDD_list = []
    EDD_list = []

    for record in records:
        if record.training == "SAR":
            try:
                SAR_list.append(Decimal(record.grade))
            except:
                SAR_list.append(Decimal(0))
        if record.training == "NDD":
            try:
                NDD_list.append(Decimal(record.grade))
            except:
                NDD_list.append(Decimal(0))
        if record.training == "EDD":
            try:
                EDD_list.append(Decimal(record.grade))
            except:
                EDD_list.append(Decimal(0))

    if not SAR_list:
        SAR_list.append(Decimal(0))
    if not NDD_list:
        NDD_list.append(Decimal(0))
    if not EDD_list:
        EDD_list.append(Decimal(0))

    skill_ave_sar = Average(SAR_list)
    skill_ave_ndd = Average(NDD_list)
    skill_ave_edd = Average(EDD_list)

    print("TRAINING LIST")
    print(skill_ave_sar)
    print(skill_ave_ndd)
    print(skill_ave_edd)

    ave_list = []
    ave_list.append(skill_ave_sar)
    ave_list.append(skill_ave_ndd)
    ave_list.append(skill_ave_edd)

    max_ave = max(ave_list)


    #skill_demand() TODO Add demand score
    method_arrays.append(skill_count_between_breeds(id))
    #method_arrays.append(skill_percentage_between_sexes(id))
    #method_arrays.append(skill_count_ratio())

    tree = genealogy(id)
    genes = K9_Genealogy.objects.filter(zero = id)
    if genes:
        #method_arrays.append(skills_from_gender(id))
        method_arrays.append(skill_in_general(id))

    breed_score = []
    #gene_score = []
    ave_score = [0, 0, 0]


    SAR_score = 0
    NDD_score = 0
    EDD_score = 0

    if trait_score[0] == 1:
        SAR_score += 1
    if trait_score[1] == 1:
        NDD_score += 1
    if trait_score[2] == 1:
        EDD_score += 1

    if max_ave == skill_ave_sar and max_ave != 0:
        SAR_score += 1
        ave_score[0] = 1
    if max_ave == skill_ave_ndd and max_ave != 0:
        NDD_score += 1
        ave_score[1] = 1
    if max_ave == skill_ave_edd and max_ave != 0:
        EDD_score += 1
        ave_score[2] = 1

    print("AVE SCORE")
    print(ave_score)

    skill_breed_sar = method_arrays[0][1]
    skill_breed_ndd = method_arrays[0][2]
    skill_breed_edd = method_arrays[0][3]
    SAR_score += skill_breed_sar
    NDD_score += skill_breed_ndd
    EDD_score += skill_breed_edd
    breed_score.append(skill_breed_sar)
    breed_score.append(skill_breed_ndd)
    breed_score.append(skill_breed_edd)


    skill_gene_sar = 0
    skill_gene_ndd = 0
    skill_gene_edd = 0

    gene_score = [0, 0, 0]

    #Run this if k9 has ancestors
    if len(method_arrays) == 2:
        skill_gene_sar = method_arrays[1][1]
        skill_gene_ndd = method_arrays[1][2]
        skill_gene_edd = method_arrays[1][3]
        SAR_score += skill_gene_sar
        NDD_score += skill_gene_ndd
        EDD_score += skill_breed_edd
        gene_score[0] = skill_gene_sar
        gene_score[1] = skill_gene_ndd
        gene_score[2] = skill_gene_edd


    #Save skills scores from methods then add all scores
    # ctr = 0
    # for array in method_arrays:
    #     SAR_score += method_arrays[ctr][1]
    #     NDD_score += method_arrays[ctr][2]
    #     EDD_score += method_arrays[ctr][3]
    #
    #     ctr += 1
    #
    #
    # print("SAR SCORE")
    # print(SAR_score)
    # print("NDD SCORE")
    # print(NDD_score)
    # print("EDD SCORE")
    # print(EDD_score)

    #Save all aggregated skill scores in one array
    compact_score = []
    compact_score.append(SAR_score)
    compact_score.append(NDD_score)
    compact_score.append(EDD_score)

    print("COMPACT SCORE")
    print(compact_score)

    recommended = [0, 0, 0]

    #Check which one has the highest score (regardless if all scores are 0)
    ctr = 0
    for x in compact_score:
        if x == max(compact_score):
            recommended[ctr] = 1
        ctr += 1

    #Mark as recommended those skills that are equal to the highest score
    max_score = max(recommended)
    recommended.append(max_score)
    print("RECOMMENDED")
    print(recommended)

    sar_recommended = ""
    ndd_recommended = ""
    edd_recommended = ""

    if recommended[0] == 1:
        sar_recommended = "Recommended!"
    if recommended[1] == 1:
        ndd_recommended = "Recommended!"
    if recommended[2] == 1:
        edd_recommended = "Recommended!"

    try:
        edd = Training.objects.filter(k9=data).get(training='EDD')
    except:
        edd = None
    
    try:
        ndd = Training.objects.filter(k9=data).get(training='NDD')
    except:
        ndd = None

    try:
        sar = Training.objects.filter(k9=data).get(training='SAR')
    except:
        sar = None

    # TODO:
	#if already has capability and on training from other records,
	#previous record training will result to grade 0

    #graph = unified_graph()

    # NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)

    if request.method == 'POST':
        print(data.capability)

        if data.capability == 'EDD':
            edd.grade = '0'
            edd.save()
        elif data.capability == 'NDD':
            ndd.grade = '0'
            ndd.save()
        elif data.capability == 'SAR':
            sar.grade = '0'
            sar.save()
        else:
            pass

        if data.training_status == 'On-Training':
            ...
        else:
            data.training_status = "Classified"

        data.training_count = data.training_count+1 
        data.capability = request.POST.get('radio')
        data.save()

        style = "ui green message"
        messages.success(request, 'K9 has been successfully Classified!')
        return HttpResponseRedirect('../list-classify-k9?type=unclassified')

    try:
        parent = K9_Parent.objects.get(offspring=data)
    except K9_Parent.DoesNotExist:

        #NOTIF SHOW
        notif_data = notif(request)
        count = notif_data.filter(viewed=False).count()
        user = user_session(request)
        context = {
            'data': data,
            'title': title,
            'style': style,
            'recommended': recommended,
            'tree': tree,
            'genes': genes,
            'edd': edd,
            'ndd': ndd,
            'sar': sar,
            'sar_recommended': sar_recommended,
            'ndd_recommended': ndd_recommended,
            'edd_recommended': edd_recommended,
            'form': form,
            # 'graph': graph,


            'skill_breed_sar': skill_breed_sar,
            'skill_breed_ndd': skill_breed_ndd,
            'skill_breed_edd': skill_breed_edd,
            'skill_gene_sar': skill_gene_sar,
            'skill_gene_ndd': skill_gene_ndd,
            'skill_gene_edd': skill_gene_edd,
            'skill_ave_sar': skill_ave_sar,
            'skill_ave_ndd': skill_ave_ndd,
            'skill_ave_edd': skill_ave_edd,

            'compact_score': compact_score,
            'SAR_score': SAR_score,
            'NDD_score': NDD_score,
            'EDD_score': EDD_score,

            'breed_score': breed_score,
            'gene_score': gene_score,
            'ave_score': ave_score,
            'select_trait': select_trait,
            'trait_score': trait_score,

            'notif_data':notif_data,
            'count':count,
            'user':user,

            'EDD_count': EDD_count,
            'NDD_count': NDD_count,
            'SAR_count': SAR_count,

            'NDD_demand': NDD_demand,
            'EDD_demand': EDD_demand,
            'SAR_demand': SAR_demand,
            'NDD_deployed': NDD_deployed,
            'EDD_deployed': EDD_deployed,
            'SAR_deployed': SAR_deployed,
            'NDD_assigned': NDD_assigned,
            'EDD_assigned': EDD_assigned,
            'SAR_assigned' : SAR_assigned,

            'NDD_difference': NDD_difference,
            'EDD_difference': EDD_difference,
            'SAR_difference': SAR_difference,

        }
    else:
        parent_exist = 1
        context = {
            'data': data,
            'parent': parent,
            'parent_exist': parent_exist,
            'title': title,
            'style': style,
            'recommended': recommended,
            'tree': tree,
            'genes' : genes,
            'edd': edd,
            'ndd': ndd,
            'sar': sar,
            'sar_recommended': sar_recommended,
            'ndd_recommended': ndd_recommended,
            'edd_recommended': edd_recommended,
            'form': form,
            # 'graph': graph,


            'skill_breed_sar': skill_breed_sar,
            'skill_breed_ndd': skill_breed_ndd,
            'skill_breed_edd': skill_breed_edd,
            'skill_gene_sar': skill_gene_sar,
            'skill_gene_ndd': skill_gene_ndd,
            'skill_gene_edd': skill_gene_edd,
            'skill_ave_sar': skill_ave_sar,
            'skill_ave_ndd': skill_ave_ndd,
            'skill_ave_edd': skill_ave_edd,

            'compact_score': compact_score,
            'SAR_score': SAR_score,
            'NDD_score': NDD_score,
            'EDD_score': EDD_score,

            'breed_score': breed_score,
            'gene_score': gene_score,
            'ave_score': ave_score,
            'select_trait': select_trait,
            'trait_score': trait_score,

            'notif_data':notif_data,
            'count':count,
            'user':user,

            'EDD_count': EDD_count,
            'NDD_count': NDD_count,
            'SAR_count': SAR_count,

            'NDD_demand': NDD_demand,
            'EDD_demand': EDD_demand,
            'SAR_demand': SAR_demand,
            'NDD_deployed': NDD_deployed,
            'EDD_deployed': EDD_deployed,
            'SAR_deployed': SAR_deployed,
            'NDD_assigned': NDD_assigned,
            'EDD_assigned': EDD_assigned,
            'SAR_assigned': SAR_assigned,

            'NDD_difference' : NDD_difference ,
            'EDD_difference' :  EDD_difference,
            'SAR_difference' : SAR_difference,

        }

    return render (request, 'training/classify_k9_select.html', context)

# TODO 
def assign_k9_select(request, id):
    form = assign_handler_form(request.POST or None)
    style = ""
    k9 = K9.objects.get(id=id)  

    handler = User.objects.filter(status='Working').filter(position='Handler').filter(partnered=False)
    g = []
    for h in handler:
        c = Handler_K9_History.objects.filter(handler=h).filter(k9__capability=k9.capability).count()
        g.append(c)

    if request.method == 'POST':
        print(form.errors)
        if form.is_valid():
            f = form.save(commit=False)
            f.k9 = k9
            f.save()
            
            #K9 Update
            k9.training_status = 'On-Training'
            k9.handler = f.handler
            k9.save()


            #Create K9_Handler Model
            K9_Handler.objects.create(k9 = k9, handler = f.handler)

            #Handler Update
            h = User.objects.get(id= f.handler.id)
            h.partnered = True
            h.save()

            messages.success(request, str(k9) + ' has been assigned to ' + str(h) + ' and is ready for Training!')
            messages.info(request, 'On-Training')
            return redirect('training:classify_k9_list')


        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    
    context = {
        'Title': "K9 Assignment for " + k9.name,
        'form': form,
        'style': style,
        'notif_data':notif_data,
        # 'type_text':type_text,
        'count':count,
        'user':user,
        'k9':k9,
        'g':g,
    }
    return render (request, 'training/assign_k9_select.html', context)

#Trained Dog - Assign serial number Form
def serial_number_form(request, id):
    form = SerialNumberForm(request.POST or None)
    style = "ui teal message"
    data = K9.objects.get(id=id) # get k9

    if request.method == 'POST':
        print(form.errors)
        if form.is_valid():
            data.serial_number ='SN-' + str(data.id) +'-'+str(datetime.datetime.now().year)
            #data.microchip = request.POST.get('microchip')
            training_status = request.POST.get('dog_type')
            data.training_status = training_status
            data.save()

            if training_status == "For-Breeding":
                user = User.objects.get(id = data.handler.id)
                user.partnered = 0
                user.save()
                data.handler = None
                data.save()
                try:
                    k9_handler = K9_Handler.objects.get(k9=data)
                    k9_handler.delete()
                except:
                    k9_handler = None


            style = "ui green message"
            messages.success(request, 'K9 has been finalized!')

        else:
            style = "ui red message"
            messages.warning(request, 'Invalid input data!')

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'form': form,
        'title': 'Trained K9 Finalization',
        'texthelp': 'Input Final Details Here',
        'actiontype': 'Submit',
        'style' : style,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render (request, 'training/serial_number_form.html', context)
    
def training_records(request):
    data = K9.objects.all()
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title': "Training Records",
        'data': data,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render(request, 'training/training_records.html', context)


def training_update_form(request, id):
    data = K9.objects.get(id=id)  # get k9
    handler = User.objects.get(id=data.handler.id)  
    training = Training.objects.filter(k9=data).get(training=data.capability)  #get training record
    form = TrainingUpdateForm(request.POST or None, instance=training)
    handlerID = K9_Handler.objects.filter(k9=data)
    #form2 = RecordForm(request.POST or None)
    average = 0
    print(training.stage)
    print(data.training_level)
    stage = ""
    style = "ui blue message"
    # CHANGED stage = Failed
    if request.method == 'POST':
        if data.training_status == 'On-Training':
            remarks = request.POST.get('remarks')
            if training.stage == "Stage 0":
                stage1_1 = request.POST.get('stage1_1')
                if stage1_1 == '0':
                    data.training_status = "For-Adoption"
                    data.trained = "Failed"
                    data.handler = None
                    data.save()

                    handler.partnered = False
                    handler.save()

                    training.stage = "Stage 0 - Failed"
                    training.save()

                    style = "ui red message"
                    messages.warning(request, str(data) + " has failed a stage and is now up for adoption.")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
                else:
                    average = (Decimal(average) + Decimal(stage1_1))
                    stage = "Stage 1.1"
                    # print(stage1_1)

                    # print(average)
                    training.stage = stage
                    training.stage1_1 = stage1_1
                    data.training_level = stage
                    data.save()
                    training.save()

                    train_sched = Training_Schedule.objects.create(k9 = data, stage = stage, remarks = remarks)
                    style = "ui green message"
                    messages.success(request, str(data) + " has been graded!")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
            elif training.stage == "Stage 1.1":
                stage1_2 = request.POST.get('stage1_2')
                # print("STAGE 1")
                # print(stage1_2)
                if stage1_2 == '0':
                    data.training_status = "For-Adoption"
                    data.trained = "Failed"
                    data.handler = None
                    data.save()

                    handler.partnered = False
                    handler.save()


                    training.stage = "Stage 1.1 - Failed"
                    training.save()

                    style = "ui red message"
                    messages.warning(request, str(data) + " has failed a stage and is now up for adoption.")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
                else:
                    average = (Decimal(average) + Decimal(stage1_2))
                    stage = "Stage 1.2"
                    # print(stage1_2)
                    # print(average)
                    training.stage = stage
                    training.stage1_2 = stage1_2
                    data.training_level = stage
                    data.save()
                    training.save()

                    train_sched = Training_Schedule.objects.create(k9=data, stage=stage, remarks = remarks)
                    style = "ui green message"
                    messages.success(request, str(data) + " has been graded!")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
            elif training.stage == "Stage 1.2":
                stage1_3 = request.POST.get('stage1_3')
                if stage1_3 == '0':
                    data.training_status = "For-Adoption"
                    data.trained = "Failed"
                    data.handler = None
                    data.save()

                    handler.partnered = False
                    handler.save()


                    training.stage = "Stage 1.2 - Failed"
                    training.save()

                    style = "ui red message"
                    messages.warning(request, str(data) + " has failed a stage and is now up for adoption.")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
                else:
                    average = (Decimal(average) + Decimal(stage1_3))
                    stage = "Stage 1.3"
                    training.stage = stage
                    training.stage1_3 = stage1_3
                    data.training_level = stage
                    # print(stage1_3)
                    # print(average)
                    data.save()
                    training.save()

                    train_sched = Training_Schedule.objects.create(k9=data, stage=stage, remarks = remarks)
                    style = "ui green message"
                    messages.success(request, str(data) + " has been graded!")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
            elif training.stage == "Stage 1.3":
                stage2_1 = request.POST.get('stage2_1')
                if stage2_1 == '0':
                    data.training_status = "For-Adoption"
                    data.trained = "Failed"
                    data.handler = None
                    data.save()

                    handler.partnered = False
                    handler.save()


                    training.stage = "Stage 1.3 - Failed"
                    training.save()

                    style = "ui red message"
                    messages.warning(request, str(data) + " has failed a stage and is now up for adoption.")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
                else:
                    average = Decimal(average) + Decimal(stage2_1)
                    stage = "Stage 2.1"
                    training.stage = stage
                    training.stage2_1 = stage2_1
                    data.training_level = stage
                    
                    data.save()
                    training.save()

                    train_sched = Training_Schedule.objects.create(k9=data, stage=stage, remarks = remarks)
                    style = "ui green message"
                    messages.success(request, str(data) + " has been graded!")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
            elif training.stage == "Stage 2.1":
                stage2_2 = request.POST.get('stage2_2')
                if stage2_2 == '0':
                    data.training_status = "For-Adoption"
                    data.trained = "Failed"
                    data.handler = None
                    data.save()

                    handler.partnered = False
                    handler.save()


                    training.stage = "Stage 2.1 - Failed"
                    training.save()

                    style = "ui red message"
                    messages.warning(request, str(data) + " has failed a stage and is now up for adoption.")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
                else:
                    average = Decimal(average) + Decimal(stage2_2)
                    stage = "Stage 2.2"
                    training.stage = stage
                    training.stage2_2 = stage2_2
                    data.training_level = stage
                    
                    data.save()
                    training.save()

                    train_sched = Training_Schedule.objects.create(k9=data, stage=stage, remarks = remarks)
                    style = "ui green message"
                    messages.success(request, str(data) + " has been graded!")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
            elif training.stage == "Stage 2.2":
                stage2_3 = request.POST.get('stage2_3')
                if stage2_3 == '0':
                    data.training_status = "For-Adoption"
                    data.trained = "Failed"
                    data.handler = None
                    data.save()

                    handler.partnered = False
                    handler.save()


                    training.stage = "Stage 2.2 - Failed"
                    training.save()

                    style = "ui red message"
                    messages.warning(request, str(data) + " has failed a stage and is now up for adoption.")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
                else:
                    average = Decimal(average) + Decimal(stage2_3)
                    stage = "Stage 2.3"
                    training.stage = stage
                    training.stage2_3 = stage2_3
                    data.training_level = stage
                    
                    data.save()
                    training.save()

                    train_sched = Training_Schedule.objects.create(k9=data, stage=stage, remarks = remarks)
                    messages.success(request, str(data) + " has been graded!")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
            elif training.stage == "Stage 2.3":
                stage3_1 = request.POST.get('stage3_1')
                if stage3_1 == '0':
                    data.training_status = "For-Adoption"
                    data.trained = "Failed"
                    data.handler = None
                    data.save()

                    handler.partnered = False
                    handler.save()


                    training.stage = "Stage 2.3 - Failed"
                    training.save()

                    style = "ui red message"
                    messages.success(request, str(data) + " has failed a stage and is now up for adoption.")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
                else:
                    average = Decimal(average) + Decimal(stage3_1)
                    stage = "Stage 3.1"
                    training.stage = stage
                    training.stage3_1 = stage3_1
                    data.training_level = stage
                
                    data.save()
                    training.save()

                    train_sched = Training_Schedule.objects.create(k9=data, stage=stage, remarks = remarks)
                    style = "ui green message"
                    messages.success(request, str(data) + " has been graded!")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
            elif training.stage == "Stage 3.1":
                stage3_2 = request.POST.get('stage3_2')
                if stage3_2 == "0":
                    data.training_status = "For-Adoption"
                    data.trained = "Failed"
                    data.handler = None
                    data.save()

                    handler.partnered = False
                    handler.save()


                    training.stage = "Stage 3.1 - Failed"
                    training.save()

                    style = "ui red message"
                    messages.warning(request, str(data) + " has failed a stage and is now up for adoption.")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
                else:
                    average = Decimal(average) + Decimal(stage3_2)
                    stage = "Stage 3.2"
                    training.stage = stage
                    training.stage3_2 = stage3_2
                    data.training_level = stage
                    
                    data.save()
                    training.save()

                    train_sched = Training_Schedule.objects.create(k9=data, stage=stage, remarks = remarks)
                    style = "ui green message"
                    messages.success(request, str(data) + " has been graded!")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
            elif training.stage == "Stage 3.2":
                stage3_3 = request.POST.get('stage3_3')
                if stage3_3 == "0":
                    data.training_status = "For-Adoption"
                    data.trained = "Failed"
                    data.handler = None
                    data.save()

                    handler.partnered = False
                    handler.save()


                    training.stage = "Stage 3.2 - Failed"
                    training.save()

                    train_sched = Training_Schedule.objects.create(k9=data, stage=stage, remarks = remarks)
                    
                    style = "ui red message"
                    messages.warning(request, str(data) + " has failed a stage and is now up for adoption.")
                    return HttpResponseRedirect('../list-classify-k9?type=grading')
                else:
                    average = Decimal(average) + Decimal(stage3_3)
                    stage = "Finished Training"
                    training.stage = stage
                    training.stage3_3 = stage3_3
                    training.grade = (Decimal(average) / 9)
                    training.remarks = request.POST.get('remarks')
                    data.training_status = "Trained"
                    training.date_finished = datetime.datetime.now()
                    data.training_level = stage
                    data.trained = "Trained"
                    
                    data.save()
                    training.save()

                    style = "ui green message"
                    messages.success(request, str(data) + " has finished training!")

                    return HttpResponseRedirect('../list-classify-k9?type=grading')

    # NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title': data.name,
        'data': data,
        'form': form,
        'notif_data': notif_data,
        'count': count,
        'user': user,
        'training': training,
        'style': style,
    }

    if data.capability == 'EDD':
        return render(request, 'training/training_update_edd.html', context)
    elif data.capability == 'NDD':
        return render(request, 'training/training_update_ndd.html', context)
    else:
        return render(request, 'training/training_update_sar.html', context)


def fail_dog(request, id):
    data = K9.objects.get(id=id) # get k9
    print(data.handler.id)
    k9_handler = User.objects.get(id=data.handler.id)
    k9_handler.partnered = False
    k9_handler.save()

    data.training_status = "For-Adoption"
    data.handler = None
    data.partnered = False
    data.save()

    training = Training.objects.filter(k9=data)

    for training in training:
        training.grade = '75.0'
        training.save()
    return HttpResponseRedirect('../training/list-classify-k9?type=grading')

def training_details(request, id):
    data = K9.objects.get(id=id) # get k9
    
    try:
        train = Training.objects.filter(k9=data).get(training=data.capability) # get training record
    except:
        train=None
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title': str(data),
        'data': data,
        'train': train,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render (request, 'training/training_details.html', context)

def daily_record(request, id):
    form = DateForm(request.POST or None)
    data = K9.objects.get(id=id) # get k9
    context = ''
    record = ''

    if request.method == 'POST':
        if form.is_valid():
            date = request.POST.get('choose_date')
            record = Daily_Refresher.objects.filter(k9=data).get(date_today = date)

    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title': str(data),
        'data': data,
        'form': form,
        'record': record,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render(request, 'training/daily_record.html', context)

def adoption_confirmed(request):

    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render (request, 'training/adoption_confirmed.html', context)


def skill_count_between_breeds(id):
    k9_set = K9.objects.exclude(capability="None")

    breeds = []
    sar_count = []
    ndd_count = []
    edd_count = []

    for k9 in k9_set:
        breeds.append(k9.breed)

    breeds = list(set(breeds))

    print("BREEDS")
    print(breeds)

    for breed in breeds:
        S = K9.objects.filter(capability='SAR', breed=breed)
        N = K9.objects.filter(capability='NDD', breed=breed)
        E = K9.objects.filter(capability='EDD', breed=breed)
        sar_count.append(S.count())
        ndd_count.append(N.count())
        edd_count.append(E.count())


    skill_total = 0
    for count in sar_count:
        skill_total += count
    for count in ndd_count:
        skill_total += count
    for count in edd_count:
        skill_total += count


    sar = 0
    ndd = 0
    edd = 0

    skill_count = []
    target_k9 = K9.objects.get(id = id)
    for dog in k9_set:
        if dog.capability == "SAR" and dog.breed == target_k9.breed:
            sar += 1
        if dog.capability == "NDD" and dog.breed == target_k9.breed:
            ndd += 1
        if dog.capability == "EDD" and dog.breed == target_k9.breed:
            edd += 1

    skill_count.append(sar)
    skill_count.append(ndd)
    skill_count.append(edd)

    print("SKILL COUNT")
    print(skill_count)

    SAR_score = 0
    NDD_score = 0
    EDD_score = 0

    desc2 = ""
    if max(skill_count) == sar and max(skill_count) != 0:
        SAR_score = 1
        desc2 = "SAR"
    if max(skill_count) == ndd and max(skill_count) != 0:
        NDD_score = 1
        desc2 = "NDD"
    if max(skill_count) == edd and max(skill_count) != 0:
        EDD_score = 1
        desc2 = "EDD"

    desc = str(target_k9.name) + " is a " + str(target_k9.breed) + ". " + str(max(skill_count)) + " out of " + str(max(skill_count)) + " trained dogs of the same breed are "+ str(desc2) + ". " + str(desc2) + " is the most recurring skill among " + target_k9.breed + "s."

    graph = None
    classifier = []
    classifier.append(graph)
    classifier.append(SAR_score)
    classifier.append(NDD_score)
    classifier.append(EDD_score)
    classifier.append(desc)

    classifier.append(sar)
    classifier.append(ndd)
    classifier.append(edd)

    return classifier


def make_annotations(pos, labels, M):
    #test = list(map(str, range(7)))
    font_size = 10
    font_color = 'rgb(250,250,250)'
    L=len(pos)
    '''
    if len(test)!=L:
        raise ValueError('The lists pos and text must have the same len')
    '''
    annotations = []#lout.Annotations()
    for k in range(L):
        annotations.append(
            dict (
                text=labels[k], # or replace labels with a different list for the text within the circle
                x=pos[k][0], y=2*M-pos[k][1],
                xref='x1', yref='y1',
                font=dict(color=font_color, size=font_size),
                showarrow=False)
        )
    return annotations

def remove_duplicates(values):
    output = []
    seen = set()
    for value in values:
        # If value has not been encountered yet,
        # ... add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output

def generate_family_tree(id):
    k9 = K9.objects.get(id=id)
    target = k9.name
    genepool = K9_Genealogy.objects.filter(zero = k9)

    g = Graph() #initialize graph

    names = []
    ids = []
    g.vs["name"] = []
    for gene in genepool:
        try:
            g.add_vertices(1)
            f = gene.f
            if f is not None:
                k9_f = K9.objects.get(id=f.id)
                names.append(str(k9_f.name))
                ids.append(k9_f.id)
        except K9.DoesNotExist:
            pass

        try:
            g.add_vertices(1)
            m = gene.m
            if m is not None:
                k9_m = K9.objects.get(id=m.id)
                names.append(str(k9_m.name))
                ids.append(k9_m.id)
        except K9.DoesNotExist:
            pass

        try:
            g.add_vertices(1)
            o = gene.o
            if o is not None:
                k9_o = K9.objects.get(id=o.id)
                names.append(str(k9_o.name))
                ids.append(k9_o.id)
        except K9.DoesNotExist:
            pass

    count_before = len(names)
    # Remove duplicates from this list.
    result = remove_duplicates(names)
    family_ids = remove_duplicates(ids)
    count_after = len(result)
    extras = count_before - count_after
    g.vs["name"] = result #remove_duplicates
    #for extra in range(extras):
        #g.delete_vertices(count_before+1)

    for gene in genepool:
        f = gene.f
        m = gene.m
        o = gene.o
        if f is not None:
            father = K9.objects.get(id=f.id)
            father_name = str(father.name)
            f_index = g.vs.find(name=father_name)
        if m is not None:
            mother = K9.objects.get(id=m.id)
            mother_name = str(mother.name)
            m_index = g.vs.find(name=mother_name)
        if o is not None:
            offspring = K9.objects.get(id=o.id)
            offspring_name = str(offspring.name)
            o_index = g.vs.find(name=offspring_name)

        connection = []

        if o is not None and f is not None:
            g.add_edges([(o_index, f_index)])
            connection.append("Father")
        if o is not None and m is not None:
            g.add_edges([(o_index, m_index)])
            connection.append("Mother")

        g.es["relation"] = connection

    #vertex_count = len(genes)
    #v_label = map(str, range(7))

    '''
    g.add_vertices(7) #Add Points
    g.add_edges([(0, 1), (0, 2), (2, 3), (3, 4), (4, 2), (2, 5), (5, 0), (6, 3), (5, 6)])# Add lines by specifying which vertex is connected to which

    #Add attributes to each vertex and edge (Note that these always follow index id)
    #vs = vertex, should have same number of vertices
    #es = edge, should have same number of edges
    g.vs["name"] = ["Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George"]
    g.vs["age"] = [25, 31, 18, 47, 22, 23, 50]
    g.vs["gender"] = ["f", "m", "f", "m", "f", "m", "m"]
    g.es["is_formal"] = [False, False, True, True, True, False, True, False, False]
    '''

    lay = g.layout("rt")

    position = {k: lay[k] for k in range(count_after)}
    Y = [lay[k][1] for k in range(count_after)]
    M = max(Y)

    es = EdgeSeq(g)  # sequence of edges
    E = [e.tuple for e in g.es]  # list of edges

    L = len(position)
    Xn = [position[k][0] for k in range(L)]
    Yn = [2 * M - position[k][1] for k in range(L)]
    Xe = []
    Ye = []
    for edge in E:
        Xe += [position[edge[0]][0], position[edge[1]][0], None]
        Ye += [2 * M - position[edge[0]][1], 2 * M - position[edge[1]][1], None]

    labels = g.vs["name"]
    relation = g.es["relation"]
    print(labels)
    print(relation)

    size = len(list(labels))
    print("SIZE")
    print(size)
    w = 300
    h = 400

    for x in range(size):
        w += 50
        h += 50

    complete_labels = []
    for member_id in family_ids:
        k9 = K9.objects.get(id = member_id)
        label = str(k9.name) + " : " + str(k9.capability)
        complete_labels.append(label)

    lines = go.Scatter(x=Xe,
                       y=Ye,
                       mode='lines',
                       text=(list(relation)),
                       hoverinfo='text',
                       line=dict(color='rgb(210,210,210)', width=2),
                       )
    dots = go.Scatter(x=Xn,
                      y=Yn,
                      mode='markers',
                      name='',
                      marker=dict(  # symbol='dot',
                          size=80,
                          color='#6175c1',  # '#DB4551',
                          line=dict(color='rgb(50,50,50)', width=1)
                      ),
                      text=(list(labels)),
                      hoverinfo= 'text',
                      opacity=0.8
                      )

    axis = dict(showline=False,  # hide axis line, grid, ticklabels and  title
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                )

    layout = dict(title='Ancestors of K9 '+ str(target),
                  autosize=False,
                  annotations=make_annotations(position, labels, M),
                  font=dict(size=12),
                  showlegend=False,
                  xaxis=lout.XAxis(axis),
                  yaxis=lout.YAxis(axis),
                  width=w,
                  height=h,
                  margin=dict(l=40, r=40, b=85, t=100),
                  hovermode='closest',
                  plot_bgcolor='rgb(248,248,248)'
                  )

    data = [lines, dots]
    fig = dict(data=data, layout=layout)
    graph = opy.plot(fig, auto_open=False, output_type='div')

    return graph


def skill_in_general(id):
    target_k9 = K9.objects.get(id = id)
    k9_family = K9_Genealogy.objects.filter(zero = id)

    k9_list = []
    for k9 in k9_family:
        if k9.o is not None:
            cursor = k9.o
            k9_list.append(cursor.id)
        if k9.f is not None:
            cursor = k9.f
            k9_list.append(cursor.id)
        if k9.m is not None:
            cursor = k9.m
            k9_list.append(cursor.id)

    k9_list = remove_duplicates(k9_list)

    k9_set = K9.objects.filter(pk__in=k9_list).exclude(capability="None").filter()


    '''
    unclassified, classified, on-training, trained, for-breeding, for-adoption, for-deployment, deployed, adopted, breeding, sick, recovery, dead, retired
    '''

    SAR = K9.objects.filter(capability="SAR", pk__in=k9_list)
    NDD = K9.objects.filter(capability="NDD", pk__in=k9_list)
    EDD = K9.objects.filter(capability="EDD", pk__in=k9_list)

    labels = ['SAR', 'NDD', 'EDD']
    values = [SAR.count(), NDD.count(), EDD.count()]

    # trace = go.Pie(labels=labels, values=values,
    #                hoverinfo='label+value', textinfo='percent', )
    #
    # data = [trace]
    #
    # layout = go.Layout(
    #     title="Skill Count of Classified Ancestors (" + str(k9_set.count()) + " dogs)",
    # )
    #
    # fig = go.Figure(data=data, layout=layout)
    # graph = opy.plot(fig, auto_open=False, output_type='div')

    SAR_score = 0
    NDD_score = 0
    EDD_score = 0

    desc2 = ""
    if max(values) == SAR.count() and max(values) != 0 :
        SAR_score = 1
        desc2 = "SAR"
    if max(values) == NDD.count() and max(values) != 0:
        NDD_score = 1
        desc2 = "NDD"
    if max(values) == EDD.count() and max(values) != 0:
        EDD_score = 1
        desc2 = "EDD"

    desc = str(target_k9.name) + " has " + str(max(values)) + " out of " + str(k9_set.count()) + " ancestors who are trained as " + str(desc2) + ". " + str(desc2) + " is the most recurring skill among descendants."

    graph = None
    classifier = []
    classifier.append(graph)
    classifier.append(SAR_score)
    classifier.append(NDD_score)
    classifier.append(EDD_score)
    classifier.append(desc)

    classifier.append(SAR.count())
    classifier.append(NDD.count())
    classifier.append(EDD.count())

    return classifier


def genealogy(id):

    tree = ""
    general = ""
    gender = ""

    cancel = 0
    #data = K9_Genealogy.objects.filter(zero=k9)
    #data.delete()
    K9_Genealogy.objects.all().delete()

    target = K9.objects.get(id=id)
    flag = 0 #SET FLAG FOR WHEN END OF TREE IS REACHED
    counter = 1  # SET INITIAL DEPTH

    k9s = [target]  # INITIAL: TARGET K9 per depth

    while flag == 0: #CONTINUE TREE GENERATION
        for k9 in k9s:# FOR EVERY K9 IN CURRENT DEPTH
            if k9:
                try:
                    k9_parents = K9_Parent.objects.get(offspring=k9)  # FIND TARGET'S PARENTS
                except K9_Parent.DoesNotExist:
                    pass
                else:
                    cancel = 1
                    mother = k9_parents.mother #SET MOTHER
                    father = k9_parents.father #SET FATHER

                    tree = K9_Genealogy(o = k9, m = mother, f = father, depth = counter, zero = target)
                    tree.save()


        nodes = K9_Genealogy.objects.filter(depth = counter)

        k9s = []

        if nodes:
            for node in nodes:
                m = node.m
                f = node.f
                k9s.append(m)# GET TARGET K9s for next depth (mothers)
                k9s.append(f) # GET TARGET K9s for next depth (fathers)

        counter += 1 #INCREASE DEPTH

        if not k9s: #IF FINAL NODES HAVE NO PARENTS, EXIT TREE GENERATION
            flag = 1

        if cancel == 1:
            print("STR ID = " + str(target.id))
            tree = generate_family_tree(target.id)
            #general = skill_in_general(target.id)
            #gender = skills_from_gender(target.id)
            #TODO Put other family related graphs here
        else:
            tree = None

    return tree

def view_family_tree(request, id):
    #TODO fix filtering (low priority)
    k9 = K9.objects.get(id = id)
    tree = genealogy(k9.id)
    k9_genealogy = K9_Genealogy.objects.all()

    context = {
        'k9' : k9,
        'tree': tree,
        'k9_genealogy': k9_genealogy
    }
    return render(request, 'training/genealogy.html', context)


def k9_training_list(request):
    data_ontraining = K9.objects.filter(training_status="On-Training")
    #NOTIF SHOW
    notif_data = notif(request)
    count = notif_data.filter(viewed=False).count()
    user = user_session(request)
    context = {
        'title': 'K9 Training List',
        'data_ontraining': data_ontraining,
        'notif_data':notif_data,
        'count':count,
        'user':user,
    }
    return render (request, 'training/k9_training_list.html', context)

def record_form(request):

    handlerid = request.session["session_id"]
    print(handlerid)
   # data = K9.objects.get(id=id) # get k9
   # training = Training.objects.filter(k9=data).get(training=data.capability) # get training record
   # form = TrainingUpdateForm(request.POST or None, instance = training)


    handler = User.objects.get(id = int(handlerid))
    data = K9.objects.get(handler=handler)
    form2 = RecordForm(request.POST or None)
    title = data.name

    if request.method == 'POST':
        if form2.is_valid():
            record = form2.save(commit=False)
            record.k9 = data
            record.handler = data.handler
            record.save()

    context = {
        'title': title,
        'data': data,
        'form2': form2,
    }
    return render(request, 'training/record_daily.html', context)

def k9_record(request):
    data = K9.objects.all()
    context = {
        'title': "Training Records",
        'data': data,
    }
    return render(request, 'training/k9_record.html', context)

def choose_date(request, id):
    form = DateForm(request.POST or None)
    data = K9.objects.get(id=id)  # get k9

    if request.method == 'POST':
        if form.is_valid():
            choose_date = request.POST.get('choose_date')
            request.session["session_date"] = choose_date
            request.session["session_k9"] = data.id

            return HttpResponseRedirect('daily-record/')

    context = {
        'title': "",
        'form': form,
    }
    return render(request, 'training/choose_date.html', context)

def daily_record_mult(request):
  #  form = DateForm(request.POST or None)
    data = request.session["session_k9"] # get k9
  #  context = ''
    record = ''
    k9 = K9.objects.get(id = data)

    date = request.session["session_date"]
    try:
        record = Daily_Refresher.objects.filter(k9 = k9).get(date_today = date)

    except:
        record = None

    context = {
        'title': str(k9),
        'data': data,
        #'form': form,
        'record': record,
    }
    return render(request, 'training/daily_record.html', context)

def load_handler(request):

    handler = None

    try:
        handler_id = request.GET.get('handler')
        handler = User.objects.get(id=handler_id)

        pi = Personal_Info.objects.get(UserID=handler)
        edd = Handler_K9_History.objects.filter(handler=handler).filter(k9__capability='EDD').count()
        ndd = Handler_K9_History.objects.filter(handler=handler).filter(k9__capability='NDD').count()
        sar = Handler_K9_History.objects.filter(handler=handler).filter(k9__capability='SAR').count()
        

    except:
        pass

    context = {
        'handler': handler,

        'pi':pi,
        'ndd':ndd,
        'edd':edd,
        'sar':sar,

    }

    return render(request, 'training/handler_data.html', context)

def load_form(request):
    formset = None
    k9_formset = None
    try:
        num = request.GET.get('num')
        k9_formset = formset_factory(adoption_K9_form, extra=int(num), can_delete=False)
        formset = k9_formset(request.POST, request.FILES)
    except:
        pass

    context = {
        'formset': k9_formset(),
    }

    return render(request, 'training/load_adoption.html', context)

def load_k9_details(request):
    breed = None
    sex = None
    color = None
    age = None
    try:
        id_val = request.GET.get('id')
        k9 = K9.objects.get(id=id_val)
        breed= k9.breed
        sex= k9.sex
        color= k9.color
        age= str(k9.age) + " yrs & " + str(k9.month_remainder()) + "mos"

    except:
        pass

    data = {
        'breed':breed,
        'sex':sex,
        'color':color,
        'age':age,
    }
    return JsonResponse(data)