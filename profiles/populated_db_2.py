from faker import Faker
import random
from datetime import timedelta, datetime, date
from profiles.models import User, Account, Personal_Info, Education
from planningandacquiring.models import K9, K9_Supplier, Dog_Breed, K9_Mated, K9_Parent, K9_Litter
from deployment.models import Area, Location, Dog_Request, Incidents, Maritime, Team_Assignment, K9_Pre_Deployment_Items, \
    K9_Schedule, Team_Dog_Deployed
from django.contrib.auth.models import User as AuthUser
from training.models import Training, Training_Schedule, Training_History, K9_Adopted_Owner
from inventory.models import Miscellaneous, Food, Medicine_Inventory, Medicine, Food_Received_Trail, Food_Subtracted_Trail, Food_Inventory_Count, Medicine_Received_Trail, Medicine_Subtracted_Trail, Medicine_Inventory_Count, Miscellaneous_Received_Trail, Miscellaneous_Subtracted_Trail, Miscellaneous_Inventory_Count
from deployment.models import Daily_Refresher

from unitmanagement.models import PhysicalExam, Handler_Incident, K9_Incident, Health, HealthMedicine, Handler_On_Leave, Emergency_Leave, Handler_K9_History, VaccinceRecord, VaccineUsed
from itertools import groupby

from dateutil.relativedelta import *
from deployment.tasks import assign_TL
from django.db.models import Q
import re
'''
For more info on faker.Faker, view https://faker.readthedocs.io/en/latest/index.html

Populate DB process

REPORTS
1.)generate_dogbreed()
    a.)Creates Dog Breed Details

DEPLOYMENT
1.)create_predeployment_inventory()
    a.) Creates Pre Deployment Inventory Items
    b.) Creates Mandatory Vaccines and Prevention
2.)create_teams() - generate_user() first to assign commander
    a.) Creates Areas
    b.) Creates Locations
    c.) Creates Team_assignments
    d.) Assigns Commander

USER-K9
1.)generate_user()
  a.) Creates User
  b.) Creates Personal Info
  c.) Creates Education
  d.) Creates Account
2.) generate_k9()
  a.) Creates K9 (500 procured)
  b.) Creates Supplier
  c.) Assign Capability to 95% of procured k9s
  d.) Assign Handler to 80% of classified k9s
  e.) Complete training for 80% of partnered k9s
    - Creates Training
    - Creates Training_Sched
    - Creates Training_History
  f.) Make 90% of trained k9s "For-Deployment", the other 90% are "For-Breeding"
  g.) Assign 70% of "For-Deployment" k9s to a port
    - Creates Pre_Deployment_Items
    - Creates "Initial Deployment" K9 Schedule
    - Creates "Checkup" K9 Schedule
    - Creates Team Dog Deployed
    - Creates PhysicalExam
    - Assigns TL
'''

def generate_city_ph():

    CITY = (
        ('Alaminos', 'Alaminos'),
        ('Angeles', 'Angeles'),
        ('Antipolo', 'Antipolo'),
        ('Bacolod', 'Bacolod'),
        ('Bacoor', 'Bacoor'),
        ('Bago', 'Bago'),
        ('Baguio', 'Baguio'),
        ('Bais', 'Bais'),
        ('Balanga', 'Balanga'),
        ('Batac', 'Batac'),
        ('Batangas', 'Batangas'),
        ('Bayawan', 'Bayawan'),
        ('Baybay', 'Baybay'),
        ('Bayugan', 'Bayugan'),
        ('Biñan', 'Biñan'),
        ('Bislig', 'Bislig'),
        ('Bogo', 'Bogo'),
        ('Borongan', 'Borongan'),
        ('Butuan', 'Butuan'),
        ('Cabadbaran', 'Cabadbaran'),
        ('Cabanatuan', 'Cabanatuan'),
        ('Cabuyao', 'Cabuyao'),
        ('Cadiz', 'Cadiz'),
        ('Cagayan de Oro', 'Cagayan de Oro'),
        ('Calamba', 'Calamba'),
        ('Calapan', 'Calapan'),
        ('Calbayog', 'Calbayog'),
        ('Caloocan', 'Caloocan'),
        ('Candon', 'Candon'),
        ('Canlaon', 'Canlaon'),
        ('Carcar', 'Carcar'),
        ('Catbalogan', 'Catbalogan'),
        ('Cauayan', 'Cauayan'),
        ('Cavite', 'Cavite'),
        ('Cebu', 'Cebu'),
        ('Cotabato', 'Cotabato'),
        ('Dagupan', 'Dagupan'),
        ('Danao', 'Danao'),
        ('Dapitan', 'Dapitan'),
        ('Dasmariñas', 'Dasmariñas'),
        ('Davao', 'Davao'),
        ('Digos', 'Digos'),
        ('Dipolog', 'Dipolog'),
        ('Dumaguete', 'Dumaguete'),
        ('El Salvador', 'El Salvador'),
        ('Escalante', 'Escalante'),
        ('Gapan', 'Gapan'),
        ('General Santos', 'General Santos'),
        ('General Trias', 'General Trias'),
        ('Gingoog', 'Gingoog'),
        ('Guihulngan', 'Guihulngan'),
        ('Himamaylan', 'Himamaylan'),
        ('Ilagan', 'Ilagan'),
        ('Iligan', 'Iligan'),
        ('Iloilo', 'Iloilo'),
        ('Imus', 'Imus'),
        ('Iriga', 'Iriga'),
        ('Isabela', 'Isabela'),
        ('Kabankalan', 'Kabankalan'),
        ('Kidapawan', 'Kidapawan'),
        ('Koronadal', 'Koronadal'),
        ('La Carlota', 'La Carlota'),
        ('Lamitan', 'Lamitan'),
        ('Laoag', 'Laoag'),
        ('Lapu‑Lapu', 'Lapu‑Lapu'),
        ('Las Piñas', 'Las Piñas'),
        ('Legazpi', 'Legazpi'),
        ('Ligao', 'Ligao'),
        ('Lipa', 'Lipa'),
        ('Lucena', 'Lucena'),
        ('Maasin', 'Maasin'),
        ('Mabalacat', 'Mabalacat'),
        ('Makati', 'Makati'),
        ('Malabon', 'Malabon'),
        ('Malaybalay', 'Malaybalay'),
        ('Malolos', 'Malolos'),
        ('Mandaluyong', 'Mandaluyong'),
        ('Mandaue', 'Mandaue'),
        ('Manila', 'Manila'),
        ('Marawi', 'Marawi'),
        ('Marikina', 'Marikina'),
        ('Masbate', 'Masbate'),
        ('Mati', 'Mati'),
        ('Meycauayan', 'Meycauayan'),
        ('Muñoz', 'Muñoz'),
        ('Muntinlupa', 'Muntinlupa'),
        ('Naga - Camarines Sur', 'Naga - Camarines Sur'),
        ('Naga - Cebu', 'Naga - Cebu'),
        ('Navotas', 'Navotas'),
        ('Olongapo', 'Olongapo'),
        ('Ormoc', 'Ormoc'),
        ('Oroquieta', 'Oroquieta'),
        ('Ozamiz', 'Ozamiz'),
        ('Pagadian', 'Pagadian'),
        ('Palayan', 'Palayan'),
        ('Panabo', 'Panabo'),
        ('Parañaque', 'Parañaque'),
        ('Pasay', 'Pasay'),
        ('Pasig', 'Pasig'),
        ('Passi', 'Passi'),
        ('Puerto Princesa', 'Puerto Princesa'),
        ('Quezon', 'Quezon'),
        ('Roxas', 'Roxas'),
        ('Sagay', 'Sagay'),
        ('Samal', 'Samal'),
        ('San Carlos - Negros Occidental', 'San Carlos - Negros Occidental'),
        ('San Carlos - Pangasinan', 'San Carlos - Pangasinan'),
        ('San Fernando - La Union', 'San Fernando - La Union'),
        ('San Fernando - Pampanga', 'San Fernando - Pampanga'),
        ('San Jose', 'San Jose'),
        ('San Jose del Monte', 'San Jose del Monte'),
        ('San Juan', 'San Juan'),
        ('San Pablo', 'San Pablo'),
        ('San Pedro', 'San Pedro'),
        ('Santa Rosa', 'Santa Rosa'),
        ('Santiago', 'Santiago'),
        ('Silay', 'Silay'),
        ('Sipalay', 'Sipalay'),
        ('Sorsogon', 'Sorsogon'),
        ('Surigao', 'Surigao'),
        ('Tabaco', 'Tabaco'),
        ('Tabuk', 'Tabuk'),
        ('Tacloban', 'Tacloban'),
        ('Tacurong', 'Tacurong'),
        ('Tagaytay', 'Tagaytay'),
        ('Tagbilaran', 'Tagbilaran'),
        ('Taguig', 'Taguig'),
        ('Tagum', 'Tagum'),
        ('Talisay - Cebu', 'Talisay - Cebu'),
        ('Talisay - Negros Occidental', 'Talisay - Negros Occidental'),
        ('Tanauan', 'Tanauan'),
        ('Tandag', 'Tandag'),
        ('Tangub', 'Tangub'),
        ('Tanjay', 'Tanjay'),
        ('Tarlac', 'Tarlac'),
        ('Tayabas', 'Tayabas'),
        ('Toledo', 'Toledo'),
        ('Trece Martires', 'Trece Martires'),
        ('Tuguegarao', 'Tuguegarao'),
        ('Urdaneta', 'Urdaneta'),
        ('Valencia', 'Valencia'),
        ('Valenzuela', 'Valenzuela'),
        ('Victorias', 'Victorias'),
        ('Vigan', 'Vigan'),
        ('Zamboanga', 'Zamboanga')
    )

    randomizer = random.randint(0, len(CITY) - 1)

    return CITY[randomizer][0]

# START REPORT NECESSITIES
def generate_dogbreed():
    COLOR = (
        ('Black', 'Black'),
        ('Chocolate', 'Chocolate'),
        ('Yellow', 'Yellow'),
        ('Dark Golden', 'Dark Golden'),
        ('Light Golden', 'Light Golden'),
        ('Cream', 'Cream'),
        ('Golden', 'Golden'),
        ('Brindle', 'Brindle'),
        ('Silver Brindle', 'Silver Brindle'),
        ('Gold Brindle', 'Gold Brindle'),
        ('Salt and Pepper', 'Salt and Pepper'),
        ('Gray Brindle', 'Gray Brindle'),
        ('Blue and Gray', 'Blue and Gray'),
        ('Tan', 'Tan'),
        ('Black-Tipped Fawn', 'Black-Tipped Fawn'),
        ('Mahogany', 'Mahogany'),
        ('White', 'White'),
        ('Black and White', 'Black and White'),
        ('White and Tan', 'White and Tan')
    )

    arr = ['Belgian Malinois', 'Dutch Sheperd', 'German Sheperd', 'Golden Retriever', 'Jack Russel',
           'Labrador Retriever']

    temperament_list = ['Friendly', 'Skittish', 'Timid', 'Wild', 'Adventurous']
    skill_list = ['EDD', 'NDD', 'SAR']

    for data in arr:
        randomizer = random.randint(0, 4)
        randomizer2 = random.randint(0, 2)
        temperament = temperament_list[randomizer]
        skill = skill_list[randomizer2]

        random_val1 = random.randint(10000, 15000)
        random_val2 = random.randint(15000, 20000)
        litter_val = random.randint(4, 8)

        arr1 = ['EDD', 'NDD', 'SAR']
        arr2 = []

        while len(arr1) != 0:
            randomizer2 = random.randint(0, 2)
            skill1 = skill_list[randomizer2]
            if skill1 in arr1:
                arr1.remove(skill1)
                arr2.append(skill1)

        randomizer = random.randint(0, 18)
        color = COLOR[randomizer][0]
        Dog_Breed.objects.create(breed=data, sex='Male', life_span=10, temperament=temperament,
                                 colors=color, weight=20, male_height=10, female_height=10,
                                 skill_recommendation=arr2[0], skill_recommendation2=arr2[1],
                                 skill_recommendation3=arr2[2], litter_number=litter_val, value=random_val1)

        Dog_Breed.objects.create(breed=data, sex='Female', life_span=10, temperament=temperament,
                                 colors=color, weight=20, male_height=10, female_height=10,
                                 skill_recommendation=arr2[0], skill_recommendation2=arr2[1],
                                 skill_recommendation3=arr2[2], litter_number=litter_val, value=random_val2)
        print("Generated Dog Breed : " + str(data))

    return None
# END REPORT NECESSITIES

