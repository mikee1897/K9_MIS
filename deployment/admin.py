from django.contrib import admin

from deployment.models import Area, Location, Team_Assignment, Team_Dog_Deployed, Incidents, K9_Schedule
from deployment.models import Dog_Request, Daily_Refresher, K9_Pre_Deployment_Items, Maritime
# Register your models here.
admin.site.register(Area)
admin.site.register(Location)
admin.site.register(Team_Assignment)
admin.site.register(Team_Dog_Deployed)
admin.site.register(Incidents)
admin.site.register(K9_Schedule)
admin.site.register(Dog_Request)
admin.site.register(Daily_Refresher)
admin.site.register(Maritime)
admin.site.register(K9_Pre_Deployment_Items)
