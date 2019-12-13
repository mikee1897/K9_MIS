from django import template
# from planningandacquiring.models import Budget_allocation, Budget_medicine, Budget_equipment, Budget_food, Budget_vaccine, Budget_vet_supply
from inventory.models import Medicine, Miscellaneous, Food
from unitmanagement.forms import SelectUnitsForm
from deployment.models import Location, Team_Assignment
from datetime import date, datetime, timedelta

register = template.Library()

@register.filter
def render_k9_checkbox(k9, selected_list): #check_true as form parameter to set initial value as true
    k9_list = []
    k9_list.append((k9.id, k9.name))

    print("K9_LIST")
    print(k9_list)

    k9_is_checked = False

    for item in selected_list:
        if int(item) == int(k9.id):
            k9_is_checked = True

    if k9_is_checked == True:
        unit_form = SelectUnitsForm(k9_dict=k9_list, check_true=True)
    else:
        unit_form = SelectUnitsForm(k9_dict=k9_list)

    return unit_form['k9'][0].tag()

@register.filter
def list_item(List, i):

    return List[i]

@register.filter
def list_item_date(List, i):

    date = List[i]

    year = date.year
    month = date.month
    day = date. day

    new_date = datetime(year=year, month=month, day=day)

    return new_date.strftime("%Y-%m-%d")

@register.filter
def formset_item(formset, i):

    return formset.forms[i].fields['quantity']

# @register.filter
# def get_medicine_price(object, i):

#     budget_med = Budget_medicine.objects.get(medicine = object)
#     return budget_med.price

# @register.filter
# def get_medicine_quantity(object, i):

#     budget_med = Budget_medicine.objects.get(medicine = object)
#     return budget_med.quantity

@register.filter
def get_medicine_name(med_budget, i):

    med = Medicine.objects.get(id = med_budget.medicine.id)

    return med.medicine

@register.filter
def get_vaccine_name(vac_budget, i):

    vac = Medicine.objects.get(id = vac_budget.vaccine.id)

    return vac.medicine

@register.filter
def get_equipment_name(equipment_budget, i):

    equipment = Miscellaneous.objects.get(id = equipment_budget.equipment.id)

    return equipment.miscellaneous

@register.filter
def get_vet_name(vet_budget, i):

    vet = Miscellaneous.objects.get(id = vet_budget.vet_supply.id)

    return vet.miscellaneous

@register.filter
def get_food_name(food_budget, i):

    food = Food.objects.get(id = food_budget.food.id)

    return food.food

@register.filter
def get_medicine_recent_price(med_budget_price_list, i):


    return med_budget_price_list[i]

@register.filter
def get_quantity_medicine(quantity_medicine, i):

    object = quantity_medicine[i]

    return object.quantity

@register.filter
def get_quantity_spendings(spendings_list, i):

    list = spendings_list[i]

    #total = object.quantity * object.price

    return list

@register.filter
def recent_budget_medicine(recent_budget_medicine, i):

    object = recent_budget_medicine[i]

    return object.total

@register.filter
def equipment_quantity(equipment_objects, i):

    object = equipment_objects[i]

    return object.quantity


@register.filter
def get_team_name(k9_schedule):
    return str(k9_schedule.team.location.city)

@register.filter
def get_event_name(k9_schedule):

    return k9_schedule.dog_request.event_name

@register.filter
def get_number_of_units(choice):

    id = choice.data['value']
    loc = Location.objects.get(id = choice.data['value'] )
    team = Team_Assignment.objects.filter(location = loc).last()


    return team.total_dogs_deployed


@register.filter
def recommended_checkup_date(deployment_date):
    adjusted_date = deployment_date - timedelta(days=7)
    weekno = adjusted_date.weekday()
    while weekno > 5:
        adjusted_date += timedelta(days=1)
        weekno = adjusted_date.weekday()

    return adjusted_date