# START DEPLOYMENT NECESSITIES
def create_predeployment_inventory():
    randomizer = random.randint(30, 100)
    collar = Miscellaneous.objects.create(miscellaneous="Collar", misc_type="Kennel Supply", uom="pc",
                                          quantity=randomizer, price=199.12)
    randomizer = random.randint(30, 100)
    vest = Miscellaneous.objects.create(miscellaneous="Vest", misc_type="Kennel Supply", uom="pc",
                                        quantity=randomizer, price=900.21)
    randomizer = random.randint(30, 100)
    leash = Miscellaneous.objects.create(miscellaneous="Leash", misc_type="Kennel Supply", uom="pc",
                                         quantity=randomizer, price=230.41)
    randomizer = random.randint(30, 100)
    shipping_crate = Miscellaneous.objects.create(miscellaneous="Shipping Crate", misc_type="Kennel Supply", uom="pc",
                                                  quantity=randomizer, price=1500.24)

    randomizer = random.randint(100, 250)
    food = Food.objects.create(food="Pedigree Sack", foodtype="Adult Dog Food", unit="Sack - 20kg", quantity=randomizer,price=1500)

    randomizer = random.randint(100, 250)
    Food.objects.create(food="Pedigree Puppy", foodtype="Puppy Dog Food", unit="kilograms", quantity=randomizer,price=120)

    randomizer = random.randint(100, 250)
    Food.objects.create(food="Pedigree", foodtype="Adult Dog Food", unit="kilograms", quantity=randomizer,price=120)

    randomizer = random.randint(100, 250)
    Food.objects.create(food="Pedigree Puppy Sack", foodtype="Puppy Dog Food", unit="Sack - 20kg", quantity=randomizer,price=1500)

    Food.objects.create(food="Cosi Milk", foodtype="Milk", unit="Box - 1L", quantity=randomizer,price=130)

    randomizer = random.randint(50, 150)
    medicine = Medicine.objects.create(medicine="LC Vit Multivitamins Syrup", med_type="Vitamins", uom="mL", price=149, dose=60)

    randomizer = random.randint(50, 150)
    Medicine.objects.create(medicine="Broncure", med_type="Bottle", uom="mL", price=220, dose=90)

    randomizer = random.randint(50, 150)
    Medicine.objects.create(medicine="Refamol", med_type="Capsule", uom="mg", price=32.05,dose=50)

    randomizer = random.randint(50, 150)
    Medicine.objects.create(medicine="Parvo Aid", med_type="Tablet", uom="mg", price=25.66, dose=25)

    randomizer = random.randint(50, 150)
    Medicine.objects.create(medicine="Papi Doxy", med_type="Bottle", uom="mL", price=173, dose=80)

    randomizer = random.randint(30, 100)
    grooming_kit = Miscellaneous.objects.create(miscellaneous="Grooming Kit", misc_type="Kennel Supply", uom="pc",
                                                quantity=randomizer, price=321.12)
    randomizer = random.randint(30, 100)
    first_aid_kit = Miscellaneous.objects.create(miscellaneous="First Aid Kit", misc_type="Kennel Supply", uom="pc",
                                                 quantity=randomizer, price=211.12)
    randomizer = random.randint(30, 100)
    oral_dextrose = Miscellaneous.objects.create(miscellaneous="Oral Dextrose", misc_type="Kennel Supply", uom="pc",
                                                 quantity=randomizer, price=140.12)
    randomizer = random.randint(30, 100)
    ball = Miscellaneous.objects.create(miscellaneous="Ball", misc_type="Kennel Supply", uom="pc",
                                        quantity=randomizer, price=260.33)

    # Create Mandatory Vaccine and Prevention
    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='Rabies Immune Globulin', med_type='Vaccine', immunization='Anti-Rabies',
                            price=randomizer)

    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='Bronchicine CAe', med_type='Vaccine',
                            immunization='Bordetella Bronchiseptica Bacterin', price=randomizer)

    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='VANGUARD PLUS 5 L4 CV', med_type='Vaccine', immunization='DHPPiL+CV',
                            price=randomizer)

    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='Versican Plus DHPPi/L4', med_type='Vaccine', immunization='DHPPiL4',
                            price=randomizer)

    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='PetArmor Sure Shot 2x', med_type='Preventive', immunization='Deworming',
                            price=randomizer)

    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='Heartgard', med_type='Preventive', immunization='Heartworm', price=randomizer)
    randomizer = random.randint(100, 1000)

    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='Frontline', med_type='Preventive', immunization='Tick and Flea', price=randomizer)

    #VET SUPPLY
    randomizer = random.randint(100, 1000)
    Miscellaneous.objects.create(miscellaneous='Adhesive Bandage',uom='pack', misc_type='Vet Supply', price=randomizer)

    randomizer = random.randint(100, 1000)
    Miscellaneous.objects.create(miscellaneous='Face Mask',uom='pack', misc_type='Vet Supply', price=randomizer)

    randomizer = random.randint(500, 800)
    Miscellaneous.objects.create(miscellaneous='Cotton Gauze Dressing',uom='pack', misc_type='Vet Supply',price=randomizer)

    randomizer = random.randint(300, 600)
    Miscellaneous.objects.create(miscellaneous='Medical Gloves',uom='box', misc_type='Vet Supply', price=randomizer)

    randomizer = random.randint(800, 1200)
    Miscellaneous.objects.create(miscellaneous='Surgical Suture',uom='box', misc_type='Vet Supply', price=randomizer)

    randomizer = random.randint(300, 800)
    Miscellaneous.objects.create(miscellaneous='Injection Syringe',uom='pc', misc_type='Vet Supply', price=randomizer)

    randomizer = random.randint(500, 1200)
    Miscellaneous.objects.create(miscellaneous='EDTA K2 K3 Blood Tube',uom='tube', misc_type='Vet Supply',price=randomizer)

    print("Generated inventory items")
    return None

# START CREATE SUPPLIERS
def create_supplier():
    fake = Faker()
    for x in range(12):
        contact = "+63" + fake.msisdn()[:10]
        sup = K9_Supplier.objects.create(name=fake.name(), organization=fake.company(), address=fake.address(),contact_no=contact)
        print('K9 SUPPLIER - ', sup)

def create_teams():
    fake = Faker()
    CITY = (
        ('Alaminos', 'Alaminos'),
        # ('Angeles', 'Angeles'),
        ('Antipolo', 'Antipolo'),
        ('Bacolod', 'Bacolod'),
        ('Bacoor', 'Bacoor'),
        # ('Bago', 'Bago'),
        ('Baguio', 'Baguio'),
        # ('Bais', 'Bais'),
        # ('Balanga', 'Balanga'),
        ('Batac', 'Batac'),
        ('Batangas', 'Batangas'),
        # ('Bayawan', 'Bayawan'),
        # ('Baybay', 'Baybay'),
        # ('Bayugan', 'Bayugan'),
        ('Biñan', 'Biñan'),
        ('Bislig', 'Bislig'),
        # ('Bogo', 'Bogo'),
        # ('Borongan', 'Borongan'),
        ('Butuan', 'Butuan'),
        # ('Cabadbaran', 'Cabadbaran'),
        ('Cabanatuan', 'Cabanatuan'),
        ('Cabuyao', 'Cabuyao'),
        # ('Cadiz', 'Cadiz'),
        ('Cagayan de Oro', 'Cagayan de Oro'),
        ('Calamba', 'Calamba'),
        ('Calapan', 'Calapan'),
        # ('Calbayog', 'Calbayog'),
        ('Caloocan', 'Caloocan'),
        ('Candon', 'Candon'),
        ('Canlaon', 'Canlaon'),
        ('Carcar', 'Carcar'),
        ('Catbalogan', 'Catbalogan'),
        # ('Cauayan', 'Cauayan'),
        ('Cavite', 'Cavite'),
        ('Cebu', 'Cebu'),
        ('Cotabato', 'Cotabato'),
        ('Dagupan', 'Dagupan'),
        ('Danao', 'Danao'),
        ('Dapitan', 'Dapitan'),
        ('Dasmariñas', 'Dasmariñas'),
        ('Davao', 'Davao'),
        # ('Digos', 'Digos'),
        ('Dipolog', 'Dipolog'),
        ('Dumaguete', 'Dumaguete'),
        # ('El Salvador', 'El Salvador'),
        # ('Escalante', 'Escalante'),
        # ('Gapan', 'Gapan'),
        ('General Santos', 'General Santos'),
        ('General Trias', 'General Trias'),
        # ('Gingoog', 'Gingoog'),
        # ('Guihulngan', 'Guihulngan'),
        ('Himamaylan', 'Himamaylan'),
        ('Iligan', 'Iligan'),
        ('Iloilo', 'Iloilo'),
        ('Imus', 'Imus'),
        # ('Iriga', 'Iriga'),
        ('Isabela', 'Isabela'),
        # ('Kabankalan', 'Kabankalan'),
        ('Kidapawan', 'Kidapawan'),
        ('Koronadal', 'Koronadal'),
        ('La Carlota', 'La Carlota'),
        # ('Lamitan', 'Lamitan'),
        ('Laoag', 'Laoag'),
        # ('Lapu‑Lapu', 'Lapu‑Lapu'),
        ('Las Piñas', 'Las Piñas'),
        ('Legazpi', 'Legazpi'),
        # ('Ligao', 'Ligao'),
        ('Lipa', 'Lipa'),
        ('Lucena', 'Lucena'),
        # ('Maasin', 'Maasin'),
        # ('Mabalacat', 'Mabalacat'),
        ('Makati', 'Makati'),
        ('Malabon', 'Malabon'),
        # ('Malaybalay', 'Malaybalay'),
        ('Malolos', 'Malolos'),
        ('Mandaluyong', 'Mandaluyong'),
        # ('Mandaue', 'Mandaue'),
        ('Manila', 'Manila'),
        ('Marawi', 'Marawi'),
        ('Marikina', 'Marikina'),
        ('Masbate', 'Masbate'),
        # ('Mati', 'Mati'),
        # ('Meycauayan', 'Meycauayan'),
        ('Muñoz', 'Muñoz'),
        ('Muntinlupa', 'Muntinlupa'),
        # ('Naga - Camarines Sur', 'Naga - Camarines Sur'),
        # ('Naga - Cebu', 'Naga - Cebu'),
        ('Navotas', 'Navotas'),
        ('Olongapo', 'Olongapo'),
        # ('Ormoc', 'Ormoc'),
        # ('Oroquieta', 'Oroquieta'),
        ('Ozamiz', 'Ozamiz'),
        ('Pagadian', 'Pagadian'),
        ('Palayan', 'Palayan'),
        ('Panabo', 'Panabo'),
        ('Parañaque', 'Parañaque'),
        ('Pasay', 'Pasay'),
        ('Pasig', 'Pasig'),
        # ('Passi', 'Passi'),
        ('Puerto Princesa', 'Puerto Princesa'),
        ('Quezon', 'Quezon'),
        ('Roxas', 'Roxas'),
        # ('Sagay', 'Sagay'),
        # ('Samal', 'Samal'),
        # ('San Carlos - Negros Occidental', 'San Carlos - Negros Occidental'),
        # ('San Carlos - Pangasinan', 'San Carlos - Pangasinan'),
        # ('San Fernando - La Union', 'San Fernando - La Union'),
        # ('San Fernando - Pampanga', 'San Fernando - Pampanga'),
        ('San Jose', 'San Jose'),
        # ('San Jose del Monte', 'San Jose del Monte'),
        ('San Juan', 'San Juan'),
        ('San Pablo', 'San Pablo'),
        ('San Pedro', 'San Pedro'),
        ('Santa Rosa', 'Santa Rosa'),
        ('Santiago', 'Santiago'),
        # ('Silay', 'Silay'),
        ('Sipalay', 'Sipalay'),
        ('Sorsogon', 'Sorsogon'),
        ('Surigao', 'Surigao'),
        ('Tabaco', 'Tabaco'),
        # ('Tabuk', 'Tabuk'),
        ('Tacloban', 'Tacloban'),
        # ('Tacurong', 'Tacurong'),
        ('Tagaytay', 'Tagaytay'),
        # ('Tagbilaran', 'Tagbilaran'),
        ('Taguig', 'Taguig'),
        ('Tagum', 'Tagum'),
        ('Talisay - Cebu', 'Talisay - Cebu'),
        # ('Talisay - Negros Occidental', 'Talisay - Negros Occidental'),
        ('Tanauan', 'Tanauan'),
        # ('Tandag', 'Tandag'),
        # ('Tangub', 'Tangub'),
        # ('Tanjay', 'Tanjay'),
        ('Tarlac', 'Tarlac'),
        ('Tayabas', 'Tayabas'),
        ('Toledo', 'Toledo'),
        ('Trece Martires', 'Trece Martires'),
        ('Tuguegarao', 'Tuguegarao'),
        ('Urdaneta', 'Urdaneta'),
        ('Valencia', 'Valencia'),
        ('Valenzuela', 'Valenzuela'),
        ('Victorias', 'Victorias'),
        ('Vigan', 'Vigan'),
        ('Zamboanga', 'Zamboanga')
    )

    #create areas
    areas = ["National Capital Region", "Ilocos Region", "Cordillera Administrative Region", "Cagayan Valley",
             "Central Luzon",
             "Southern Tagalog Mainland", "Southwestern Tagalog Region", "Bicol Region", "Western Visayas",
             "Central Visayas", "Eastern Visayas",
             "Zamboanga Peninsula", "Northern Mindanao", "Davao Region", "SOCCSKSARGEN", "Caraga Region",
             "Bangsamoro Autonomous Region"]

    for item in areas:
        area = Area.objects.create(name=item)
        area.save()
        print("Area Generated : " + str(area))

    area_list = []
    for area in Area.objects.all():
        area_list.append(area)

    commanders = User.objects.filter(position="Commander")

    commander_list = []
    for commander in commanders:
        commander_list.append(commander)

    commander_list = random.sample(commander_list, len(commander_list) - 1)

    partnership = zip(commander_list, area_list)

    for item in partnership:
        area = item[1]
        area.commander = item[0]
        area.save()
        print("Assigned " + str(item[0]) + " to " + str(item[1]))

    for item in CITY:
        place = fake.address() + " port"

        randomizer = random.randint(0, len(area_list) - 1)
        area = area_list[randomizer]

        lat = random.uniform(7.823, 18.579)
        lng = random.uniform(118.975, 125.563)

        # Create location
        location = Location.objects.create(area = area, place = place, city = item[0], latitude = lat, longtitude = lng)
        location.save()
        # Create team
        team = Team_Assignment.objects.create(location = location)
        team.save()
        print("Generated " + str(team))

    return None

# END DEPLOYMENT NECESSITIES

