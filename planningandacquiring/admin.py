from django.contrib import admin

from .models import K9, K9_Parent, K9_Quantity, K9_Donated, K9_Supplier, K9_Litter, K9_Mated, Dog_Breed, Proposal_Budget, Proposal_K9,Proposal_Milk_Food, Proposal_Vac_Prev, Proposal_Medicine, Proposal_Vet_Supply, Proposal_Kennel_Supply, Proposal_Others,Actual_Budget, Actual_K9,Actual_Milk_Food, Actual_Vac_Prev, Actual_Medicine, Actual_Vet_Supply, Actual_Kennel_Supply, Actual_Others, Proposal_Training, Actual_Training

from training.models import K9_Adopted_Owner

# Register your models here.

admin.site.register(K9)
admin.site.register(K9_Parent)
admin.site.register(K9_Quantity)
admin.site.register(K9_Adopted_Owner)
admin.site.register(Dog_Breed)
admin.site.register(K9_Supplier)
admin.site.register(K9_Litter)
admin.site.register(K9_Mated)

admin.site.register(Proposal_Budget)
admin.site.register(Proposal_K9)
admin.site.register(Proposal_Milk_Food)
admin.site.register(Proposal_Vac_Prev)
admin.site.register(Proposal_Medicine)
admin.site.register(Proposal_Vet_Supply)
admin.site.register(Proposal_Kennel_Supply)
admin.site.register(Proposal_Others)
admin.site.register(Proposal_Training)

admin.site.register(Actual_Budget)
admin.site.register(Actual_K9)
admin.site.register(Actual_Milk_Food)
admin.site.register(Actual_Vac_Prev)
admin.site.register(Actual_Medicine)
admin.site.register(Actual_Vet_Supply)
admin.site.register(Actual_Kennel_Supply)
admin.site.register(Actual_Others)
admin.site.register(Actual_Training)


