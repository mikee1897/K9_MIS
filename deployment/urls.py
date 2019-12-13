from django.urls import path
from django.conf.urls import include, url
from .import views

app_name='deployment'
urlpatterns = [
    path('', views.index, name='index'),
    path('add-area/', views.add_area, name='add_area'),
    path('add-location/', views.add_location, name='add_location'),
    path('assign-team-location/', views.assign_team_location, name='assign_team_location'),
    path('assigned-location-list/', views.assigned_location_list, name='assigned_location_list'),
    path('team-location-details/<int:id>', views.team_location_details, name='team_location_details'),
    path('edit-team/<int:id>', views.edit_team, name='edit_team'),
    path('remove-dog-deployed/<int:id>', views.remove_dog_deployed, name='remove_dog_deployed'),
    path('request_form/', views.dog_request, name='request_form'),
    path('request_dog_list/', views.request_dog_list, name='request_dog_list'),
    path('request_dog_details/<int:id>', views.request_dog_details, name='request_dog_details'),
    path('remove-dog-request/<int:id>', views.remove_dog_request, name='remove_dog_request'),
    path('view-schedule/<int:id>', views.view_schedule, name='view_schedule'),
    path('add-incident/', views.add_incident, name='add_incident'),
    path('view-incidents/', views.incident_list, name='view_incidents'),


    path('incident-detail/<int:id>', views.incident_detail, name='incident_detail'),

    path('choose-date/', views.choose_date, name='choose_date'),
    path('choose-date/deployment-report/', views.deployment_report, name='deployment_report'),

    path('deployment-area-details/', views.deployment_area_details, name='deployment_area_details'),
    path('fou-details/', views.fou_details, name='fou_details'),
    path('daily-refresher-form', views.daily_refresher_form, name='daily_refresher_form'),


    path('add-location/ajax_load_locations', views.load_locations, name='ajax_load_locations'),
    path('add-location/ajax_load_map', views.load_map, name='ajax_load_map'),
    path('request_form/ajax_load_locations', views.load_locations, name='ajax_load_locations'),
    path('request_form/ajax_load_map', views.load_map, name='ajax_load_map'),

    path('choose-location/', views.choose_location, name='choose_location'),
    path('choose-location/ajax_load_units', views.load_units, name='ajax_load_units'),
    path('choose-location/ajax_load_units_selected', views.load_units_selected, name='ajax_load_units_selected'),

    path('schedule-units', views.schedule_units, name = 'schedule_units'),

    path('pre_req_unconfirmed', views.pre_req_unconfirmed, name='pre_req_unconfirmed'),
    path('pre_req_unconfirmed/ajax_load_pre_req', views.load_pre_req, name='load_pre_req'),

    # path('dogs-deployed', views.deployed_dogs, name='deployed_dogs'),
    # path('dogs-requested', views.requested_dogs, name='requested_dogs'),
    # path('deploy-number-dogs', views.deploy_number_dogs, name='deploy_number_dogs'),
    # path('location-form', views.location_form, name='location_form'),
    # path('assign_team/', views.assign_team, name='assign_team'),
    # path('load-teams/', views.load_teams, name='ajax_load_teams'),  # <-- this one here
    # path('area_list/', views.area_list_view, name='area_list'),
    # path('add_location/', views.area_form, name='add_location'),
    # path('add_team/', views.team_form, name='add_team'),
    # path('area_detail/<int:id>', views.area_list_detail, name='area_detail'),
    #path('/<int:id>/', views., name=''),
];