# START USER CREATION
def generate_user():
    fake = Faker()

    RANK = (
        ('MCPO', 'MCPO'),
        ('SCPO', 'SCPO'),
        ('CPO', 'CPO'),
        ('PO1', 'PO1'),
        ('PO2', 'PO2'),
        ('PO3', 'PO3'),
        ('SN1/SW1', 'SN1/SW1'),
        ('SN2/SW2', 'SN2/SW2'),
        ('ASN/ASW', 'ASN/ASW'),
    )

    BLOODTYPE = (
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O')
    )

    RELIGION = (
        ('Roman Catholic', 'Roman Catholic'),
        ('Christianity', 'Christianity'),
        ('Islam', 'Islam'),
        ('Iglesia ni Cristo', 'Iglesia ni Cristo'),
        ('Buddhist', 'Buddhist'),
    )

    SKINCOLOR = (
        ('Light', 'Light'),
        ('Dark', 'Dark'),
        ('Yellow', 'Yellow'),
        ('Brown', 'Brown')
    )

    ctr = 0
    for x in range(0, 500):

        position = ""

        if ctr <= 429:
            position = "Handler"
        elif ctr >= 430 and ctr <= 460:
            position = "Commander"
        elif ctr >= 461 and ctr <= 479:
            position = "Veterinarian"
        elif ctr == 480 or ctr == 481:
            position = "Operations"
        elif ctr >= 482 and ctr <= 485:
            position = "Trainer"
        else:
            position = 'Administrator'

        randomizer = random.randint(0, 8)
        rank = RANK[randomizer][0]

        randomizer = random.randint(0, 1)

        gender = "?"
        first_name = "?"
        if randomizer == 0:
            first_name = fake.first_name_male()
            gender = "Male"
        else:
            first_name = fake.first_name_female()
            gender = "Female"

        last_name = fake.last_name()

        generated_date = fake.date_between(start_date="-30y", end_date="-20y")
        birthdate = generated_date.strftime("%m/%d/%Y")
        birthplace = fake.address()

        randomizer = random.randint(0, 3)
        blood_type = BLOODTYPE[randomizer][0]
        randomizer = random.randint(0, 4)
        religion = RELIGION[randomizer][0]

        randomizer = random.randint(0, 1)

        civil_status = "?"
        if randomizer == 0:
            civil_status = "Single"
        else:
            civil_status = "Married"

        randomizer = random.randint(0, 3)
        skin_color = SKINCOLOR[randomizer][0]
        eye_color = fake.safe_color_name()
        hair_color = fake.safe_color_name()

        username = first_name + last_name
        username = username.lower()
        email = username + "@gmail.com"

        # Create Users
        user = User.objects.create(rank = rank, firstname = first_name, lastname = last_name, middlename = "", nickname = "", birthdate = generated_date, birthplace = birthplace, gender = gender,
                                   civilstatus = civil_status, citizenship = "Filipino", religion = religion, bloodtype = blood_type, haircolor = hair_color, eyecolor = eye_color, skincolor = skin_color,
                                   position = position)
        user.save()

        cellnum = fake.msisdn()[:10]
        phonenum = fake.msisdn()[:7]

        father = fake.first_name_male() + " " + last_name
        mother_birth = fake.date_between(start_date="-30y", end_date="-20y")
        mother = fake.first_name_female() + " " + last_name
        father_birth = fake.date_between(start_date="-30y", end_date="-20y")

        street = fake.street_name() + " St."
        brngy = "Brngy. " + fake.street_name()
        city = generate_city_ph()
        province = "x province"

        tin = fake.msisdn()[:7]
        phil = fake.msisdn()[:7]

        # Create Personal Information
        personal = Personal_Info.objects.create(UserID=user, mobile_number=cellnum, tel_number=phonenum, street=street,
                                                barangay=brngy, city=city, province=province,
                                                mother_name=mother, father_name=father, mother_birthdate=mother_birth,
                                                father_birthdate=father_birth, tin=tin, philhealth=phil)
        personal.save()

        # Create Education
        education = Education.objects.create(UserID = user, primary_education = "", secondary_education = "", tertiary_education = "", pe_schoolyear = "", se_schoolyear = "", te_schoolyear = "",
                                             pe_degree = "", se_degree = "", te_degree = "")
        education.save()
        serial_number = "O-" + str(user.id)
        # account = Account.objects.create(UserID = user, email_address = email, password = "zaq12wsx")
        # account.serial_number = "O-" + str(account.id)
        # account.save()
        AuthUser.objects.create_user(username=serial_number,
                                     email=email,
                                     password="zaq12wsx")
        #AuthUser.save()
        ctr += 1
        print("Generated " + str(ctr) + " out of 500 users")
    return None

# END USER CREATION

# START K9 CREATION
def generate_k9():
    fake = Faker()

    COLOR = (
        ('Black', 'Black'),
        ('Chocolate', 'Chocolate'),
        ('Yellow', 'Yellow'),
        ('Dark Golden', 'Dark Golden'),
        ('Light Golden', 'Light Golden'),
        ('Cream', 'Cream'),
        ('Golden', 'Golden'),
        ('Brindle', 'Brindle'),
        ('Silver Brindle', 'Silver Brindle'),
        ('Gold Brindle', 'Gold Brindle'),
        ('Salt and Pepper', 'Salt and Pepper'),
        ('Gray Brindle', 'Gray Brindle'),
        ('Blue and Gray', 'Blue and Gray'),
        ('Tan', 'Tan'),
        ('Black-Tipped Fawn', 'Black-Tipped Fawn'),
        ('Mahogany', 'Mahogany'),
        ('White', 'White'),
        ('Black and White', 'Black and White'),
        ('White and Tan', 'White and Tan')
    )

    BREED = (
        ('Belgian Malinois', 'Belgian Malinois'),
        ('Dutch Sheperd', 'Dutch Sheperd'),
        ('German Sheperd', 'German Sheperd'),
        ('Golden Retriever', 'Golden Retriever'),
        ('Jack Russel', 'Jack Russel'),
        ('Labrador Retriever', 'Labrador Retriever'),
    )

    SKILL = (
        ('NDD', 'NDD'),
        ('EDD', 'EDD'),
        ('SAR', 'SAR')
    )

    GRADE = (
        # ("0", "0"),
        ("75", "75"),
        ("80", "80"),
        ("85", "85"),
        ("90", "90"),
        ("95", "95"),
        ("100", "100"),
    )

    suppliers = K9_Supplier.objects.all()
    # END CREATE SUPPLIERS

    # START CREATE PROCURED K9S
    # Initial K9 Count = 500
    idx = 0
    for x in range (0, 500):
        randomizer = random.randint(0, 1)
        name = "?"
        gender = "?"
        if randomizer == 0:
            name = fake.first_name_male()
            gender = "Male"
        else:
            name = fake.first_name_female()
            gender = "Female"

        randomizer = random.randint(0, 18)
        color = COLOR[randomizer][0]
        randomizer = random.randint(0, 5)
        breed = BREED[randomizer][0]

        generated_date = fake.date_between(start_date="-2y", end_date="-2y")
        # date_time = generated_date.strftime("%m/%d/%Y")

        # Create procured k9s
        k9 = K9.objects.create(name = name, breed = breed, sex = gender, color = color, birth_date = generated_date, source = "Procurement", training_status = "Unclassified")
        k9.save()

        if k9.source == "Procurement":
            #TODO
            #CREATE VACCINE YEARLY RECORD HERE
            vr = VaccinceRecord.objects.filter(k9=k9).last()

            VaccineUsed.objects.create(k9=k9,disease='DHPPiL4',date_vaccinated=fake.date_between(start_date="-2y", end_date="now"),done=True)

            VaccineUsed.objects.create(k9=k9,disease='Anti-Rabies',date_vaccinated=fake.date_between(start_date="-2y", end_date="-2y"),done=True)

            VaccineUsed.objects.create(k9=k9,disease='Deworming',date_vaccinated=fake.date_between(start_date="-2y", end_date="-2y"),done=True)

            VaccineUsed.objects.create(k9=k9,disease='Bordetella',date_vaccinated=fake.date_between(start_date="-2y", end_date="-2y"),done=True)

            try:
                randomizer = random.randint(0, suppliers.count() - 1)
                supplier = K9_Supplier.objects.get(id = randomizer)
                k9.supplier = supplier
                k9.save()
            except:
                pass
        idx += 1
        print("Generated " + str(idx) + " out of 500 procured k9s")
    # END CREATE PROCURED K9S

    # START ASSIGN CAPABILITY
    k9s = K9.objects.all()
    k9_list = []
    for k9 in k9s:
        k9_list.append(k9)

    # 90% of k9s will be assigned a capability
    classified_k9_sample = random.sample(k9_list, int(len(k9_list) * .95))

    # Assign Capability
    for k9 in classified_k9_sample:
        randomizer = random.randint(0, 2)
        k9.capability = SKILL[randomizer][0]
        k9.training_status = "Classified"
        k9.save()
        print("Assigned capability " + str(SKILL[randomizer][0]) + " to " + str(k9))
    # END ASSIGN CAPABILITY

    # START ASSIGN HANDLER
    users = User.objects.filter(position="Handler")

    user_id_list = []
    for user in users:
        user_id_list.append(user.id)

    partnership_k9_sample = random.sample(classified_k9_sample, int(len(classified_k9_sample) * .80))
    if len(partnership_k9_sample) < len(user_id_list):
        user_sample = random.sample(user_id_list, len(partnership_k9_sample))  # user sample now have the same length as k9 sample (possible issue here if classified k9s are more than handlers)
    else:
        user_sample = user_id_list

    partnership = zip(partnership_k9_sample, user_sample)

    for item in partnership:
        k9 = K9.objects.get(id=item[0].id)
        user = User.objects.get(id=item[1])

        k9.handler = user
        k9.training_status = 'On-Training'
        k9.save()

        user.partnered = True
        user.save()
        Handler_K9_History.objects.create(handler=user,k9=k9)
        print("Assigned Handler " + str(user) + " to " + str(k9))
    # END ASSIGN HANDLER

    # START CREATE TRAINING
    training_k9 = K9.objects.filter(training_status = 'On-Training')
    training_k9_list = []
    for k9 in training_k9:
        training_k9_list.append(k9)

    training_k9_sample = random.sample(training_k9_list, int(len(training_k9_list) * .80))

    for k9 in training_k9_sample:
        # #create training history
        fake_date = fake.date_between(start_date='-5y', end_date='today')
        Training_History.objects.create(k9=k9,handler=k9.handler,date=fake_date)

        birthdate = k9.birth_date

        training_start_alpha = datetime.combine(birthdate, datetime.min.time())
        training_start_alpha = training_start_alpha + timedelta(days=365)
        try:
            training = Training.objects.filter(k9 = k9).get(training = k9.capability)

            remark = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)
        except:
            pass
        #
        #     train_sched = Training_Schedule.objects.filter(k9 = k9).last() #Because we have 1 instance of this per k9 instance at the start
        #     train_sched.date_start = training_start_alpha
        #     train_sched.date_end = training_start_alpha + timedelta(days=20)
        #
        #     grade_list = []
        #     stage = "Stage 0"
        #     for idx in range(9):
        #         randomizer = random.randint(0, 5)
        #         grade = GRADE[randomizer][0]
        #         grade_list.append(grade)
        #
        #         if idx == 0:
        #             stage = "Stage 1.1"
        #         elif idx == 1:
        #             stage = "Stage 1.2"
        #         elif idx == 2:
        #             stage = "Stage 1.3"
        #         elif idx == 3:
        #             stage = "Stage 2.1"
        #         elif idx == 4:
        #             stage = "Stage 2.2"
        #         elif idx == 5:
        #             stage = "Stage 2.3"
        #         elif idx == 6:
        #             stage = "Stage 3.1"
        #         elif idx == 7:
        #             stage = "Stage 3.2"
        #         elif idx == 8:
        #             stage = "Stage 3.3"
        #
        #         # if exclude_k9 == False and idx != 8:
        #         sched_remark = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)
        #         train_sched = Training_Schedule.objects.create(k9 = k9, date_start = training_start_alpha + timedelta(days=20 * idx + 1),
        #                                                             date_end = training_start_alpha + timedelta(days=20 * idx + 2), stage = stage, remarks = sched_remark)
        #         # train_sched.save()
        #
        #     training.stage1_1 = grade_list[0]
        #     training.stage1_2 = grade_list[1]
        #     training.stage1_3 = grade_list[2]
        #
        #     training.stage2_1 = grade_list[3]
        #     training.stage2_2 = grade_list[4]
        #     training.stage2_3 = grade_list[5]
        #
        #     training.stage3_1 = grade_list[6]
        #     training.stage3_2 = grade_list[7]
        #     training.stage3_3 = grade_list[8]
        #
        #     start_date = datetime(2019, 1, 1)
        #     end_date = datetime(2019, 12, 31)
        #     f_date = fake.date_between(start_date=start_date, end_date=end_date)
        #
        #     # if exclude_k9 == False:
        #
        #     training.stage = "Finished Training"
        #     training.date_finished = f_date
        #
        #     k9.training_status = 'Trained'
        #     k9.training_level = "Finished Training"
        #     k9.serial_number = 'SN-' + str(k9.id) + '-' + str(datetime.now().year)
        #     k9.trained = "Trained"
        #     k9.save()
        #     # else:
        #     #     training.stage = "Stage 3.2"

        train_sched = Training_Schedule.objects.filter(k9=k9).filter(stage='Stage 0').last() #Because we have 1 instance of this per k9 instance
        train_sched.date_start = training_start_alpha
        train_sched.date_end = training_start_alpha + timedelta(days=20)

        train_sched.remarks = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)
        train_sched.save()

        grade_list = ['75','80','85','90','95','100']
        training.stage1_1 = random.choice(grade_list)
        training.stage1_2 = random.choice(grade_list)
        training.stage1_3 = random.choice(grade_list)

        training.stage2_1 = random.choice(grade_list)
        training.stage2_2 = random.choice(grade_list)
        training.stage2_3 = random.choice(grade_list)

        training.stage3_1 = random.choice(grade_list)
        training.stage3_2 = random.choice(grade_list)
        training.stage3_3 = random.choice(grade_list)

        training.remarks = remark
        training.stage = "Finished Training"

        stage = "Stage 0"
        for idx in range(8):
            # randomizer = random.randint(0, 5)
            # grade = GRADE[randomizer][0]
            # grade_list.append(grade)

            if idx == 0:
                stage = "Stage 1.1"
            elif idx == 1:
                stage = "Stage 1.2"
            elif idx == 2:
                stage = "Stage 1.3"
            elif idx == 3:
                stage = "Stage 2.1"
            elif idx == 4:
                stage = "Stage 2.2"
            elif idx == 5:
                stage = "Stage 2.3"
            elif idx == 6:
                stage = "Stage 3.1"
            elif idx == 7:
                stage = "Stage 3.2"


            dur = random.randint(20,40)
            sched_remark = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)
            train_sched = Training_Schedule.objects.create(k9 = k9, date_start = training_start_alpha + timedelta(days=dur),date_end = training_start_alpha + timedelta(days=dur), stage = stage, remarks = sched_remark)
            # train_sched.save()

        # start_date = datetime(2019,1,1)
        # end_date = datetime(2019,12,31)
        # f_date = fake.date_between(start_date=start_date, end_date=end_date)

        f_date = Training_Schedule.objects.filter(k9 = k9).last()
        training.date_finished = f_date.date_end
        training.save()

        k9.training_status = 'Trained'
        k9.training_level = "Finished Training"
        k9.trained = "Trained"
        k9.save()
        print("Created Training for " + str(k9))

    # END CREATE TRAINING

    # START BREEDING_or_DEPLOYMENT
    trained_k9s = K9.objects.filter(training_status="Trained").filter(training_level="Finished Training")
    k9_id_list = []
    for k9 in trained_k9s:
        k9_id_list.append(k9.id)
    for_breeding_k9_sample = random.sample(k9_id_list, int(len(k9_id_list) * .90))  # 90% of all trained k9s
    for_deployment_k9_sample = random.sample(for_breeding_k9_sample, int(len(for_breeding_k9_sample) * .90))  # 90% of all breeding k9s

    for id in for_deployment_k9_sample:
        try:
            for_breeding_k9_sample.remove(id)
        except:
            pass

    for id in for_deployment_k9_sample:
        try:
            k9 = K9.objects.get(id=id)
            k9.training_status = "For-Deployment"
            k9.status = "Working Dog"
            sn = 'SN-' + str(k9.id) + '-' + str(datetime.now().year)
            k9.serial_number = sn
            k9.birth_date = k9.birth_date - timedelta(days = 2190)
            k9.save()
            print(str(k9) + " is now For-Deployment")
        except:
            pass

    for id in for_breeding_k9_sample:
        #For BREEDING age is now 6yrs old
        try:
            k9 = K9.objects.get(id=id)
            k9.training_status = "For-Breeding"
            k9.status = "Working Dog"
            handler = User.objects.filter(id=k9.handler.id).last()
            k9.handler = None
            handler.partnered = False
            handler.save()
            k9.birth_date = fake.date_between(start_date="-6y", end_date="-6y")
            sn = 'SN-' + str(k9.id) + '-' + str(datetime.now().year)
            k9.serial_number = sn
            k9.save()
            print(str(k9) + " is now For-Breeding")
        except:
            pass
    # END BREEDING_or_DEPLOYMENT

    #START CREATE PRE DEPLOYMENT SCHEDULES
    for_deployment_k9s = K9.objects.filter(training_status = "For-Deployment").filter(status = "Working Dog")
    k9_list = []
    for k9 in  for_deployment_k9s:
        k9_list.append(k9)
    for_deployment_k9_sample = random.sample(k9_list, int(len(k9_list) * .70))

    team_assign = Team_Assignment.objects.all()

    sublist_for_deployment_k9_sample = [for_deployment_k9_sample[i:i+3] for i in range(0, len(for_deployment_k9_sample), 3)]
    vets = User.objects.filter(position="Veterinarian")
    vet_list = []
    for vet in vets:
        vet_list.append(vet)

    idx = 0
    for team in team_assign:
        if idx < len(sublist_for_deployment_k9_sample) - 1:
            sublist = sublist_for_deployment_k9_sample[idx]
            randomizer = random.randint(1, 45)
            gen_birthdate = fake.date_between(start_date="-2y", end_date="-2y")
            deployment_date = gen_birthdate + timedelta(days=495 + randomizer)

            for k9 in sublist:
                deploy = K9_Schedule.objects.create(team=team, k9=k9, status="Initial Deployment",
                                                   date_start=deployment_date)
                K9_Schedule.objects.create(team=team, k9=k9, status="Checkup",
                                           date_start=deployment_date - timedelta(days=7))
                K9_Pre_Deployment_Items.objects.create(k9=k9, initial_sched=deploy, status="Done")
                Team_Dog_Deployed.objects.create(team_assignment=team, k9=k9,
                                                          date_added=deployment_date + timedelta(days=random.randint(1, 6)))
                randomizer = random.randint(0, len(vet_list) - 1)
                PhysicalExam.objects.create(dog = k9, veterinary = vet_list[randomizer], heart_rate = 32, respiratory_rate = 32, temperature = 32, weight = 32, cleared = True)

                if k9.capability == "SAR":
                    team.SAR_deployed += 1
                elif k9.capability == "NDD":
                    team.NDD_deployed += 1
                elif k9.capability == "EDD":
                    team.EDD_deployed += 1
                team.save()
                k9.training_status = 'Deployed'
                k9.status = 'Working Dog'
                k9.assignment = team.team
                k9.training_status = "Deployed"
                handler = k9.handler
                handler.assigned = True
                handler.save()
                k9.save()
                print(str(k9) + " is deployed to " + str(team))

            assign_TL(team)
            idx += 1
        else:
            break


    #END PRE DEPLOYMENT SCHEDULES

    return None
