from django.urls import path
from django.conf.urls import include, url
from .import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from rest_framework import routers

router = routers.DefaultRouter()
router.register('user', views.UserView)


app_name='profiles'
urlpatterns = [
    path('team-leader-dashboard/', views.team_leader_dashboard, name='team_leader_dashboard'),
    path('handler-dashboard/', views.handler_dashboard, name='handler_dashboard'),
    path('vet-dashboard/', views.vet_dashboard, name='vet_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('commander-dashboard/', views.commander_dashboard, name='commander_dashboard'),
    path('operations-dashboard/', views.operations_dashboard, name='operations_dashboard'),
    path('trainer-dashboard/', views.trainer_dashboard, name='trainer_dashboard'),

    path('profile/', views.profile, name='profile'),
    path('notifications/', views.notif_list, name='notif_list'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),
    path('add_User_form/', views.add_User, name='add_User_form'),
    path('add_User_form/add_personal_form/', views.add_personal_info, name='add_personal_form'),
    path('add_User_form/add_personal_form/add_education/', views.add_education, name='add_education'),
    path('add_User_form/add_personal_form/add_education/add_user_account/', views.add_user_account, name='add_user_account'),
    path('user_list/', views.user_listview, name='user_list'),
    path('user_detail/<int:id>', views.user_detailview, name='user_detail'),
    path('user_add_confirmed/', views.user_add_confirmed, name='user_add_confirmed'),
    
    path('dashboard/update_event/', views.update_event, name='update_event'),

    path('api', views.NotificationListView.as_view()),
    path('api/<int:id>', views.NotificationDetailView.as_view()),

    path('handler-dashboard/ajax_load_locations', views.load_locations, name='ajax_load_locations'),
    path('handler-dashboard/ajax_load_map', views.load_map, name='ajax_load_map'),
    
    path('operations-dashboard/ajax_load_locations', views.load_locations, name='ajax_load_locations'),
    path('operations-dashboard/ajax_load_map', views.load_map, name='ajax_load_map'),
    path('team-leader-dashboard/ajax_load_locations', views.load_locations, name='ajax_load_locations'),
    path('team-leader-dashboard/ajax_load_map', views.load_map, name='ajax_load_map'),

    path('operations-dashboard/ajax_load_event', views.load_event, name = "ajax_load_event"),
    path('team-leader-dashboard/ajax_load_event', views.load_event, name = "ajax_load_event"),
    path('commander-dashboard/ajax_load_event', views.load_event, name = "ajax_load_event"),
    path('dashboard/ajax_load_event', views.load_event, name = "ajax_load_event"),
    path('handler-dashboard/ajax_load_event_handler', views.load_event_handler, name = "ajax_load_event_handler"),

    path('schedule/api', views.ScheduleView.as_view()),
    path('handler-dashboard/team-location-details/<int:id>', views.team_location_details, name='team_location_details'),
    path('handler-dashboard/request_dog_details/<int:id>', views.request_dog_details, name='request_dog_details'),

    # path('user/api', views.UserListView.as_view()),
    # path('user/api/<int:id>', views.UserDetailView.as_view()),

    path('user/api', include(router.urls)),

];