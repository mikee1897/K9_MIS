from django.contrib import admin
from unitmanagement.models import Health, HealthMedicine, PhysicalExam, VaccinceRecord, VaccineUsed, Transaction_Health
from unitmanagement.models import K9_Incident, Handler_Incident, Notification,Handler_K9_History, Image, Handler_On_Leave, Request_Transfer, Call_Back_K9, Miscellaneous_Request, Medicine_Request, Food_Request, Replenishment_Request, Emergency_Leave

# Register your models here.
admin.site.register(Health)
admin.site.register(HealthMedicine)
admin.site.register(PhysicalExam)
admin.site.register(VaccinceRecord)
admin.site.register(VaccineUsed)
admin.site.register(K9_Incident)
admin.site.register(Handler_Incident)
admin.site.register(Handler_On_Leave)
admin.site.register(Emergency_Leave)
admin.site.register(Notification)
# admin.site.register(Equipment_Request)
admin.site.register(Food_Request)
# admin.site.register(All_Item_Request)
admin.site.register(Handler_K9_History)
admin.site.register(Image)
admin.site.register(Transaction_Health)
admin.site.register(Request_Transfer)
admin.site.register(Call_Back_K9)
admin.site.register(Miscellaneous_Request)
admin.site.register(Medicine_Request)
admin.site.register(Replenishment_Request)