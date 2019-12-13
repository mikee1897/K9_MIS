from django.urls import path
from django.conf.urls import include, url
from .import views

app_name='planningandacquiring'
urlpatterns = [
    path('', views.index, name='index'),
    #path('/<int:id>/', views., name=''),
    path('add_donated_K9_form/', views.add_donated_K9, name='add_donated_K9_form'),
    #path('add_donated_K9_form/add_donator_form/', views.add_donator, name='add_donator_form'),
    path('add_donated_K9_form/confirm_donation/', views.confirm_donation, name='confirm_donation'),
    path('donation_confirmed/', views.donation_confirmed, name='donation_confirmed'),
    path('add_K9_parents_form/', views.add_K9_parents, name='add_K9_parents_form'),
    path('add_K9_parents_form/confirm_K9_parents/', views.confirm_K9_parents, name='confirm_K9_parents'),
    path('add_K9_parents_form/confirm_K9_parents/K9_parents_confirmed', views.K9_parents_confirmed, name='K9_parents_confirmed'),
    path('add_K9_offspring/<int:id>', views.add_K9_offspring, name='add_K9_offspring'),
    path('confirm_failed_pregnancy/<int:id>', views.confirm_failed_pregnancy, name='confirm_failed_pregnancy'),
    path('add_K9_parents_form/confirm_K9_parents/add_K9_offspring_form/confirm_breeding/', views.confirm_breeding, name='confirm_breeding'),
    path('breeding_confirmed/', views.breeding_confirmed, name='breeding_confirmed'),
    path('K9_list/', views.K9_listview, name='K9_list'),
    path('K9_detail/<int:id>', views.K9_detailview, name='K9_detail'),
    path('index/', views.index, name='index'),

    path('in_heat_change/', views.in_heat_change, name='in_heat_change'),
    
    path('budgeting/', views.budgeting, name = 'budgeting'),
    path('budget_list/', views.budgeting_list, name='budget_list'),
    path('budgeting_detail/<int:id>', views.budgeting_detail, name='budgeting_detail'),

    path('add_breed_form/', views.add_breed, name='add_breed_form'),
    path('view_breed/', views.breed_listview, name='view_breed'),
    path('breed_list/', views.breed_list, name='breed_list'),
    path('breed_detail/<int:id>', views.breed_detail, name='breed_detail'),
    path('mating_confirmed/', views.mating_confirmed, name='mating_confirmed'),
    path('breeding_list/', views.breeding_list, name='breeding_list'),
    path('breeding_list/<int:id>', views.breeding_list, name='breeding_list'),
    path('breeding_k9_confirmed/', views.breeding_k9_confirmed, name='breeding_k9_confirmed'),
    path('add_supplier/', views.add_supplier, name='add_supplier'),
    path('add_procured_k9/', views.add_procured_k9, name='add_procured_k9'),
    
    path('add_procured_k9/ajax_load_supplier', views.load_supplier, name='ajax_load_supplier'),
    path('add_K9_parents_form/ajax_load_k9_reco', views.load_k9_reco, name='ajax_load_k9_reco'),
    

    # path('procured_form_data/', views.procured_form_data, name='procured_form_data'),

    path('add_K9_parents_form/ajax_load_health', views.load_health, name='ajax_load_health'),
    path('add_K9_offspring/ajax_load_form', views.load_form, name='ajax_load_form'),
    path('add_procured_k9/ajax_load_form_procured', views.load_form_procured, name='ajax_load_form_procured'),
    
    path('budgeting/ajax_load_budget_data', views.load_budget_data, name='ajax_load_budget_data'),
    path('budgeting/ajax_load_budget', views.load_budget, name='ajax_load_budget'),
    
    #REPORTS
    path('k9_performance_date/', views.k9_performance_date, name='k9_performance_date'),
    path('k9_performance_date/k9_performance_report/', views.ajax_k9_performance_report, name='ajax_k9_performance_report'),
    
    path('fou_accomplishment_date/', views.fou_accomplishment_date, name='fou_accomplishment_date'),
    path('fou_accomplishment_date/fou_accomplishment_report/', views.ajax_fou_accomplishment_report, name='ajax_fou_accomplishment_report'),

    path('fou_acc_date/', views.fou_acc_date, name='fou_acc_date'),
    path('fou_acc_date/fou_acc_report/', views.ajax_fou_acc_report, name='ajax_fou_acc_report'),

    path('training_date/', views.training_date, name='training_date'),
    path('training_date/training_report/', views.ajax_training_report, name='ajax_training_report'),

    path('training_summary_date/', views.training_summary_date, name='training_summary_date'),
    path('training_summary_date/training_summary_report/', views.ajax_training_summary_report, name='ajax_training_summary_report'),
    
    path('aor_summary_date/', views.aor_summary_date, name='aor_summary_date'),
    path('aor_summary_date/aor_summary_report/', views.ajax_aor_summary_report, name='ajax_aor_summary_report'),
    
    path('port_date/', views.port_date, name='port_date'),
    path('port_date/port_report/', views.ajax_port_report, name='ajax_port_report'),
    
    path('k9_request_date/', views.k9_request_date, name='k9_request_date'),
    path('k9_request_date/k9_request_report/', views.ajax_k9_request_report, name='ajax_k9_request_report'),


    path('k9_incident_summary_date/', views.k9_incident_summary_date, name='k9_incident_summary_date'),
    path('k9_incident_summary_date/k9_incident_summary_report/', views.ajax_k9_incident_summary_report, name='ajax_k9_incident_summary_report'),
    
    path('k9_breeding_date/', views.k9_breeding_date, name='k9_breeding_date'),
    path('k9_breeding_date/k9_breeding_report/', views.ajax_k9_breeding_report, name='ajax_k9_breeding_report'),
    
    path('health_date/', views.health_date, name='health_date'),
    path('health_date/health_report/', views.ajax_health_report, name='ajax_health_report'),
    
    path('inventory_date/', views.inventory_date, name='inventory_date'),
    path('inventory_date/inventory_report/', views.ajax_inventory_report, name='ajax_inventory_report'),

    path('physical_count_med_date/', views.physical_count_med_date, name='physical_count_med_date'),
    path('physical_count_med_date/physical_count_med_report/', views.ajax_physical_count_med_report, name='ajax_physical_count_med_report'),
    
    path('physical_count_misc_date/', views.physical_count_misc_date, name='physical_count_misc_date'),
    path('physical_count_misc_date/physical_count_misc_report/', views.ajax_physical_count_misc_report, name='ajax_physical_count_misc_report'),
    
    path('physical_count_food_date/', views.physical_count_food_date, name='physical_count_food_date'),
    path('physical_count_food_date/physical_count_food_report/', views.ajax_physical_count_food_report, name='ajax_physical_count_food_report'),
    
    path('received_med_date/', views.received_med_date, name='received_med_date'),
    path('received_med_date/received_med_report/', views.ajax_received_med_report, name='ajax_received_med_report'),
    
    path('received_misc_date/', views.received_misc_date, name='received_misc_date'),
    path('received_misc_date/received_misc_report/', views.ajax_received_misc_report, name='received_count_misc_report'),
    
    path('received_food_date/', views.received_food_date, name='received_food_date'),
    path('received_food_date/received_food_report/', views.ajax_received_food_report, name='ajax_received_food_report'),
    
    path('on_leave_date/', views.on_leave_date, name='on_leave_date'),
    path('on_leave_date/on_leave_report/', views.ajax_on_leave_report, name='ajax_on_leave_report'),
    
    path('demand_supply_date/', views.demand_supply_date, name='demand_supply_date'),
    path('demand_supply_date/demand_supply_report/', views.ajax_demand_supply_report, name='ajax_demand_supply_report'),
    
    path('supplier_date/', views.supplier_date, name='supplier_date'),
    path('supplier_date/supplier_report/', views.ajax_supplier_report, name='ajax_supplier_report'),
    
    path('adoption_date/', views.adoption_date, name='adoption_date'),
    path('adoption_date/adoption_report/', views.ajax_adoption_report, name='ajax_adoption_report'),
];