# END K9 CREATION

# START MISC

def generate_requests():
    fake = Faker()

    pre_titles = ['An Evening of ', 'A Night to Celebrate ', 'A Celebration of Life and ', 'The Wonders of '
                  , 'In Observance of ', 'In Recognition of ', 'In Commemoration of ', 'Meetup for '
                  , 'The Future of ', 'The Technology of ', 'A Date with ']
    post_titles = [' Conference', ' Con', ' Competition', ' Hackathon', ' Fundraiser', ' Charity', ' Party'
                   , ' Bash', ' Ball', ' Gala', ' Shindig', 'athon', ' Celebration', ' Affair'
                   , ' Ceremony', ' Awards', ' Event of the Year!', ' Jubilee', ' Performance', ' Blast'
                   , ' Blowout', ' Rite', ' Show', ' Meetup', ' for Health', ' Workshop', ' Research Event'
                   , ' Summit', ' Course', ' Symposium', ' Town Hall Meeting', ' Games', ' Expo', ': The Event']

    location_list = []
    for location in Location.objects.all():
        location_list.append(location)

    area_list = []
    for area in Area.objects.all():
        area_list.append(area)

    for x in range(0, 80):
        requester = fake.company()
        cell = "+63" + fake.msisdn()[:10]

        randomizer = random.randint(0, 1)

        event_type = "?"
        k9s_required = 0
        status = "Pending"
        if randomizer == 0:
            event_type = "Big Event"
            k9s_required = random.randint(5, 10)
            status = "Approved"

        else:
            event_type = "Small Event"
            k9s_required = random.randint(2, 4)

        location = fake.address()
        city = generate_city_ph()

        lat = random.uniform(7.823, 18.579)
        lng = random.uniform(118.975, 125.563)

        start_date = fake.date_between(start_date="+10d", end_date="+60d")
        end_date = start_date + timedelta(days=random.randint(1, 14))

        remarks = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)
        event_name = fake.word()

        randomizer = random.randint(0, 1)

        if randomizer == 0:
            randomizer = random.randint(0, len(pre_titles) - 1)
            event_name = str(pre_titles[randomizer]) + event_name.capitalize()
        else:
            randomizer = random.randint(0, len(post_titles) - 1)
            event_name = event_name.capitalize() + str(post_titles[randomizer])

        email = requester.lower() + "@gmail.com"

        randomizer = random.randint(0, len(area_list) - 1)
        area = area_list[randomizer]

        request = Dog_Request.objects.create(requester=requester, location=location, city=city, sector_type=event_type,
                                             phone_number=cell, email_address=email, event_name=event_name,
                                             remarks=remarks, area=area, k9s_needed=k9s_required, start_date=start_date,
                                             end_date=end_date, latitude=lat, longtitude=lng, status = status)
        request.save()
        print("Event: " + event_name + ". " + str(x) + "/150 events")

        if request.sector_type == "Big Event":
            request.status = "Approved"
            request.save()

    return None

def generate_maritime():
    fake = Faker()
    for x in range(0, 100):
        BOAT_TYPE = (
            ('Domestice Passenger Vessels', 'Domestice Passenger Vessels'),
            ('Motorbancas', 'Motorbancas'),
            ('Fastcrafts', 'Fastcrafts'),
            ('Cruise Ships', 'Cruise Ships'),
            ('Tugboat', 'Tugboat'),
            ('Barge', 'Barge'),
            ('Tanker', 'Tanker')
        )

        location_list = []
        for location in Location.objects.all():
            location_list.append(location)

        randomizer = random.randint(0, len(location_list) - 1)
        location = location_list[randomizer]
        print("Location : " + str(location))

        randomizer = random.randint(0, len(BOAT_TYPE) - 1)
        boat_type = BOAT_TYPE[randomizer][0]
        print("Boat type : " + boat_type)

        date = fake.date_between(start_date="-10y", end_date="-5y")

        time = fake.time_object(end_datetime=None)

        # TODO Generate Time

        passenger_count = random.randint(20, 100)

        maritime = Maritime.objects.create(location = location, boat_type = boat_type, date = date, time = time, passenger_count = passenger_count)
        print(str(x) + " out of 100 maritime generated")
    return None


# END MISC

