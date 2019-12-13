from django.contrib import admin

from profiles.models import User, Personal_Info, Account, Education
# Register your models here.

admin.site.register(User)
admin.site.register(Personal_Info)
admin.site.register(Education)
admin.site.register(Account)

