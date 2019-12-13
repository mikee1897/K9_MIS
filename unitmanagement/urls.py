from django.urls import path
from django.conf.urls import include, url
from .import views
from django.views.generic import TemplateView

app_name='unitmanagement'
urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('health-form', views.health_form, name='health_form'),
    path('health-record', views.health_record, name='health_record'),
    path('health-history/<int:id>', views.health_history, name='health_history'),
    path('health-history-handler', views.health_history_handler, name='health_history_handler'),
    path('health-details/<int:id>', views.health_details, name='health_details'),
    path('physical-exam-details/<int:id>', views.physical_exam_details, name='physical_exam_details'),
    path('approve-medicine/<int:id>', views.medicine_approve, name='medicine_approve'),
    # path('request-form', views.requests_form, name='request_form'),
    #path('request-list', views.request_list, name='request_list'),
    path('k9-incident', views.k9_incident, name='k9_incident'),
    path('handler-incident-form', views.handler_incident_form, name='handler_incident_form'),
    path('reproductive-list', views.reproductive_list, name='reproductive_list'),
    path('reproductive-edit/<int:id>', views.reproductive_edit, name='reproductive_edit'),
    path('k9-unpartnered-list', views.k9_unpartnered_list, name='k9_unpartnered_list'),
    path('choose-handler-list/<int:id>', views.choose_handler_list, name='choose_handler_list'),
    path('choose-handler/<int:id>', views.choose_handler, name='choose_handler'),
    path('k9-sick-form', views.k9_sick_form, name='k9_sick_form'),
    path('k9-sick-list', views.k9_sick_list, name='k9_sick_list'),
    path('k9-sick-details/<int:id>', views.k9_sick_details, name='k9_sick_details'),
    path('on-leave-request', views.on_leave_request, name='on_leave_request'),
    path('on-leave-list', views.on_leave_list, name='on_leave_list'),
    path('on-leave-decision/<int:id>', views.on_leave_decision, name='on_leave_decision'),
    # path('on-leave-details/<int:id>', views.on_leave_details, name='on_leave_details'),

    path('transfer-request-form', views.transfer_request_form, name='transfer_request_form'),
    path('transfer-request-list', views.transfer_request_list, name='transfer_request_list'),
    path('due-retired-list', views.due_retired_list, name='due_retired_list'),
    path('due-retired-call/<int:id>', views.due_retired_call, name='due_retired_call'),

    path('called-back-list', views.confirm_base_arrival, name='confirm_base_arrival'),
    path('confirm_arrive/<int:id>', views.confirm_arrive, name='confirm_arrive'),
    path('confirm_going_back/<int:id>', views.confirm_going_back, name='confirm_going_back'),

    path('unfit-list', views.unfit_list, name='unfit_list'),
    path('health-list', views.health_list_handler, name='health_list_handler'),
    path('k9-incident-list', views.k9_incident_list, name='k9_incident_list'),
    path('k9-retrieved/<int:id>', views.k9_retreived, name='k9_retreived'),
    path('follow-up/<int:id>', views.follow_up, name='follow_up'),

    path('yearly-vaccine-list', views.yearly_vaccine_list, name='yearly_vaccine_list'),
    path('vaccination-list', views.vaccination_list, name='vaccination_list'),
    path('vaccine_submit', views.vaccine_submit, name='vaccine_submit'),
    #path('choose-date/<int:id>', views.choose_date, name='choose_date'),

    path('redirect-notif/<int:id>', views.redirect_notif, name='redirect_notif'),

    path('choose-handler-list/ajax_load_handler', views.load_handler, name='ajax_load_handler'),
    path('health-history/ajax_load_stamp', views.load_stamp, name='ajax_load_stamp'),
    path('ajax_load_k9', views.load_k9, name='ajax_load_k9'),

    path('k9-sick-details/ajax_load_health', views.load_health, name='ajax_load_health'),
    path('k9-incident-list/ajax_load_incident', views.load_incident, name='ajax_load_incident'),
    path('k9-sick-details/ajax_load_image', views.load_image, name='ajax_load_image'),
    path('yearly-vaccine-list/ajax_load_yearly_vac', views.load_yearly_vac, name='ajax_load_yearly_vac'),
    path('vaccination-list/ajax_load_yearly_vac', views.load_yearly_vac, name='ajax_load_yearly_vac'),
    path('unfit-list/ajax_load_physical', views.load_physical, name='ajax_load_physical'),
    path('reassign-assets/ajax_load_handler', views.load_handler, name='load_handler'),
    path('trained-list/ajax_load_k9_data', views.load_k9_data, name='ajax_load_k9_data'),
    path('transfer-request-list/ajax_load_transfer', views.load_transfer, name='load_transfer'),

    path('reassign-assets/<int:id>', views.reassign_assets, name='reassign_assets'),
    # path('confirm-death/<int:id>', views.confirm_death, name='confirm_death'),
    path('trained-list', views.trained_list, name='trained_list'),
    path('classified-list', views.classified_list, name='classified_list'),
    #path('change-equipment/<int:id>', views.change_equipment, name='change_equipment'),
    path('transfer-request-list/ajax_load_handler', views.load_handler, name='ajax_load_handler'),

    path('replenishment_form', views.replenishment_form, name='replenishment_form'),
    path('replenishment_form/ajax_load_item', views.load_item, name='load_item'),
    path('replenishment_form/ajax_load_item_food', views.load_item_food, name='load_item_food'),
    path('replenishment_form/ajax_load_item_med', views.load_item_med, name='load_item_med'),
    path('replenishment_form/ajax_load_item_misc', views.load_item_misc, name='load_item_misc'),

    path('replenishment_confirm', views.replenishment_confirm, name='replenishment_confirm'),
    path('replenishment_approval/<int:id>', views.replenishment_approval, name='replenishment_approval'),
    path('load_item/', views.load_item, name='load_item'),


    path('confirm_item_request/<int:id>', views.confirm_item_request, name='confirm_item_request'),

    path('team-leader/api', views.TeamLeaderView.as_view()),
    path('handler/api', views.HandlerView.as_view()),
    path('vet/api', views.VetView.as_view()),
    path('commander/api', views.CommanderView.as_view()),
    path('trainer/api', views.TrainerView.as_view()),
    path('admin/api', views.AdminView.as_view()),


    path('k9-checkup-pending', views.k9_checkup_pending, name='k9_checkup_pending'),
    path('ajax_load_appointments', views.load_appointments, name='ajax_load_appointments'),
    path('ajax_load_checkups', views.load_checkups, name='ajax_load_checkups'),

    path('k9-checkup-list-today', views.k9_checkup_list_today, name = 'k9_checkup_list_today'),
    path('physical-exam-form/', views.physical_exam_form, name='physical_exam_form'),
    path('physical-exam-form/<int:id>', views.physical_exam_form, name='physical_exam_form'),

    path('k9-mia-list', views.k9_mia_list, name ='k9_mia_list'),
    path('k9_mia_change/<int:id>', views.k9_mia_change, name ='k9_mia_change'),
    # add in unitmanagement urls.py
    path('replenishment_form/ajax_load_item', views.load_item, name='load_item'),
    path('k9_accident/<int:id>', views.k9_accident, name ='k9_accident'),
    path('k9_accident', views.k9_accident, name ='k9_accident'),
    #path('/<int:id>/', views., name=''),

    path('emergency_leave_list', views.emeregency_leave_list, name ='emergency_leave_list'),
    path('handler_status_mia/<int:id>', views.handler_status_mia, name ='handler_status_mia'),
    path('k9_accident_death_handler', views.k9_accident_death_handler, name ='k9_accident_death_handler'),

    path('replenishment_confirm/ajax_load_replenishment', views.load_replenishment, name='load_replenishment'),
    
    path('mia_fou/<int:id>', views.mia_fou, name ='mia_fou'),

    # path('returning_handlers_list', views.returning_handlers_list, name ='returning_handlers_list'),
];