#GENERATE PHYSICAL COUNT, RECEIVED, SUBTRACTED
def generate_inventory_trail():
    fake = Faker()
    admin = User.objects.filter(position='Administrator')
    admin = list(admin) #food received & count by admin

    vet = User.objects.filter(position='Veterinarian')
    vet = list(vet)
    # DATE OF THIS YEAR - 2019
    # FOOD
    food = Food.objects.all()
    #food = Food.objects.filter(foodtype='Milk')
    for data in food:
        #FOOD RECEIVED TRAIL
        for i in range(5):
            start_date = datetime(2019,1,1)
            end_date = datetime(2019,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            choice = random.choice(admin)
            randomizer = random.randint(50, 150)
            new_q = data.quantity+randomizer
            print(data,data.quantity,new_q)
            Food_Received_Trail.objects.create(inventory=data, user=choice,old_quantity=data.quantity, quantity=new_q, date_received=f_date)
            data.quantity = new_q
            data.save()

        #FOOD SUBTRACT TRAIL
        for i in range(3):
            start_date = datetime(2019,1,1)
            end_date = datetime(2019,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            randomizer = random.randint(0, 50)
            new_q = data.quantity-randomizer
            if new_q < 0:
                new_q = 0
            print(data,data.quantity,new_q)
            Food_Subtracted_Trail.objects.create(inventory=data, old_quantity=data.quantity, quantity=new_q,date_subtracted=f_date)
            data.quantity = new_q
            data.save()

        #FOOD PHYSICAL COUNT
        for i in range(3):
            start_date = datetime(2019,1,1)
            end_date = datetime(2019,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            randomizer = random.randint(100, 500)
            choice = random.choice(admin)
            new_q = randomizer
            print(data,data.quantity,new_q)
            Food_Inventory_Count.objects.create(inventory=data, user=choice, old_quantity=data.quantity, quantity=new_q,date_counted=f_date)
            data.quantity = new_q
            data.save()

    # MISC
    misc = Miscellaneous.objects.all()
    for data in misc:
        #MISCELLANEOUS RECEIVED TRAIL
        for i in range(5):
            start_date = datetime(2019,1,1)
            end_date = datetime(2019,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            choice = random.choice(admin)
            randomizer = random.randint(50, 150)
            new_q = data.quantity+randomizer
            print(data,data.quantity,new_q)
            Miscellaneous_Received_Trail.objects.create(inventory=data, user=choice,old_quantity=data.quantity, quantity=new_q, date_received=f_date)
            data.quantity = new_q
            data.save()

        #MISCELLANEOUS SUBTRACT TRAIL
        for i in range(3):
            start_date = datetime(2019,1,1)
            end_date = datetime(2019,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            randomizer = random.randint(0, 50)
            new_q = data.quantity-randomizer
            if new_q < 0:
                new_q = 0
            print(data,data.quantity,new_q)
            Miscellaneous_Subtracted_Trail.objects.create(inventory=data, old_quantity=data.quantity, quantity=new_q,date_subtracted=f_date)
            data.quantity = new_q
            data.save()

        #MISCELLANEOUS PHYSICAL COUNT
        for i in range(3):
            start_date = datetime(2019,1,1)
            end_date = datetime(2019,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            randomizer = random.randint(100, 500)
            choice = random.choice(admin)
            new_q = randomizer
            print(data,data.quantity,new_q)
            Miscellaneous_Inventory_Count.objects.create(inventory=data, user=choice, old_quantity=data.quantity, quantity=new_q,date_counted=f_date)
            data.quantity = new_q
            data.save()

    # MED
    med = Medicine_Inventory.objects.all()
    for data in med:
        #MEDICINE RECEIVED TRAIL
        for i in range(5):
            start_date = datetime(2019,1,1)
            end_date = datetime(2019,12,31)
            exp_date = datetime(2023,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            choice = random.choice(admin)
            randomizer = random.randint(50, 150)
            new_q = data.quantity+randomizer
            print(data,data.quantity,new_q)
            Medicine_Received_Trail.objects.create(inventory=data, user=choice,old_quantity=data.quantity, quantity=new_q, date_received=f_date,expiration_date=exp_date,status='Done')
            data.quantity = new_q
            data.save()

        #MEDICINE SUBTRACT TRAIL
        for i in range(3):
            start_date = datetime(2019,1,1)
            end_date = datetime(2019,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            randomizer = random.randint(0, 50)
            new_q = data.quantity-randomizer
            if new_q < 0:
                new_q = 0
            print(data,data.quantity,new_q)
            Medicine_Subtracted_Trail.objects.create(inventory=data, old_quantity=data.quantity, quantity=new_q,date_subtracted=f_date)
            data.quantity = new_q
            data.save()

        #MEDICINE PHYSICAL COUNT
        for i in range(3):
            start_date = datetime(2019,1,1)
            end_date = datetime(2019,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            randomizer = random.randint(100, 500)
            choice = random.choice(admin)
            new_q = randomizer
            print(data,data.quantity,new_q)
            Medicine_Inventory_Count.objects.create(inventory=data, user=choice, old_quantity=data.quantity, quantity=new_q,date_counted=f_date)
            data.quantity = new_q
            data.save()

    # DATE OF LAST YEAR - 2018
    # FOOD
    food = Food.objects.all()
    for data in food:
        #FOOD RECEIVED TRAIL
        for i in range(5):
            start_date = datetime(2018,1,1)
            end_date = datetime(2018,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            choice = random.choice(admin)
            randomizer = random.randint(50, 150)
            new_q = data.quantity+randomizer
            print(data,data.quantity,new_q)
            Food_Received_Trail.objects.create(inventory=data, user=choice,old_quantity=data.quantity, quantity=new_q, date_received=f_date)
            data.quantity = new_q
            data.save()

        #FOOD SUBTRACT TRAIL
        for i in range(3):
            start_date = datetime(2018,1,1)
            end_date = datetime(2018,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            randomizer = random.randint(0, 50)
            new_q = data.quantity-randomizer
            if new_q < 0:
                new_q = 0
            print(data,data.quantity,new_q)
            Food_Subtracted_Trail.objects.create(inventory=data, old_quantity=data.quantity, quantity=new_q,date_subtracted=f_date)
            data.quantity = new_q
            data.save()

        #FOOD PHYSICAL COUNT
        for i in range(3):
            start_date = datetime(2018,1,1)
            end_date = datetime(2018,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            randomizer = random.randint(100, 500)
            choice = random.choice(admin)
            new_q = randomizer
            print(data,data.quantity,new_q)
            Food_Inventory_Count.objects.create(inventory=data, user=choice, old_quantity=data.quantity, quantity=new_q,date_counted=f_date)
            data.quantity = new_q
            data.save()

    # MISC
    misc = Miscellaneous.objects.all()
    for data in misc:
        #MISCELLANEOUS RECEIVED TRAIL
        for i in range(5):
            start_date = datetime(2018,1,1)
            end_date = datetime(2018,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            choice = random.choice(admin)
            randomizer = random.randint(50, 150)
            new_q = data.quantity+randomizer
            print(data,data.quantity,new_q)
            Miscellaneous_Received_Trail.objects.create(inventory=data, user=choice,old_quantity=data.quantity, quantity=new_q, date_received=f_date)
            data.quantity = new_q
            data.save()

        #MISCELLANEOUS SUBTRACT TRAIL
        for i in range(3):
            start_date = datetime(2018,1,1)
            end_date = datetime(2018,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            randomizer = random.randint(0, 50)
            new_q = data.quantity-randomizer
            if new_q < 0:
                new_q = 0
            print(data,data.quantity,new_q)
            Miscellaneous_Subtracted_Trail.objects.create(inventory=data, old_quantity=data.quantity, quantity=new_q,date_subtracted=f_date)
            data.quantity = new_q
            data.save()

        #MISCELLANEOUS PHYSICAL COUNT
        for i in range(3):
            start_date = datetime(2018,1,1)
            end_date = datetime(2018,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            randomizer = random.randint(100, 500)
            choice = random.choice(admin)
            new_q = randomizer
            print(data,data.quantity,new_q)
            Miscellaneous_Inventory_Count.objects.create(inventory=data, user=choice, old_quantity=data.quantity, quantity=new_q,date_counted=f_date)
            data.quantity = new_q
            data.save()

    # MED
    med = Medicine_Inventory.objects.all()
    for data in med:
        #MEDICINE RECEIVED TRAIL
        for i in range(5):
            start_date = datetime(2018,1,1)
            end_date = datetime(2018,12,31)
            exp_date = datetime(2023,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            choice = random.choice(admin)
            randomizer = random.randint(50, 150)
            new_q = data.quantity+randomizer
            print(data,data.quantity,new_q)
            Medicine_Received_Trail.objects.create(inventory=data, user=choice,old_quantity=data.quantity, quantity=new_q, date_received=f_date,expiration_date=exp_date,status='Done')
            data.quantity = new_q
            data.save()

        #MEDICINE SUBTRACT TRAIL
        for i in range(3):
            start_date = datetime(2018,1,1)
            end_date = datetime(2018,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            randomizer = random.randint(0, 50)
            new_q = data.quantity-randomizer
            if new_q < 0:
                new_q = 0
            print(data,data.quantity,new_q)
            Medicine_Subtracted_Trail.objects.create(inventory=data, old_quantity=data.quantity, quantity=new_q,date_subtracted=f_date)
            data.quantity = new_q
            data.save()

        #MEDICINE PHYSICAL COUNT
        for i in range(3):
            start_date = datetime(2018,1,1)
            end_date = datetime(2018,12,31)
            f_date = fake.date_between(start_date=start_date, end_date=end_date)
            randomizer = random.randint(100, 500)
            choice = random.choice(admin)
            new_q = randomizer
            print(data,data.quantity,new_q)
            Medicine_Inventory_Count.objects.create(inventory=data, user=choice, old_quantity=data.quantity, quantity=new_q,date_counted=f_date)
            data.quantity = new_q
            data.save()

def generate_daily_refresher():
    fake = Faker()
    user = User.objects.filter(position="Handler")
    user = list(user)
    k9 = K9.objects.exclude(serial_number='Unassigned Serial Number')
    k9_list = list(k9)

    k9_sample = random.sample(k9_list, int(len(k9_list) * .15))
    for data in k9_sample:
        handler = random.choice(user)
        for i in range(2):
            start_date = datetime(2019,1,1)
            end_date = datetime(2019,12,31)

            choice = random.choice(k9_list)

            mar = ['MARSEC','MARLEN','MARSAR','MAREP']
            mar = random.choice(mar)

            port_plant = random.randint(1, 3)
            port_find = random.randint(0, port_plant)
            building_plant = random.randint(1, 3)
            building_find = random.randint(0, building_plant)
            vehicle_plant = random.randint(1, 3)
            vehicle_find = random.randint(0, vehicle_plant)
            baggage_plant = random.randint(1, 3)
            baggage_find = random.randint(0, baggage_plant)
            others_plant = random.randint(1, 3)
            others_find = random.randint(0, others_plant)

            port_date = fake.date_time_between(start_date=start_date, end_date="now", tzinfo=None)
            port_hour = int(port_date.time().hour)
            port_date = port_date - timedelta(hours=port_hour)

            port_time = port_date.time()

            building_date = fake.date_time_between(start_date=start_date, end_date="now", tzinfo=None)
            building_hour = int(building_date.time().hour)
            building_date = building_date - timedelta(hours=building_hour)

            building_time = building_date.time()

            vehicle_date = fake.date_time_between(start_date=start_date, end_date="now", tzinfo=None)
            vehicle_hour = int(vehicle_date.time().hour)
            vehicle_date = vehicle_date - timedelta(hours=vehicle_hour)

            vehicle_time = vehicle_date.time()

            baggage_date = fake.date_time_between(start_date=start_date, end_date="now", tzinfo=None)
            baggage_hour = int(baggage_date.time().hour)
            baggage_date = baggage_date - timedelta(hours=baggage_hour)

            baggage_time = baggage_date.time()

            others_date = fake.date_time_between(start_date=start_date, end_date="now", tzinfo=None)
            others_hour = int(others_date.time().hour)
            others_date = others_date - timedelta(hours=others_hour)

            others_time = others_date.time()

            dr = Daily_Refresher.objects.create(k9=choice,handler=handler,date=port_date,morning_feed_cups=2,evening_feed_cups=2,on_leash=True,off_leash=True,obstacle_course=True,panelling=True, mar = mar, port_plant=port_plant, port_find=port_find, port_time=port_time, building_plant=building_plant,  building_find=building_find, building_time=building_time, vehicle_plant=vehicle_plant,  vehicle_find=vehicle_find, vehicle_time=vehicle_time, baggage_plant=baggage_plant,  baggage_find=baggage_find, baggage_time=baggage_time, others_plant=others_plant, others_find=others_find, others_time=others_time)

            print('DR'+str(i), dr.k9, dr.rating)

#LOCATION INCIDENT, MARITIME, DOG REQUEST
def generate_location_incident():
    fake = Faker()
    ta = Team_Assignment.objects.exclude(team_leader=None)
    ta_list = list(ta)
    ta_sample = random.sample(ta_list, int(len(ta_list) * .25))
    user = User.objects.all()
    user_list = list(user)

    incident_type = ['Explosives Related', 'Narcotics Related', 'Search and Rescue Related', 'Others']

    explosive = ['Bombing in Mall', 'Bombing in Airport', 'Bombing at Road', 'Terrorist Bombing']
    narcotics = ['Drug Bust', 'Airport Drug Traffic', 'Drug Trade', 'Drug Use at Mall']
    search = ['Landslide', 'Typhoon', 'Hurricane', 'Kidnapping', 'Arson', 'Earthquake']
    others = ['Attack', 'Bodyguard Duty', 'Security Duty']
    boat = ['Domestice Passenger Vessels', 'Motorbancas', 'Fastcrafts', 'Cruise Ships', 'Tugboat', 'Barge','Tanker']
    event = ['Big Event', 'Small Event']

    pre_titles = ['An Evening of ', 'A Night to Celebrate ', 'A Celebration of Life and ', 'The Wonders of ', 'In Observance of ', 'In Recognition of ', 'In Commemoration of ', 'Meetup for ', 'The Future of ', 'The Technology of ', 'A Date with ']
    post_titles = [' Conference', ' Con', ' Competition', ' Hackathon', ' Fundraiser', ' Charity', ' Party', ' Bash', ' Ball', ' Gala', ' Shindig', 'athon', ' Celebration', ' Affair', ' Ceremony', ' Awards', ' Event of the Year!', ' Jubilee', ' Performance', ' Blast', ' Blowout', ' Rite', ' Show', ' Meetup', ' for Health', ' Workshop', ' Research Event', ' Summit', ' Course', ' Symposium', ' Town Hall Meeting', ' Games', ' Expo', ': The Event']

    loc = []
    tl = []
    for ta in ta:
        if ta.location:
            loc.append(ta.location)
        if ta.team_leader:
            tl.append(ta.team_leader)

    start_date = datetime(2019,1,1)
    end_date = datetime(2019,12,31)

    for data in ta_sample:
        for i in range(10):
            f_date = fake.date_time_between(start_date=start_date, end_date=end_date, tzinfo=None)
            i_type = random.choice(incident_type)
            i_loc = random.choice(loc)
            i_tl = random.choice(tl)
            if i_type == 'Explosives Related':
                i_inc = random.choice(explosive)
                i_rem = 'Explosive Remarks Here'
            elif i_type == 'Narcotics Related':
                i_inc = random.choice(narcotics)
                i_rem = 'Narcotics Remarks Here'
            elif i_type == 'Search and Rescue Related':
                i_inc = random.choice(search)
                i_rem = 'Search and Rescue Remarks Here'
            elif i_type == 'Others':
                i_inc = random.choice(others)
                i_rem = 'Other Remarks Here'

            Incidents.objects.create(user=i_tl,date=f_date.date(),incident=i_inc,location=i_loc,type=i_type,remarks=i_rem)

            m_boat = random.choice(boat)
            p_count = random.randint(50, 150)

            Maritime.objects.create(location=i_loc, boat_type=m_boat, date=f_date.date(), time=f_date.time(), passenger_count=p_count)
            # print(f_date,i_type,i_tl,i_loc,i_inc)

            city = generate_city_ph()
            pre_t = random.choice(pre_titles)
            post_t = random.choice(post_titles)
            e = random.choice(event)
            cellnum = fake.msisdn()[:10]
            u = random.choice(user_list)
            email = u.lastname.lower() + "@gmail.com"
            lat = random.uniform(7.823, 18.579)
            lng = random.uniform(118.975, 125.563)
            needed = random.randint(3, 10)
            deployed = random.randint(1, needed)

            s_date = datetime(2019,1,1)
            e_date = datetime(2019,6,30)

            ss_date = datetime(2019,7,1)
            ee_date = datetime(2019,12,10)

            sf_date = fake.date_between(start_date=start_date, end_date=end_date)
            ef_date = fake.date_between(start_date=start_date, end_date=end_date)

            s_loc = str(i_loc)
            place = s_loc.replace('port', '')
            Dog_Request.objects.create(requester=str(u),event_name=pre_t+post_t,location=place,city=city,sector_type=e,phone_number=cellnum,email_address=email,area=i_loc.area,k9s_needed=needed,k9s_deployed=deployed,status='Done',longtitude=lng,latitude=lat,team_leader=i_tl, start_date=sf_date, end_date=ef_date,remarks='No remarks')

def generate_handler_incident():
    fake = Faker()
    incident = ['Rescued People','Made an Arrest','Poor Performance','Violation']
    ta = Team_Assignment.objects.exclude(team_leader=None)
    k9 = K9.objects.exclude(assignment='None').exclude(handler=None).exclude(serial_number='Unassigned Serial Number')

    k9_list = list(k9)
    k9_sample = random.sample(k9_list, int(len(k9_list) * .10))

    for data in k9_sample:
        for i in range(5):
            start_date = datetime(2019,1,1)
            end_date = datetime(2019,12,31)

            f_date = fake.date_between(start_date=start_date, end_date=end_date)

            inc = random.choice(incident)
            ta_list = random.choice(ta)
            dog = random.choice(k9_sample)

            Handler_Incident.objects.create(handler=dog.handler, k9=dog, incident=inc, date = f_date, description='Description Here', status='Done', reported_by=ta_list.team_leader)

def generate_handler_leave():
    fake = Faker()
    admin = User.objects.filter(position='Administrator')
    admin = list(admin)

    k9 = K9.objects.exclude(assignment='None').exclude(handler=None).exclude(serial_number='Unassigned Serial Number')
    k9_list = list(k9)
    k9_sample = random.sample(k9_list, int(len(k9_list) * .10))

    for data in k9_sample:
        start_date = datetime(2019,1,1)
        end_date = datetime(2019,11,1)

        el = random.randint(1, 8)
        rl = random.randint(1, 8)

        sf_date = fake.date_between(start_date=start_date, end_date=end_date)
        ef_date = sf_date + timedelta(days=rl)
        dog = data
        approver = random.choice(admin)

        # Handler_On_Leave
        Handler_On_Leave.objects.create(handler=dog.handler,approved_by=approver,k9=dog,description='Sick Leave',reply='Okay',status='Approved',date_from=sf_date,date_to=ef_date)

        ssf_date = fake.date_between(start_date=start_date, end_date=end_date)
        eef_date = ssf_date + timedelta(days=el)

        # Emergency_Leave
        Emergency_Leave.objects.create(handler=dog.handler,date_of_leave=ssf_date,date_of_return=eef_date,status='Returned',reason='Family Emergency')

def generate_k9_incident():
    fake = Faker()
    inc = ['Stolen','Lost','Sick','Accident']
    k9 = K9.objects.exclude(assignment='None').exclude(handler=None).exclude(serial_number='Unassigned Serial Number')
    k9_list = list(k9)
    k9_sample = random.sample(k9_list, int(len(k9_list) * .15))

    handler = User.objects.filter(position="Handler")
    handler = list(handler)

    lost = ['Collar not properly put on', 'Leashed on a pole', 'Suddenly disappeared']
    stolen = ['Dognapped', 'Left with a stranger', 'Snatched']

    sick = ['Rashes', 'Red Spots', 'Breathing Heavy', 'Depressed/Low Energy', 'Would not Eat', 'Runny Eyes', 'Vomiting', 'Coughing', 'Fever', 'Weight loss', 'Diarrhea']

    accident = ['Hit by Car', 'Caught in Bomb Explosion', 'Building Fell Down', 'Stab by Unknown Subject','Caught by Gun Fired on Premises']

    clinic = ['Companion Animal Veterinary Clinic','BSF Animal Clinic','Makati Dog & Cat Hospital','Ada Animal Clinics','Animal House','UP Veterinary Teaching Hospital, Diliman Station','Pendragon Veterinary Clinic','Vets in Practice Animal Hospital','The Pet Project Vet Clinic','Pet Society Veterinary Clinic']

    for data in k9_sample:
        k_inc = random.choice(inc)

        start_date = datetime(2019,1,1)
        end_date = datetime(2019,12,10)

        f_date = fake.date_between(start_date=start_date, end_date=end_date)

        if k_inc == 'Stolen':
            k_desc = random.choice(stolen)
        elif k_inc == 'Lost':
            k_desc = random.choice(lost)
        if k_inc == 'Sick':
            k_desc = random.choice(sick)
        elif k_inc == 'Accident':
            k_desc = random.choice(accident)
        if k_inc == 'Stolen' or k_inc == 'Lost':
            K9_Incident.objects.create(k9=data,incident=k_inc,title=str(data)+str(' is ')+k_inc,date=f_date,description=k_desc,status='Done',reported_by=handler)
        else:
            k_clinic = random.choice(clinic)
            K9_Incident.objects.create(k9=data,incident=k_inc,title=str(data)+str(' is ')+k_inc,date=f_date,description=k_desc,status='Done',reported_by=data.handler,clinic=k_clinic)

def generate_health_record():
    fake = Faker()
    time_of_day = ['Morning','Afternoon','Night','Morning/Afternoon','Morning/Night','Afternoon/Night','Morning/Afternoon/Night']

    clinic = ['Companion Animal Veterinary Clinic','BSF Animal Clinic','Makati Dog & Cat Hospital','Ada Animal Clinics','Animal House','UP Veterinary Teaching Hospital, Diliman Station','Pendragon Veterinary Clinic','Vets in Practice Animal Hospital','The Pet Project Vet Clinic','Pet Society Veterinary Clinic']

    sick = ['Rashes', 'Red Spots', 'Breathing Heavy', 'Depressed/Low Energy', 'Would not Eat', 'Runny Eyes', 'Vomiting', 'Coughing', 'Fever', 'Weight loss', 'Diarrhea']

    k9 = K9.objects.exclude(assignment='None').exclude(handler=None).exclude(serial_number='Unassigned Serial Number')
    k9_list = list(k9)
    k9_sample = random.sample(k9_list, int(len(k9_list) * .10))

    vet = User.objects.filter(position="Veterinarian")
    vet_list=list(vet)

    problem = ['Anemia','Elbow Dysplasia','Lymphoma','Bladder Stones','Diabetes']
    treatment = ['Acute, supportive care may be necessary and indicate a need for a blood transfusion.','Integrative therapies, such as cold-therapy laser can also help decrease pain and inflammation.','Cyclophosphamide, vincristine, doxorubicin, and prednisone.','Extreme case is treated through surgery.','Monitor diet, feeding regimen, and start your dog on insulin therapy.']

    med = Medicine_Inventory.objects.exclude(medicine__med_type='Vaccine')
    med_list = list(med)

    for data in k9_sample:
        start_date = datetime(2019,1,1)
        end_date = datetime(2019,12,10)

        f_date = fake.date_between_dates(date_start=start_date, date_end=end_date)
        k_desc = random.choice(sick)
        v = random.choice(vet_list)
        prob = random.choice(problem)
        treat = random.choice(treatment)
        days = random.randint(1, 5)

        k9_incident = K9_Incident.objects.create(k9=data,incident='Sick',title=str(data)+str(' is Sick'),date=f_date,description=k_desc,status='Done',reported_by=data.handler)

        health = Health.objects.create(status='Done',image='prescription_image/prescription.jpg',date_done=f_date,dog=data,problem=prob,treatment=treat,veterinary=v,incident_id=k9_incident, duration = days)

        randomint = random.randint(1, 5)

        f_dur = 0
        for i in range(randomint):
            days = random.randint(1, 5)
            quan = random.randint(1, 10)
            m = random.choice(med_list)
            tod = random.choice(time_of_day)

            HealthMedicine.objects.create(health=health,medicine=m,quantity=quan,duration=days,time_of_day=tod)

            f_dur = f_dur+days

        health.duration = f_dur
        health.save()

def generate_k9_parents():
    fake = Faker()

    color_list = ['Black','Yellow','Chocolate','Dark Golden','Light Golden','Cream','Golden','Brindle','Silver Brindle','Gold Brindle','Salt and Pepper','Gray Brindle','Blue and Gray','Tan','Black-Tipped Fawn','Mahogany','White','Black and White','White and Tan']

    dam = K9.objects.filter(Q(training_status='For-Breeding') | Q(training_status='Breeding')).filter(sex='Female')

    sex_list = ['Male', 'Female']

    grade_list = ['75','80','85','90','95','100']
    vet = User.objects.filter(position="Veterinarian")
    vet_list=list(vet)

    ar = Medicine_Inventory.objects.filter(medicine__immunization='Anti-Rabies')
    bbb = Medicine_Inventory.objects.filter(medicine__immunization='Bordetella Bronchiseptica Bacterin')
    dw = Medicine_Inventory.objects.filter(medicine__immunization='Deworming')
    dhp = Medicine_Inventory.objects.filter(medicine__immunization='DHPPiL+CV')
    dh4 = Medicine_Inventory.objects.filter(medicine__immunization='DHPPiL4')
    hw = Medicine_Inventory.objects.filter(medicine__immunization='Heartworm')
    tf = Medicine_Inventory.objects.filter(medicine__immunization='Tick and Flea')

    print(dam.count())

    #BREED K9
    second_gen = []
    for data in dam:
        start_date = datetime(2019,1,1)
        end_date = datetime(2019,10,20)

        f_date = fake.date_between(start_date=start_date, end_date=end_date)
        try:
            sire = K9.objects.filter(Q(training_status='For-Breeding') | Q(training_status='Breeding')).filter(sex='Male').filter(breed=data.breed).filter(capability=data.capability)
            sire_list = list(sire)

            parent = K9_Parent.objects.filter(offspring=data)

            f_sire = []
            for par in parent:
                f_sire.append(par.father.id)

            n_sire = K9.objects.filter(Q(training_status='For-Breeding') | Q(training_status='Breeding')).filter(sex='Male').filter(breed=data.breed).filter(capability=data.capability).exclude(serial_number='Unassigned Serial Number').exclude(id__in=f_sire)


            sire_pick = random.choice(n_sire)

            if sire_pick:
                bol = True
                print('PICK', sire_pick)
            else:
                bol = False

        except:
            bol = False

        if bol == True:
            # print('SIRE',sire_pick)
            m_date = f_date - relativedelta(years=4)
            b_date = m_date + timedelta(days=63)

            born = random.randint(1, 3)
            died = random.randint(0, born)

            K9_Mated.objects.create(mother=data,father=sire_pick,status='Pregnancy Done',date_mated=m_date)

            K9_Litter.objects.create(mother=data, father=sire_pick,litter_no=born,litter_died=died)

            dif = born - died
            for i in range(dif):
                #Create offspring
                color = random.choice(color_list)
                sex = random.choice(sex_list)
                name = 'temp name'

                if sex == 'Male':
                    name = fake.first_name_male()
                elif sex == 'Female':
                    name = fake.first_name_female()

                weight = random.randint(30, 50)
                height = random.randint(60, 80)

                data.last_date_mated = m_date
                sire_pick.last_date_mated = m_date

                data.save()
                sire_pick.save()

                k9 = K9.objects.create(name=name,breed=data.breed,sex=sex,color=color,birth_date=b_date,source='Breeding',status='Working Dog', training_status='For-Breeding',training_level='Finished Training', capability=data.capability,trained='Trained',weight=weight,height=height)

                sn = 'SN-' + str(k9.id) + '-' + str(datetime.now().year)
                k9.serial_number = sn
                k9.save()

                K9_Parent.objects.create(mother=data,father=sire_pick,offspring=k9)

                second_gen.append(k9)

    print('For-Breeding CHANGE')
    print('SEC COUNT', len(second_gen))

    # CREATE/UPDATE SECOND GEN TRAINING, VACCINE, STATUS
    for data in second_gen:
        s_date = data.birth_date + relativedelta(years=2) #CHANGE
        k9 = data
        cap = data.capability
        handler = User.objects.filter(position="Handler")
        remark = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)

        Training_History.objects.create(k9=k9,handler=random.choice(handler),date=s_date)

        #FIRST TRAINING STAGE
        ts = Training_Schedule.objects.filter(k9=k9).last()
        dur_train = random.randint(20,40)
        t_date = s_date + timedelta(days=dur_train)
        ts.date_start = s_date
        ts.date_end = t_date
        ts.remarks = remark
        ts.save()

        train = Training.objects.filter(k9=k9).filter(training=cap).last()
        train.stage = 'Finished Training'
        train.stage1_1 = random.choice(grade_list)
        train.stage1_2 = random.choice(grade_list)
        train.stage1_3 = random.choice(grade_list)
        train.stage2_1 = random.choice(grade_list)
        train.stage2_2 = random.choice(grade_list)
        train.stage2_3 = random.choice(grade_list)
        train.stage3_1 = random.choice(grade_list)
        train.stage3_2 = random.choice(grade_list)
        train.stage3_3 = random.choice(grade_list)

        for i in range(8):
            dur_train = random.randint(20,40)
            ss_date = t_date
            t_date = t_date + timedelta(days=dur_train)
            remarks = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)

            if i == 0:
                # Stage 1.2
                Training_Schedule.objects.create(k9=k9,stage='Stage 1.2',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 1:
                # Stage 1.3
                Training_Schedule.objects.create(k9=k9,stage='Stage 1.3',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 2:
                # Stage 2.1
                Training_Schedule.objects.create(k9=k9,stage='Stage 2.1',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 3:
                # Stage 2.2
                Training_Schedule.objects.create(k9=k9,stage='Stage 2.2',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 4:
                # Stage 2.3
                Training_Schedule.objects.create(k9=k9,stage='Stage 2.3',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 5:
                # Stage 3.1
                Training_Schedule.objects.create(k9=k9,stage='Stage 3.1',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 6:
                # Stage 3.2
                Training_Schedule.objects.create(k9=k9,stage='Stage 3.2',date_start=ss_date,date_end=t_date,remarks=remarks)

        final_date = Training_Schedule.objects.filter(k9=k9).filter(stage='Stage 3.2').last()
        train.date_finished = final_date.date_end
        train.save()

        #VACCINE RECORD # get dont create
        vr = VaccinceRecord.objects.filter(k9=k9).last()
        vr.deworming_1 = True
        vr.deworming_2 = True
        vr.deworming_3 = True
        vr.deworming_4 = True
        vr.dhppil_cv_1 = True
        vr.dhppil_cv_2 = True
        vr.dhppil_cv_3 = True
        vr.heartworm_1 = True
        vr.heartworm_2 = True
        vr.heartworm_3 = True
        vr.heartworm_4 = True
        vr.heartworm_5 = True
        vr.heartworm_6 = True
        vr.heartworm_7 = True
        vr.heartworm_8 = True
        vr.anti_rabies = True
        vr.bordetella_1 = True
        vr.bordetella_2 = True
        vr.dhppil4_1 = True
        vr.dhppil4_2 = True
        vr.tick_flea_1 = True
        vr.tick_flea_2 = True
        vr.tick_flea_3 = True
        vr.tick_flea_4 = True
        vr.tick_flea_5 = True
        vr.tick_flea_6 = True
        vr.tick_flea_7 = True
        vr.status = 'Done'
        vr.save()

        # VaccineUsed
        start_date = data.birth_date #CHANGE K9 BDATE
        end_date = ts.date_start

        a = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='1').last()
        a.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        a.vaccine = random.choice(dw)
        a.veterinary = random.choice(vet_list)
        a.image = 'health_image/vac_stamp.jpg'
        a.done = True
        a.save()

        b = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='2').last()
        b.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        b.vaccine = random.choice(dw)
        b.veterinary = random.choice(vet_list)
        b.image = 'health_image/vac_stamp.jpg'
        b.done = True
        b.save()

        c = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='3').last()
        c.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        c.vaccine = random.choice(dw)
        c.veterinary = random.choice(vet_list)
        c.image = 'health_image/vac_stamp.jpg'
        c.done = True
        c.save()

        d = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='4').last()
        d.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        d.vaccine = random.choice(dhp)
        d.veterinary = random.choice(vet_list)
        d.image = 'health_image/vac_stamp.jpg'
        d.done = True
        d.save()

        e = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='5').last()
        e.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        e.vaccine = random.choice(hw)
        e.veterinary = random.choice(vet_list)
        e.image = 'health_image/vac_stamp.jpg'
        e.done = True
        e.save()

        f = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='6').last()
        f.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        f.vaccine = random.choice(bbb)
        f.veterinary = random.choice(vet_list)
        f.image = 'health_image/vac_stamp.jpg'
        f.done = True
        f.save()

        g = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='7').last()
        g.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        g.vaccine = random.choice(tf)
        g.veterinary = random.choice(vet_list)
        g.image = 'health_image/vac_stamp.jpg'
        g.done = True
        g.save()

        h = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='8').last()
        h.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        h.vaccine = random.choice(dh4)
        h.veterinary = random.choice(vet_list)
        h.image = 'health_image/vac_stamp.jpg'
        h.done = True
        h.save()

        i = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='9').last()
        i.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        i.vaccine = random.choice(dw)
        i.veterinary = random.choice(vet_list)
        i.image = 'health_image/vac_stamp.jpg'
        i.done = True
        i.save()

        j = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='10').last()
        j.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        j.vaccine = random.choice(hw)
        j.veterinary = random.choice(vet_list)
        j.image = 'health_image/vac_stamp.jpg'
        j.done = True
        j.save()

        k = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='11').last()
        k.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        k.vaccine = random.choice(bbb)
        k.veterinary = random.choice(vet_list)
        k.image = 'health_image/vac_stamp.jpg'
        k.done = True
        k.save()

        l = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='12').last()
        l.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        l.vaccine = random.choice(ar)
        l.veterinary = random.choice(vet_list)
        l.image = 'health_image/vac_stamp.jpg'
        l.done = True
        l.save()

        m = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='13').last()
        m.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        m.vaccine = random.choice(tf)
        m.veterinary = random.choice(vet_list)
        m.image = 'health_image/vac_stamp.jpg'
        m.done = True
        m.save()

        n = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='14').last()
        n.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        n.vaccine = random.choice(dhp)
        n.veterinary = random.choice(vet_list)
        n.image = 'health_image/vac_stamp.jpg'
        n.done = True
        n.save()

        o = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='15').last()
        o.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        o.vaccine = random.choice(hw)
        o.veterinary = random.choice(vet_list)
        o.image = 'health_image/vac_stamp.jpg'
        o.done = True
        o.save()

        p = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='16').last()
        p.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        p.vaccine = random.choice(dh4)
        p.veterinary = random.choice(vet_list)
        p.image = 'health_image/vac_stamp.jpg'
        p.done = True
        p.save()

        q = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='17').last()
        q.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        q.vaccine = random.choice(tf)
        q.veterinary = random.choice(vet_list)
        q.image = 'health_image/vac_stamp.jpg'
        q.done = True
        q.save()

        r = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='18').last()
        r.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        r.vaccine = random.choice(dh4)
        r.veterinary = random.choice(vet_list)
        r.image = 'health_image/vac_stamp.jpg'
        r.done = True
        r.save()

        s = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='19').last()
        s.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        s.vaccine = random.choice(hw)
        s.veterinary = random.choice(vet_list)
        s.image = 'health_image/vac_stamp.jpg'
        s.done = True
        s.save()

        t = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='20').last()
        t.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        t.vaccine = random.choice(tf)
        t.veterinary = random.choice(vet_list)
        t.image = 'health_image/vac_stamp.jpg'
        t.done = True
        t.save()

        u = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='21').last()
        u.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        u.vaccine = random.choice(hw)
        u.veterinary = random.choice(vet_list)
        u.image = 'health_image/vac_stamp.jpg'
        u.done = True
        u.save()

        v = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='22').last()
        v.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        v.vaccine = random.choice(tf)
        v.veterinary = random.choice(vet_list)
        v.image = 'health_image/vac_stamp.jpg'
        v.done = True
        v.save()

        w = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='23').last()
        w.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        w.vaccine = random.choice(hw)
        w.veterinary = random.choice(vet_list)
        w.image = 'health_image/vac_stamp.jpg'
        w.done = True
        w.save()

        x = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='24').last()
        x.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        x.vaccine = random.choice(tf)
        x.veterinary = random.choice(vet_list)
        x.image = 'health_image/vac_stamp.jpg'
        x.done = True
        x.save()

        y = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='25').last()
        y.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        y.vaccine = random.choice(hw)
        y.veterinary = random.choice(vet_list)
        y.image = 'health_image/vac_stamp.jpg'
        y.done = True
        y.save()

        z = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='26').last()
        z.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        z.vaccine = random.choice(tf)
        z.veterinary = random.choice(vet_list)
        z.image = 'health_image/vac_stamp.jpg'
        z.done = True
        z.save()

        zz = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='27').last()
        zz.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        zz.vaccine = random.choice(hw)
        zz.veterinary = random.choice(vet_list)
        zz.image = 'health_image/vac_stamp.jpg'
        zz.done = True
        zz.save()

        print(data, 'CREATE/UPDATE')

    dam2 = K9.objects.filter(Q(training_status='For-Breeding') | Q(training_status='Breeding')).filter(sex='Female')
    third_gen = []
    # BREED THIRD GEN
    for data in dam2:
        start_date = datetime(2019,1,1)
        end_date = datetime(2019,10,10)

        f_date = fake.date_between(start_date=start_date, end_date=end_date)

        if data.sex == 'Female':
            try:
                sire = K9.objects.filter(Q(training_status='For-Breeding') | Q(training_status='Breeding')).filter(sex='Male').filter(breed=data.breed).filter(capability=data.capability)
                sire_list = list(sire)

                parent = K9_Parent.objects.filter(offspring=data)

                f_sire = []
                for par in parent:
                    f_sire.append(par.father.id)

                n_sire = K9.objects.filter(Q(training_status='For-Breeding') | Q(training_status='Breeding')).filter(sex='Male').filter(breed=data.breed).filter(capability=data.capability).exclude(serial_number='Unassigned Serial Number').exclude(id__in=f_sire)

                sire_pick = random.choice(n_sire)

                if sire_pick:
                    bol = True
                    print('PICK', sire_pick)
                else:
                    bol = False
            except:
                bol = False

            if bol == True:
                m_date = f_date
                b_date = m_date + timedelta(days=63)

                born = random.randint(1, 3)
                died = random.randint(0, born)

                K9_Mated.objects.create(mother=data,father=sire_pick,status='Pregnancy Done',date_mated=m_date)

                K9_Litter.objects.create(mother=data, father=sire_pick,litter_no=born,litter_died=died)

                dif = born - died
                for i in range(dif):
                    #Create offspring
                    color = random.choice(color_list)
                    sex = random.choice(sex_list)
                    name = 'temp name'

                    if sex == 'Male':
                        name = fake.first_name_male()
                    elif sex == 'Female':
                        name = fake.first_name_female()

                    weight = random.randint(30, 50)
                    height = random.randint(60, 80)


                    data.last_date_mated = m_date
                    sire_pick.last_date_mated = m_date

                    data.save()
                    sire_pick.save()

                    k9 = K9.objects.create(name=name,breed=data.breed,sex=sex,color=color,birth_date=b_date,source='Breeding',weight=weight,height=height)
                    k9.save()

                    K9_Parent.objects.create(mother=data,father=sire_pick,offspring=k9)

                    third_gen.append(k9)


    print(third_gen)

    print('On Training','Puppy')
    print('THIRD COUNT', len(third_gen))
    # CREATE/UPDATE SECOND GEN TRAINING, VACCINE, STATUS, 1 yr old or less than
    for data in third_gen:
        s_date = data.birth_date
        k9 = data

        #VACCINE RECORD
        vr = VaccinceRecord.objects.filter(k9=k9).last()
        vr.deworming_1 = True
        vr.deworming_2 = True
        vr.deworming_3 = True
        vr.deworming_4 = True

        vr.dhppil_cv_1 = True
        vr.dhppil_cv_2 = True
        vr.dhppil_cv_3 = True

        vr.heartworm_1 = True
        vr.heartworm_2 = True
        vr.heartworm_3 = True

        vr.anti_rabies = True
        vr.bordetella_1 = True
        vr.bordetella_2 = True
        vr.dhppil4_1 = True
        vr.dhppil4_2 = False # LAST

        vr.tick_flea_1 = True
        vr.tick_flea_2 = True
        vr.tick_flea_3 = True
        vr.save()

        # VaccineUsed
        start_date = data.birth_date + timedelta(days=14)
        end_date = start_date + timedelta(days=133)

        a = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='1').last()
        a.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        a.vaccine = random.choice(dw)
        a.veterinary = random.choice(vet_list)
        a.image = 'health_image/vac_stamp.jpg'
        a.done = True
        a.save()

        b = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='2').last()
        b.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        b.vaccine = random.choice(dw)
        b.veterinary = random.choice(vet_list)
        b.image = 'health_image/vac_stamp.jpg'
        b.done = True
        b.save()

        c = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='3').last()
        c.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        c.vaccine = random.choice(dw)
        c.veterinary = random.choice(vet_list)
        c.image = 'health_image/vac_stamp.jpg'
        c.done = True
        c.save()

        d = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='4').last()
        d.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        d.vaccine = random.choice(dhp)
        d.veterinary = random.choice(vet_list)
        d.image = 'health_image/vac_stamp.jpg'
        d.done = True
        d.save()

        e = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='5').last()
        e.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        e.vaccine = random.choice(hw)
        e.veterinary = random.choice(vet_list)
        e.image = 'health_image/vac_stamp.jpg'
        e.done = True
        e.save()

        f = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='6').last()
        f.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        f.vaccine = random.choice(bbb)
        f.veterinary = random.choice(vet_list)
        f.image = 'health_image/vac_stamp.jpg'
        f.done = True
        f.save()

        g = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='7').last()
        g.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        g.vaccine = random.choice(tf)
        g.veterinary = random.choice(vet_list)
        g.image = 'health_image/vac_stamp.jpg'
        g.done = True
        g.save()

        h = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='8').last()
        h.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        h.vaccine = random.choice(dh4)
        h.veterinary = random.choice(vet_list)
        h.image = 'health_image/vac_stamp.jpg'
        h.done = True
        h.save()

        i = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='9').last()
        i.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        i.vaccine = random.choice(dw)
        i.veterinary = random.choice(vet_list)
        i.image = 'health_image/vac_stamp.jpg'
        i.done = True
        i.save()

        j = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='10').last()
        j.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        j.vaccine = random.choice(hw)
        j.veterinary = random.choice(vet_list)
        j.image = 'health_image/vac_stamp.jpg'
        j.done = True
        j.save()

        k = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='11').last()
        k.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        k.vaccine = random.choice(bbb)
        k.veterinary = random.choice(vet_list)
        k.image = 'health_image/vac_stamp.jpg'
        k.done = True
        k.save()

        l = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='12').last()
        l.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        l.vaccine = random.choice(ar)
        l.veterinary = random.choice(vet_list)
        l.image = 'health_image/vac_stamp.jpg'
        l.done = True
        l.save()

        m = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='13').last()
        m.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        m.vaccine = random.choice(tf)
        m.veterinary = random.choice(vet_list)
        m.image = 'health_image/vac_stamp.jpg'
        m.done = True
        m.save()

        n = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='14').last()
        n.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        n.vaccine = random.choice(dhp)
        n.veterinary = random.choice(vet_list)
        n.image = 'health_image/vac_stamp.jpg'
        n.done = True
        n.save()

        o = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='15').last()
        o.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        o.vaccine = random.choice(hw)
        o.veterinary = random.choice(vet_list)
        o.image = 'health_image/vac_stamp.jpg'
        o.done = True
        o.save()

        p = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='16').last()
        p.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        p.vaccine = random.choice(dh4)
        p.veterinary = random.choice(vet_list)
        p.image = 'health_image/vac_stamp.jpg'
        p.done = True
        p.save()

        q = VaccineUsed.objects.filter(vaccine_record=vr).filter(order='17').last()
        q.date_vaccinated = fake.date_between(start_date=start_date, end_date=end_date)
        q.vaccine = random.choice(tf)
        q.veterinary = random.choice(vet_list)
        q.image = 'health_image/vac_stamp.jpg'
        q.done = True
        q.save()

        print(data, 'CREATE/UPDATE')

