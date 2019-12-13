from django.urls import path
from django.conf.urls import include, url
from .import views

app_name='inventory'
urlpatterns = [
    path('', views.index, name='index'),
    #Medicine
    path('add-medicine', views.medicine_add, name='medicine_add'),
    path('edit-medicine/<int:id>/', views.medicine_edit, name='medicine_edit'),
    #Food
    path('add-food', views.food_add, name='food_add'),
    path('edit-food/<int:id>/', views.food_edit, name='food_edit'),
    #Miscellaneous
    path('add-miscellaneous', views.miscellaneous_add, name='miscellaneous_add'),
    path('edit-miscellaneous/<int:id>/', views.miscellaneous_edit, name='miscellaneous_edit'),
    #Inventory
    path('list-medicine-inventory', views.medicine_inventory_list, name='medicine_inventory_list'),
    path('list-food-inventory', views.food_inventory_list, name='food_inventory_list'),
    path('list-miscellaneous-inventory', views.miscellaneous_inventory_list, name='miscellaneous_inventory_list'),
    #inventory Details List
    path('medicine-inventory-details/<int:id>/', views.medicine_inventory_details, name='medicine_inventory_details'),
    path('food-inventory-details/<int:id>/', views.food_inventory_details, name='food_inventory_details'),
    path('miscellaneous-inventory-details/<int:id>/', views.miscellaneous_inventory_details, name='miscellaneous_inventory_details'),
    #inventory Count Form
    path('medicine-count-form/<int:id>/', views.medicine_count_form, name='medicine_count_form'),
    path('food-count-form/<int:id>/', views.food_count_form, name='food_count_form'),
    path('miscellaneous-count-form/<int:id>/', views.miscellaneous_count_form, name='miscellaneous_count_form'),
    #inventory Receive Form
    path('medicine-receive-form/<int:id>/', views.medicine_receive_form, name='medicine_receive_form'),
    path('food-receive-form/<int:id>/', views.food_receive_form, name='food_receive_form'),
    path('miscellaneous-receive-form/<int:id>/', views.miscellaneous_receive_form, name='miscellaneous_receive_form'),
    #inventory Subtract Form
    path('medicine-subtract-form/<int:id>/', views.medicine_subtract_form, name='medicine_subtract_form'),
    path('food-subtract-form/<int:id>/', views.food_subtract_form, name='food_subtract_form'),
    path('miscellaneous-subtract-form/<int:id>/', views.miscellaneous_subtract_form, name='miscellaneous_subtract_form'),
    #damaged form
    path('damaged-form', views.damaged_form, name='damaged_form'),
    path('damaged-report-list', views.damaged_report_list, name='damaged_report_list'),
];