def generate_k9_due_retire():
    k9_c = K9.objects.filter(training_status="Deployed").filter(status='Working Dog').exclude(handler=None).exclude(assignment="None")
    
    print('CAN RETIRE: ', k9_c.count())

    k9_list = list(k9_c)

    for i in range(5):
        k9_choice = random.choice(k9_list)
        k9 = K9.objects.get(id=k9_choice.id)

        k9.birth_date = date.today() - relativedelta(years=9)
        k9.status = "Due-For-Retirement"
        k9.save()
        
        print("DUE TO RETIRE ", k9, k9.handler.id, k9.training_status, k9.status)

    return None
def generate_sick_breeding():
    fake = Faker()

    k9 = K9.objects.filter(Q(training_status='For-Breeding') | Q(training_status='Breeding'))
    k9_list = list(k9)

    time_of_day = ['Morning','Afternoon','Night','Morning/Afternoon','Morning/Night','Afternoon/Night','Morning/Afternoon/Night']

    clinic = ['Companion Animal Veterinary Clinic','BSF Animal Clinic','Makati Dog & Cat Hospital','Ada Animal Clinics','Animal House','UP Veterinary Teaching Hospital, Diliman Station','Pendragon Veterinary Clinic','Vets in Practice Animal Hospital','The Pet Project Vet Clinic','Pet Society Veterinary Clinic']

    sick = ['Rashes', 'Red Spots', 'Breathing Heavy', 'Depressed/Low Energy', 'Would not Eat', 'Runny Eyes', 'Vomiting', 'Coughing', 'Fever', 'Weight loss', 'Diarrhea']

    vet = User.objects.filter(position="Veterinarian")
    vet_list=list(vet)

    problem = ['Anemia','Elbow Dysplasia','Lymphoma','Bladder Stones','Diabetes']
    treatment = ['Acute, supportive care may be necessary and indicate a need for a blood transfusion.','Integrative therapies, such as cold-therapy laser can also help decrease pain and inflammation.','Cyclophosphamide, vincristine, doxorubicin, and prednisone.','Extreme case is treated through surgery.','Monitor diet, feeding regimen, and start your dog on insulin therapy.']

    med = Medicine_Inventory.objects.exclude(medicine__med_type='Vaccine')
    med_list = list(med)

    for i in range(20):
        print("Generate Health Concern for Breeding ", i+1)
        data = random.choice(k9_list)

        start_date = datetime(2019,1,1)
        end_date = datetime(2019,12,10)

        f_date = fake.date_between(start_date=start_date, end_date=end_date)
        k_desc = random.choice(sick)
        v = random.choice(vet_list)
        prob = random.choice(problem)
        treat = random.choice(treatment)
        days = random.randint(1, 5)

        k9_incident = K9_Incident.objects.create(k9=data,incident='Sick',title=str(data)+str(' is Sick'),date=f_date,description=k_desc,status='Done',reported_by=data.handler)

        health = Health.objects.create(status='Done',image='prescription_image/prescription.jpg',date_done=f_date,dog=data,problem=prob,treatment=treat,veterinary=v,incident_id=k9_incident, duration = days)

        randomint = random.randint(1, 5)

        f_dur = 0
        for i in range(randomint):
            days = random.randint(1, 5)
            quan = random.randint(1, 10)
            m = random.choice(med_list)
            tod = random.choice(time_of_day)

            HealthMedicine.objects.create(health=health,medicine=m,quantity=quan,duration=days,time_of_day=tod)

            f_dur = f_dur+days

        health.duration = f_dur
        health.save()

    #K9 LITTER
    female = K9.objects.filter(Q(training_status='For-Breeding') | Q(training_status='Breeding')).filter(sex='Female')
    male = K9.objects.filter(Q(training_status='For-Breeding') | Q(training_status='Breeding')).filter(sex='Male')

    sire = list(male)
    dam = list(female)

    for i in range(20):
        print("Generate K9 Litter for Breeding ", i+1)
        born = random.randint(1, 8)
        died = random.randint(0, born)

        mom = random.choice(dam)
        dad = random.choice(sire)

        K9_Litter.objects.create(mother=mom, father=dad,litter_no=born,litter_died=died)


def generate_adoption():
    fake = Faker()

    sex_list = ['Male', 'Female']
    color_list = ['Black','Yellow','Chocolate','Dark Golden','Light Golden','Cream','Golden','Brindle','Silver Brindle','Gold Brindle','Salt and Pepper','Gray Brindle','Blue and Gray','Tan','Black-Tipped Fawn','Mahogany','White','Black and White','White and Tan']
    skill_list = ['EDD', 'NDD', 'SAR']

    breed_list = Dog_Breed.objects.all().values_list('breed', flat=True).distinct()
    breed_list = list(breed_list)

    supplier_list = K9_Supplier.objects.all().values_list('id', flat=True).distinct()
    supplier_list = list(supplier_list)
    supplier_id = random.choice(supplier_list)
    supplier = K9_Supplier.objects.filter(id=supplier_id).last()

    #CREATE K9 FAILED
    for i in range(30):
        #Create offspring
        start_date = datetime(2018,1,1)
        end_date = datetime(2019,2,20)

        b_date = fake.date_between(start_date='-2y', end_date='-1y')
        color = random.choice(color_list)
        sex = random.choice(sex_list)
        name = 'temp name'

        if sex == 'Male':
            name = fake.first_name_male()
        elif sex == 'Female':
            name = fake.first_name_female()

        weight = random.randint(30, 50)
        height = random.randint(60, 80)
        cap = random.choice(skill_list)
        breed = random.choice(breed_list)

        k9 = K9.objects.create(name=name,breed=breed,sex=sex,color=color,birth_date=b_date, source='Procurement',status='Material Dog',training_level='Stage 1.1',capability=cap,trained='Failed',weight=weight,height=height,supplier=supplier)
        k9.training_status = 'For-Adoption'
        k9.save()

        dur = random.randint(40,100)
        date_start = fake.date_between(start_date=start_date, end_date=end_date)
        date_end = fake.date_between(start_date=date_start, end_date=(date_start+timedelta(days=dur)))


        tr = Training.objects.filter(k9=k9,training=cap).last()
        ts = Training_Schedule.objects.filter(k9=k9).last()

        ts.stage = 'Stage 1.1'
        ts.date_start = date_start
        ts.date_end = date_end
        ts.remarks = 'Poor Performance'

        tr.stage = 'Stage 1.1 Failed'
        tr.date_finished = date_end

        tr.save()
        ts.save()

    k9_adopt = K9.objects.filter(training_status = 'For-Adoption')

    for i, k9 in enumerate(k9_adopt):
        sex = random.choice(sex_list)
        name = 'temp_name'
        if sex == 'Female':
            name = fake.first_name_female()
        else:
            name = fake.first_name_male()
        middle_name = fake.last_name()
        last_name = fake.last_name()
        email = name+last_name+"@gmail.com"
        birth_date = fake.date_between(start_date='-30y', end_date='-25y')
        address = fake.address()
        contact_no = "+63" + fake.msisdn()[:10]
        date_adopted = fake.date_between(start_date='-1y', end_date='now')
        date_returned = fake.date_between(start_date=date_adopted, end_date='now')
        reason = fake.paragraph(nb_sentences=1, variable_nb_sentences=True, ext_word_list=None)
        # 20 Adopted
        if i < 20:
            K9_Adopted_Owner.objects.create(k9=k9,first_name=name,middle_name=middle_name,last_name=last_name,address=address,sex=sex,birth_date=birth_date,email=email,contact_no=contact_no,date_adopted=date_adopted)
            k9.training_status = 'Adopted'
            k9.status = 'Adopted'
            k9.save()
            print("Generate Adopted" + str(i), k9)

        # 10 Returned
        if i > 20:
            K9_Adopted_Owner.objects.create(k9=k9,first_name=name,middle_name=middle_name,last_name=last_name,address=address,sex=sex,birth_date=birth_date,email=email,contact_no=contact_no,date_adopted=date_adopted,date_returned=date_returned,reason=reason)
            print("Generate Returned" + str(i), k9)

def generate_grading():
    fake = Faker()

    sex_list = ['Male', 'Female']
    color_list = ['Black','Yellow','Chocolate','Dark Golden','Light Golden','Cream','Golden','Brindle','Silver Brindle','Gold Brindle','Salt and Pepper','Gray Brindle','Blue and Gray','Tan','Black-Tipped Fawn','Mahogany','White','Black and White','White and Tan']
    skill_list = ['EDD', 'NDD', 'SAR']

    breed_list = Dog_Breed.objects.all().values_list('breed', flat=True).distinct()
    breed_list = list(breed_list)

    supplier_list = K9_Supplier.objects.all().values_list('id', flat=True).distinct()
    supplier_list = list(supplier_list)
    supplier_id = random.choice(supplier_list)
    supplier = K9_Supplier.objects.filter(id=supplier_id).last()

    grade_list = ['75','80','85','90','95','100']
    #CREATE K9 FAILED
    for x in range(6):
        handler_list = User.objects.filter(position='Handler').filter(partnered=False).filter(assigned=False)
        handler = list(handler_list)
        #Create offspring
        start_date = datetime(2018,1,1)
        end_date = datetime(2019,2,20)

        b_date = fake.date_between(start_date='-2y', end_date='-1y')
        color = random.choice(color_list)
        sex = random.choice(sex_list)
        name = 'temp name'

        if sex == 'Male':
            name = fake.first_name_male()
        elif sex == 'Female':
            name = fake.first_name_female()

        weight = random.randint(30, 50)
        height = random.randint(60, 80)
        cap = random.choice(skill_list)
        breed = random.choice(breed_list)

        #K9 on stage 3.1
        han_c = random.choice(handler)
        k9 = K9.objects.create(handler=han_c,name=name,breed=breed,sex=sex,color=color,birth_date=b_date, source='Procurement',status='Material Dog',capability=cap,weight=weight,height=height,supplier=supplier)
        k9.training_status = 'On-Training'
        k9.training_level = 'Stage 2.3'
        k9.save()
        han_c.partnered = True
        han_c.save()

        train = Training.objects.filter(k9=k9).filter(training=k9.capability).last()
        train.stage = 'Stage 2.3'
        train.stage1_1 = random.choice(grade_list)
        train.stage1_2 = random.choice(grade_list)
        train.stage1_3 = random.choice(grade_list)
        train.stage2_1 = random.choice(grade_list)
        train.stage2_2 = random.choice(grade_list)
        train.stage2_3 = random.choice(grade_list)
        train.save()

        ts = Training_Schedule.objects.filter(k9=k9).last()

        dur_train = random.randint(20,40)
        ts.date_start = fake.date_between(start_date=b_date, end_date=b_date+timedelta(days=300))
        ts.date_end = fake.date_between(start_date=ts.date_start, end_date=ts.date_start+timedelta(days=dur_train))
        ts.remarks = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)
        ts.save()

        t_date = ts.date_end

        print(k9,' - Stage 3.1 For Grading')
        #CREATE TRAINING SCHED
        for i in range(6):
            dur_train = random.randint(20,40)
            ss_date = t_date
            t_date = t_date + timedelta(days=dur_train)
            remarks = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)

            if i == 0:
                # Stage 1.2
                Training_Schedule.objects.create(k9=k9,stage='Stage 1.1',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 1:
                # Stage 1.3
                Training_Schedule.objects.create(k9=k9,stage='Stage 1.2',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 2:
                # Stage 2.1
                Training_Schedule.objects.create(k9=k9,stage='Stage 1.3',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 3:
                # Stage 2.2
                Training_Schedule.objects.create(k9=k9,stage='Stage 2.1',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 4:
                # Stage 2.3
                Training_Schedule.objects.create(k9=k9,stage='Stage 2.2',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 5:
                # Stage 3.1
                Training_Schedule.objects.create(k9=k9,stage='Stage 2.3',date_start=ss_date,date_end=t_date,remarks=remarks)

        #K9 on stage 3.3
    for x in range(6):
        handler_list = User.objects.filter(position='Handler').filter(partnered=False).filter(assigned=False)
        handler = list(handler_list)

        #Create offspring
        start_date = datetime(2018,1,1)
        end_date = datetime(2019,2,20)

        b_date = fake.date_between(start_date='-2y', end_date='-1y')
        color = random.choice(color_list)
        sex = random.choice(sex_list)
        name = 'temp name'

        if sex == 'Male':
            name = fake.first_name_male()
        elif sex == 'Female':
            name = fake.first_name_female()

        weight = random.randint(30, 50)
        height = random.randint(60, 80)
        cap = random.choice(skill_list)
        breed = random.choice(breed_list)

        han_c = random.choice(handler)
        k9 = K9.objects.create(handler=han_c,name=name,breed=breed,sex=sex,color=color,birth_date=b_date, source='Procurement',status='Material Dog',capability=cap,weight=weight,height=height,supplier=supplier)
        k9.training_status = 'On-Training'
        k9.training_level = 'Stage 3.2'
        k9.save()
        han_c.partnered = True
        han_c.save()

        train = Training.objects.filter(k9=k9).filter(training=k9.capability).last()
        train.stage = 'Stage 3.2'
        train.stage1_1 = random.choice(grade_list)
        train.stage1_2 = random.choice(grade_list)
        train.stage1_3 = random.choice(grade_list)
        train.stage2_1 = random.choice(grade_list)
        train.stage2_2 = random.choice(grade_list)
        train.stage2_3 = random.choice(grade_list)
        train.stage3_1 = random.choice(grade_list)
        train.stage3_2 = random.choice(grade_list)
        train.save()
        ts = Training_Schedule.objects.filter(k9=k9).last()

        dur_train = random.randint(20,40)
        ts.date_start = fake.date_between(start_date=b_date, end_date=b_date+timedelta(days=300))
        ts.date_end = fake.date_between(start_date=ts.date_start, end_date=ts.date_start+timedelta(days=dur_train))
        ts.remarks = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)
        ts.save()

        t_date = ts.date_end

        #CREATE TRAINING SCHED
        print(k9,' - Stage 3.3 For Grading')
        for i in range(8):
            dur_train = random.randint(20,40)
            ss_date = t_date
            t_date = t_date + timedelta(days=dur_train)
            remarks = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)

            if i == 0:
                # Stage 1.2
                Training_Schedule.objects.create(k9=k9,stage='Stage 1.1',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 1:
                # Stage 1.3
                Training_Schedule.objects.create(k9=k9,stage='Stage 1.2',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 2:
                # Stage 2.1
                Training_Schedule.objects.create(k9=k9,stage='Stage 1.3',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 3:
                # Stage 2.2
                Training_Schedule.objects.create(k9=k9,stage='Stage 2.1',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 4:
                # Stage 2.3
                Training_Schedule.objects.create(k9=k9,stage='Stage 2.2',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 5:
                # Stage 3.1
                Training_Schedule.objects.create(k9=k9,stage='Stage 2.3',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 6:
                # Stage 3.2
                Training_Schedule.objects.create(k9=k9,stage='Stage 3.1',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 7:
                # Stage 3.2
                Training_Schedule.objects.create(k9=k9,stage='Stage 3.2',date_start=ss_date,date_end=t_date,remarks=remarks)

    for x in range(6):
        handler_list = User.objects.filter(position='Handler').filter(partnered=False).filter(assigned=False)
        handler = list(handler_list)
        #Create offspring
        start_date = datetime(2018,1,1)
        end_date = datetime(2019,2,20)

        b_date = fake.date_between(start_date='-2y', end_date='-1y')
        color = random.choice(color_list)
        sex = random.choice(sex_list)
        name = 'temp name'

        if sex == 'Male':
            name = fake.first_name_male()
        elif sex == 'Female':
            name = fake.first_name_female()

        weight = random.randint(30, 50)
        height = random.randint(60, 80)
        cap = random.choice(skill_list)
        breed = random.choice(breed_list)

        han_c = random.choice(handler)
        k9 = K9.objects.create(handler=han_c,name=name,breed=breed,sex=sex,color=color,birth_date=b_date, source='Procurement',status='Material Dog',capability=cap,weight=weight,height=height,supplier=supplier)
        k9.training_status = 'On-Training'
        k9.training_level = 'Stage 3.2'
        k9.save()
        han_c.partnered = True
        han_c.save()

        train = Training.objects.filter(k9=k9).filter(training=k9.capability).last()
        train.stage = 'Stage 3.2'
        train.stage1_1 = random.choice(grade_list)
        train.stage1_2 = random.choice(grade_list)
        train.stage1_3 = random.choice(grade_list)
        train.stage2_1 = random.choice(grade_list)
        train.stage2_2 = random.choice(grade_list)
        train.stage2_3 = random.choice(grade_list)
        train.stage3_1 = random.choice(grade_list)

        train.save()
        ts = Training_Schedule.objects.filter(k9=k9).last()

        dur_train = random.randint(20,40)
        ts.date_start = fake.date_between(start_date=b_date, end_date=b_date+timedelta(days=300))
        ts.date_end = fake.date_between(start_date=ts.date_start, end_date=ts.date_start+timedelta(days=dur_train))
        ts.remarks = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)
        ts.save()

        t_date = ts.date_end

        #CREATE TRAINING SCHED
        print(k9,' - Stage 3.3 For Training')
        for i in range(7):
            dur_train = random.randint(20,40)
            ss_date = t_date
            t_date = t_date + timedelta(days=dur_train)
            remarks = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)

            if i == 0:
                # Stage 1.2
                Training_Schedule.objects.create(k9=k9,stage='Stage 1.1',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 1:
                # Stage 1.3
                Training_Schedule.objects.create(k9=k9,stage='Stage 1.2',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 2:
                # Stage 2.1
                Training_Schedule.objects.create(k9=k9,stage='Stage 1.3',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 3:
                # Stage 2.2
                Training_Schedule.objects.create(k9=k9,stage='Stage 2.1',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 4:
                # Stage 2.3
                Training_Schedule.objects.create(k9=k9,stage='Stage 2.2',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 5:
                # Stage 3.1
                Training_Schedule.objects.create(k9=k9,stage='Stage 2.3',date_start=ss_date,date_end=t_date,remarks=remarks)
            if i == 6:
                # Stage 3.2
                Training_Schedule.objects.create(k9=k9,stage='Stage 3.1',date_start=ss_date,date_end=t_date,remarks=remarks)

        print('Handler ID- ',han_c.id)

def fix_dog_duplicates():

    k9s = K9.objects.all()

    k9_list = []
    for k9 in k9s:
        k9_list.append(k9.name)

    # Get unique names
    k9_list = list(set(k9_list))

    for item in k9_list:
        k9s = K9.objects.filter(name = item)
        ctr = 1
        if k9s.count() > 1:
            for k9 in k9s:
                k9.name = k9.name + " " + str(ctr)
                k9.save()
                print(str(k9.name))
                ctr += 1

    return None

#TODO item request from team leader (approved and insufficient)
def generate_item_request():
    pass

'''
TODO

Create Incidents
Create Parents (Use For-Breeding K9s)
Create Litter
Create K9_mated
Create Health (Specially for K9s that have reach deployment/breeding decision)

VaccineUsed Record for Procured K9s (Date of vaccination lang kailangan + Name of Diseases)4 diseases
Remove handlers on For-Breeding K9s, then status is unpartnered
Fix duplicate Names on k9s
Add K9(s) on final stage of training
Schedule K9s to request
Other Report stuff
'''
