from faker import Faker
import random
from datetime import timedelta, datetime
from profiles.models import User, Account, Personal_Info, Education
from planningandacquiring.models import K9, K9_Supplier, Dog_Breed
from deployment.models import Area, Location, Dog_Request, Incidents, Maritime, Team_Assignment, K9_Pre_Deployment_Items, \
    K9_Schedule, Team_Dog_Deployed
from django.contrib.auth.models import User as AuthUser
from training.models import Training, Training_Schedule, Training_History

from inventory.models import Miscellaneous, Food, Medicine_Inventory, Medicine

from deployment.tasks import assign_TL

import re

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

def generate_rank():
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

    randomizer = random.randint(0, 8)

    return RANK[randomizer][0]

def generate_bloodtype():
    BLOODTYPE = (
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O')
    )

    randomizer = random.randint(0, 3)

    return BLOODTYPE[randomizer][0]


def generate_religion():
    RELIGION = (
        ('Roman Catholic', 'Roman Catholic'),
        ('Christianity', 'Christianity'),
        ('Islam', 'Islam'),
        ('Iglesia ni Cristo', 'Iglesia ni Cristo'),
        ('Buddhist', 'Buddhist'),
    )

    randomizer = random.randint(0, 4)

    return RELIGION[randomizer][0]

def generate_skin_color():
    SKINCOLOR = (
        ('Light', 'Light'),
        ('Dark', 'Dark'),
        ('Yellow', 'Yellow'),
        ('Brown', 'Brown')
    )

    randomizer = random.randint(0, 3)

    return SKINCOLOR[randomizer][0]

def generate_position():
    POSITION = (
        ('Handler', 'Handler'),
        ('Veterinarian', 'Veterinarian'),
        ('Administrator', 'Administrator'),
        ('Team Leader', 'Team Leader'),
        ('Commander', 'Commander'),
        ('Operations', 'Operations'),
        ('Trainer', 'Trainer'),
    )

    randomizer = random.randint(0, 6)

    return POSITION[randomizer][0]

def generate_user():
    fake = Faker()


    handler_count = 329
    commander_count = 30
    vet_count = 19
    operations = 2
    trainor = 4
    admin = 15

    ctr = 0
    for x in range(0, 400):

        position = ""

        if ctr <= 329:
            position = "Handler"
        elif ctr >= 330 and ctr <= 360:
            position = "Commander"
        elif ctr >= 361 and ctr <= 379:
            position = "Veterinarian"
        elif ctr == 380 or ctr == 381:
            position = "Operations"
        elif ctr >= 382 and ctr <= 385:
            position = "Trainer"
        else:
            position = 'Administrator'


        print("Rank : " + generate_rank())
        rank = generate_rank()

        randomizer = random.randint(0, 1)

        gender = "?"
        first_name = "?"
        if randomizer == 0:
            first_name = fake.first_name_male()
            print("First Name : " + first_name)
            gender = "Male"
        else:
            first_name = fake.first_name_female()
            print("First Name : " + first_name)
            gender = "Female"

        last_name = fake.last_name()
        print("Last Name :" + last_name)
        print("Gender : " + gender)

        generated_date = fake.date_between(start_date="-30y", end_date="-20y")
        birthdate = generated_date.strftime("%m/%d/%Y")
        print("Birthdate : " + birthdate)
        print("Birthplace : " + fake.address())
        birthplace = fake.address()

        print("Bloodtype : " + generate_bloodtype())
        blood_type = generate_bloodtype()
        print("Religion : " + generate_religion())
        religion = generate_religion()

        randomizer = random.randint(0, 1)

        civil_status = "?"
        if randomizer == 0:
            print("Civil Status : Single")
            civil_status = "Single"
        else:
            print("Civil Status : Married")
            civil_status = "Married"

        print("Skin Color : " + generate_skin_color())
        skin_color = generate_skin_color()
        print("Eye Color : " + fake.safe_color_name())
        eye_color = fake.safe_color_name()
        print("Hair Color : " + fake.safe_color_name())
        hair_color = fake.safe_color_name()

        username = first_name + last_name
        username = username.lower()
        print("Username : " + username)
        print("Email : " + username + "@gmail.com")
        email = username + "@gmail.com"
        print("Position : " + position)
        print()

        user = User.objects.create(rank = rank, firstname = first_name, lastname = last_name, middlename = "", nickname = "", birthdate = generated_date, birthplace = birthplace, gender = gender,
                                   civilstatus = civil_status, citizenship = "Filipino", religion = religion, bloodtype = blood_type, haircolor = hair_color, eyecolor = eye_color, skincolor = skin_color,
                                   position = position)
        user.save()
        generate_personal_info(user, last_name)
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
    return None

def generate_personal_info(user, last_name):
    fake = Faker()
    print("Cell Number : +63" + fake.msisdn()[:10])
    cellnum = fake.msisdn()[:10]
    print("Phone Number : " + fake.msisdn()[:7])
    phonenum = fake.msisdn()[:7]

    print("Father's Name : " + fake.first_name_male() + " " + last_name)
    father = fake.first_name_male() + " " + last_name
    mother_birth = fake.date_between(start_date="-30y", end_date="-20y")
    print("Mother's Name : " + fake.first_name_female() + " " + last_name)
    mother = fake.first_name_female() + " " + last_name
    father_birth = fake.date_between(start_date="-30y", end_date="-20y")

    print("Street : " + fake.street_name() + " St.")
    street = fake.street_name() + " St."
    print("Barangay : Brngy. " + fake.street_name())
    brngy = "Brngy. " + fake.street_name()
    city = generate_city_ph()
    province = "x province"

    tin = fake.msisdn()[:7]
    phil = fake.msisdn()[:7]

    personal = Personal_Info.objects.create(UserID = user, mobile_number = cellnum, tel_number = phonenum, street = street, barangay = brngy, city = city, province = province,
                                            mother_name = mother, father_name = father, mother_birthdate = mother_birth, father_birthdate = father_birth, tin = tin, philhealth = phil)
    personal.save()

    return None

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>END OF USER CREATION


def generate_breed():
    BREED = (
        ('Belgian Malinois', 'Belgian Malinois'),
        ('Dutch Sheperd', 'Dutch Sheperd'),
        ('German Sheperd', 'German Sheperd'),
        ('Golden Retriever', 'Golden Retriever'),
        ('Jack Russel', 'Jack Russel'),
        ('Labrador Retriever', 'Labrador Retriever'),
    )
    randomizer = random.randint(0, 5)

    return BREED[randomizer][0]

def generate_k9_color():
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

    randomizer = random.randint(0, 18)

    return COLOR[randomizer][0]

def generate_skill():
    SKILL = (
        ('NDD', 'NDD'),
        ('EDD', 'EDD'),
        ('SAR', 'SAR')
    )

    randomizer = random.randint(0, 2)

    return SKILL[randomizer][0]


# Get 90% of all k9s then assign a random skill to each one
def assign_skill_random():
    k9s = K9.objects.all()

    k9_id_list = []
    for k9 in k9s:
        k9_id_list.append(k9.id)

    k9_sample = random.sample(k9_id_list, int(len(k9_id_list)*.90))

    k9s = K9.objects.filter(pk__in = k9_sample)

    for k9 in k9s:
        k9.capability = generate_skill()
        k9.training_status = "Classified"
        k9.save()

    return k9_sample


# Get 80% of all classified k9s then assign a random handler to each one
def assign_handler_random():

    k9_sample = assign_skill_random()

    users = User.objects.filter(position = "Handler")

    user_id_list = []
    for user in users:
        user_id_list.append(user.id)

    k9_sample = random.sample(k9_sample, int(len(k9_sample)*.80))
    user_sample = random.sample(user_id_list, len(k9_sample)) #user sample now have the same length as k9 sample
    partnership = zip(k9_sample, user_sample)


    for item in partnership:
        k9 = K9.objects.get(id = item[0])
        user = User.objects.get(id = item[1])

        k9.handler = user
        k9.training_status = 'On-Training'
        k9.save()

    return k9_sample

#Get 70% of all k9s with handlers then end their training
def generate_training():
    fake = Faker()

    k9_sample = assign_handler_random() #Get all k9s with available handlers
    k9_sample = random.sample(k9_sample, int(len(k9_sample) * .80))

    k9s = K9.objects.filter(pk__in = k9_sample)

    GRADE = (
        # ("0", "0"),
        ("75", "75"),
        ("80", "80"),
        ("85", "85"),
        ("90", "90"),
        ("95", "95"),
        ("100", "100"),
    )

    for k9 in k9s:
        #create training history
        fake_date = fake.date_between(start_date='-5y', end_date='today')
        Training_History.objects.create(k9=k9,handler=k9.handler,date=fake_date)


        birthdate = k9.birth_date

        training_start_alpha = datetime.combine(birthdate, datetime.min.time())
        training_start_alpha = training_start_alpha + timedelta(days=365)


        training = Training.objects.filter(k9 = k9).get(training = k9.capability)

        remark = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)

        train_sched = Training_Schedule.objects.get(k9 = k9) #Because we have 1 instance of this per k9 instance
        train_sched.date_start = training_start_alpha
        train_sched.date_end = training_start_alpha + timedelta(days=20)

        #TODO populate does not reach stage 3.3
        grade_list = []
        stage = "Stage 0"
        for idx in range(9):
            randomizer = random.randint(0, 5)
            grade = GRADE[randomizer][0]
            grade_list.append(grade)

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
            elif idx == 8:
                stage = "Stage 3.3"

            # if idx <= 8: 

            sched_remark = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)
            train_sched = Training_Schedule.objects.create(k9 = k9, date_start = training_start_alpha + timedelta(days=20 * idx + 1),
                                                               date_end = training_start_alpha + timedelta(days=20 * idx + 2), stage = stage, remarks = sched_remark)
            train_sched.save()


        training.stage1_1 = grade_list[0]
        training.stage1_2 = grade_list[1]
        training.stage1_3 = grade_list[2]

        training.stage2_1 = grade_list[3]
        training.stage2_2 = grade_list[4]
        training.stage2_3 = grade_list[5]

        training.stage3_1 = grade_list[6]
        training.stage3_2 = grade_list[7]
        training.stage3_3 = grade_list[8]

        training.remarks = remark
        training.stage = "Finished Training"
        training.save()

        k9.training_status = 'Trained'
        k9.training_level = "Finished Training"
        k9.serial_number = 'SN-' + str(k9.id) + '-' + str(datetime.now().year)
        k9.trained = "Trained"
        k9.save()

        print(str(k9))
        print("Grade : " + str(training.grade))

    return None


def generate_k9_posttraining_decision():

    k9s = K9.objects.filter(training_status = "Trained")
    k9_id_list = []
    for k9 in k9s:
        k9_id_list.append(k9.id)
    k9_sample = random.sample(k9_id_list, int(len(k9_id_list) * .80)) #80% of all trained k9s

    for_deployment = random.sample(k9_sample, int(len(k9_sample) * .80))
    for k9 in for_deployment:
        try:
            k9_sample.remove(k9)
        except: pass
    for_breeding = k9_sample

    for id in for_deployment:
        try:
            k9 = K9.objects.get(id = id)
            k9.training_status = "For-Deployment"
            k9.status = "Working Dog"
            k9.save()
        except: pass

    for id in for_breeding:
        try:
            k9 = K9.objects.get(id = id)
            k9.training_status = "For-Breeding"
            k9.status = "Working Dog"
            k9.save()
        except: pass

    return None

def select_port_assign(k9):

    ports = Team_Assignment.objects.filter(total_dogs_deployed__lt = 5)

    if k9.capability == "SAR":
        ports = ports.filter(SAR_deployed__lt = 1)
    elif k9.capability == "NDD":
        ports = ports.filter(NDD_deployed__lt=2)
    elif k9.capability == "EDD":
        ports = ports.filter(EDD_deployed__lt=2)

    port_id_list = []
    for port in ports:
        port_id_list.append(port.id)

    randomizer = random.randint(0, len(port_id_list) - 1)
    location = Location.objects.get(id = port_id_list[randomizer])
    return Team_Assignment.objects.get(location = location)

# Randomly assign to ports
def generate_k9_deployment():
    fake = Faker()

    k9s = K9.objects.filter(training_status = "For-Deployment")

    k9_id_list = []
    for k9 in k9s:
        k9_id_list.append(k9.id)
    k9_sample = random.sample(k9_id_list, int(len(k9_id_list) * .80))

    for id in k9_sample:

        k9 = K9.objects.get(id = id)

        train_sched = Training_Schedule.objects.get(k9 = k9, stage = "Stage 3.3")
        deployment_date = train_sched.date_end
        deployment_date += timedelta(days= random.randint(7, 14))

        team = select_port_assign(k9)
        sched = K9_Schedule.objects.create(team = team, k9=k9, status="Initial Deployment",
                                            date_start=deployment_date)
        sched.save()
        pre_req_item = K9_Pre_Deployment_Items.objects.create(k9=k9, initial_sched=sched, status="Done")
        deploy = Team_Dog_Deployed.objects.create(team_assignment = team, k9 = k9,
                                                  date_added = deployment_date + timedelta(days= random.randint(1, 6)))
        deploy.save()

        if k9.capability == "SAR":
            team.SAR_deployed += 1
        elif k9.capability == "NDD":
            team.NDD_deployed += 1
        elif k9.capability == "EDD":
            team.EDD_deployed += 1
        team.save()

        assign_TL(team)
        print("K9 : " + str(k9))
        print("Team Assignment : " + str(team))


    return None

def generate_k9_supplier():
    fake = Faker()

    for x in range(0, 12):
        contact = "+63" + fake.msisdn()[:10]
        supplier = K9_Supplier.objects.create(name=fake.name(), organization=fake.company(), address=fake.address(),
                                          contact_no=contact)
        supplier.save()
    return None

#Half of K9s are classified
def generate_k9():
    fake = Faker()

    suppliers = K9_Supplier.objects.all()

    if suppliers.count() == 0:
        generate_k9_supplier()
        suppliers = K9_Supplier.objects.all()

    for x in range (0, 300):

        randomizer = random.randint(0, 1)

        name = "?"
        gender = "?"
        if randomizer == 0:
            print("Name : " + fake.first_name_male())
            name = fake.first_name_male()
            print("Gender : Male")
            gender = "Male"
        else:
            print("Name : " + fake.first_name_female())
            name = fake.first_name_female()
            print("Gender : Female")
            gender = "Female"

        print("Color : " + fake.safe_color_name())
        color = generate_k9_color()
        print("Breed : " + generate_breed())
        breed = generate_breed()

        generated_date = fake.date_between(start_date="-3y", end_date="-1y")
        date_time = generated_date.strftime("%m/%d/%Y")
        print("Birthdate : " + date_time)


        #TODO Add K9s that are For-deployment and For-Breeding
        #Classifies other K9s
        k9 = K9.objects.create(name = name, breed = breed, sex = gender, color = color, birth_date = generated_date, source = "Procurement")
        k9.save()


        if k9.source == "Procurement":
            try:
                randomizer = random.randint(0, suppliers.count() - 1)
                supplier = K9_Supplier.objects.get(id = randomizer)
                k9.supplier = supplier
                k9.save()
            except: pass

    return None


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>END OF K9 CREATION


def generate_coordinates_ph():

    lat = random.uniform(7.823, 18.579)
    lng = random.uniform(118.975, 125.563)

    return [lat, lng]


def generate_area():

    print("GENERATE AREA FLAG")

    areas = ["National Capital Region", "Ilocos Region", "Cordillera Administrative Region", "Cagayan Valley",
                 "Central Luzon",
                 "Southern Tagalog Mainland", "Southwestern Tagalog Region", "Bicol Region", "Western Visayas",
                 "Central Visayas", "Eastern Visayas",
                 "Zamboanga Peninsula", "Northern Mindanao", "Davao Region", "SOCCSKSARGEN", "Caraga Region",
                 "Bangsamoro Autonomous Region"]

    for item in areas:
        area = Area.objects.create(name = item)
        area.save()


    return None


def generate_location():
    fake = Faker()
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

    if Area.objects.all() is None:
        generate_area()

    area_list = []
    for area in Area.objects.all():
        area_list.append(area)

    for item in CITY:
        place = fake.address() + " port"

        randomizer = random.randint(0, len(area_list) - 1)
        area = area_list[randomizer]

        coordinates = generate_coordinates_ph()

        location = Location.objects.create(area = area, place = place, city = item[0], latitude = coordinates[0], longtitude = coordinates[1])
        location.save()
        team = Team_Assignment.objects.create(location = location)
        team.save()


    return None


def generate_event():
    fake = Faker()

    if Area.objects.all() is None:
        generate_area()

    area_list = []
    for area in Area.objects.all():
        area_list.append(area)


    if Location.objects.all() is None:
        generate_location()

    location_list = []
    for location in Location.objects.all():
        location_list.append(location)


    for x in range(0, 150):
        print("Requester : " + fake.company())
        requester = fake.company()
        print("Cell Number : +63" + fake.msisdn()[:10])
        cell =  "+63" + fake.msisdn()[:10]

        randomizer = random.randint(0, 1)

        event_type = "?"
        k9s_required = 0
        if randomizer == 0:
            print("Event Type : Big Event")
            event_type = "Big Event"
            print("Number of K9s. Required : " + str(random.randint(6, 12)))
            k9s_required = random.randint(6, 12)

        else:
            print("Event Type : Small Event")
            event_type = "Small Event"
            print("Number of K9s. Required : " + str(random.randint(1, 5)))
            k9s_required = random.randint(2, 5)

        print("Location : " + fake.address())
        location = fake.address()
        print("City : " + generate_city_ph())
        city = generate_city_ph()
        print("Coordinates : " + str(generate_coordinates_ph()))
        coordinates = generate_coordinates_ph()

        start_date = fake.date_between(start_date="+10d", end_date="+60d")
        #start_date = generated_date.strftime("%m/%d/%Y")
        end_date = start_date + timedelta(days= random.randint(1, 14))
        #end_date = end_date.strftime("%m/%d/%Y")

        #print("Start Date : " + start_date)
        #print("End Date : " + end_date)

        print("Remarks : " + fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None))
        remarks = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)
        event_name = fake.sentence(nb_words=3, variable_nb_words=True, ext_word_list=None)
        print()

        email = requester.lower() + "@gmail.com"

        randomizer = random.randint(0, len(area_list) - 1)
        print("Area : " + str(area_list[randomizer]))
        area = area_list[randomizer]

        request = Dog_Request.objects.create(requester = requester, location = location, city = city, sector_type = event_type, phone_number = cell, email_address = email, event_name = event_name,
                                             remarks = remarks, area = area, k9s_needed = k9s_required, start_date = start_date, end_date = end_date, latitude = coordinates[0], longtitude = coordinates[1])
        request.save()

        if request.sector_type == "Big Event":
            request.status = "Approved"
            request.save()

    return None

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>END OF Requests and Locations CREATION



def generate_incident():
    fake = Faker()
    for x in range(0, 250):
        if User.objects.filter(position = "Handler") is None:
            generate_user()

        if Location.objects.all() is None:
            generate_location()

        user_list = []
        for user in User.objects.all():
            user_list.append(user)

        location_list = []
        for location in Location.objects.all():
            location_list.append(location)

        TYPE = (
            ('Explosives Related', 'Explosives Related'),
            ('Narcotics Related', 'Narcotics Related'),
            ('Search and Rescue Related', 'Search and Rescue Related'),
            )


        randomizer = random.randint(0, 2)

        type = TYPE[randomizer][0]

        randomizer = random.randint(0, len(user_list) - 1)
        user = user_list[randomizer]
        incident_txt = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)
        print("Incident : " + incident_txt)
        print("Recorded by : " + str(user))

        randomizer = random.randint(0, len(location_list) - 1)
        location = location_list[randomizer]
        print("Location : " + str(location))

        remarks = fake.paragraph(nb_sentences=2, variable_nb_sentences=True, ext_word_list=None)

        date = fake.date_between(start_date="-10y", end_date="-5y")

        incident = Incidents.objects.create(user = user, date = date, incident = incident_txt, location = location, type = type, remarks = remarks)
        incident.save()

    return None

def generate_maritime():
    fake = Faker()
    for x in range(0, 500):
        BOAT_TYPE = (
            ('Domestice Passenger Vessels', 'Domestice Passenger Vessels'),
            ('Motorbancas', 'Motorbancas'),
            ('Fastcrafts', 'Fastcrafts'),
            ('Cruise Ships', 'Cruise Ships'),
            ('Tugboat', 'Tugboat'),
            ('Barge', 'Barge'),
            ('Tanker', 'Tanker')
        )



        if Location.objects.all() is None:
            generate_location()

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

        passenger_count = random.randint(20, 100)

        maritime = Maritime.objects.create(location = location, boat_type = boat_type, datetime = date, passenger_count = passenger_count)

    return None

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>END OF Maritimes and Incidents CREATION

#TODO Fix K9.training_stage set at "Stage 0" regardless of training progress

#ADVANCED POPULATE>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#TODO Assign  a number of k9s to ports
#TODO assign a number of k9s to events(take into account the restrictions)

def generate_dogbreed():
   
    arr = ['Belgian Malinois','Dutch Sheperd','German Sheperd','Golden Retriever','Jack Russel','Labrador Retriever']

    temperament_list = ['Friendly', 'Skittish', 'Timid', 'Wild', 'Adventurous']
    skill_list = ['EDD','NDD','SAR']

    for data in arr:
        randomizer = random.randint(0, 4)
        randomizer2 = random.randint(0, 2)
        temperament = temperament_list[randomizer]
        skill = skill_list[randomizer2]

        random_val1 = random.randint(10000, 15000)
        random_val2 = random.randint(15000, 20000)
        litter_val = random.randint(4, 8)
        
        arr1 = ['EDD','NDD','SAR']
        arr2 = []
       
        while len(arr1) !=  0:
            randomizer2 = random.randint(0, 2)
            skill1 = skill_list[randomizer2]
            if skill1 in arr1:
                arr1.remove(skill1)
                arr2.append(skill1)
                
        print('ARRAY',arr2)

        Dog_Breed.objects.create(breed=data,sex='Male',life_span=10,temperament=temperament,colors=generate_skin_color(), weight=20,male_height=10,female_height=10,skill_recommendation=arr2[0],skill_recommendation2=arr2[1],skill_recommendation3=arr2[2],litter_number=litter_val,value=random_val1)

        Dog_Breed.objects.create(breed=data,sex='Female',life_span=10,temperament=temperament,colors=generate_skin_color(), weight=20,male_height=10,female_height=10,skill_recommendation=arr2[0],skill_recommendation2=arr2[1],skill_recommendation3=arr2[2],litter_number=litter_val,value=random_val2)

    return None


def assign_commander_random():

    if Area is None:
        generate_area()
    else:
        areas = Area.objects.all()
        commanders = User.objects.filter(position = "Commander")

        area_list = []
        for area in areas:
            area_list.append(area)

        commander_list = []
        for commander in commanders:
            commander_list.append(commander)

        commander_list = random.sample(commander_list, len(commander_list)-1)

        partnership = zip(commander_list, area_list)

        for item in partnership:
            area = item[1]
            area.commander = item[0]
            area.save()

    return None

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

def generate_team_name(location):
    team_name = ""

    x_list = re.split("\s", str(location.area))
    new_x = ""
    for x in x_list:
        print(x[0])
        new_x += x[0]

    team_name += new_x
    team_name += " Team "
    team_name += location.city
    team_name += " "

    return team_name

def fix_port_names():

    areas = Area.objects.all()

    for area in areas:
        locations = Location.objects.filter(area = area)

        city_list = []
        for location in locations:
            city_list.append(location.city)

        for city in city_list:
            locations = Location.objects.filter(city = city)
            ctr = 0
            for location in locations:
                letter_order = chr(ord('a') + ctr).capitalize()
                team = Team_Assignment.objects.get(location = location)
                team_name = generate_team_name(location)
                team_name += letter_order
                team.team = team_name
                team.save()
                ctr += 1

    return None

def create_predeployment_inventory():

    randomizer = random.randint(30, 100)
    collar = Miscellaneous.objects.create(miscellaneous = "Collar", misc_type = "Kennel Supply", uom = "pc", quantity = randomizer, price=199.12)
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
    food = Food.objects.create(food = "Pedigree", foodtype = "Adult Dog Food", unit = "kilograms", quantity=randomizer, price=120)

    randomizer = random.randint(50, 150)
    medicine = Medicine.objects.create(medicine = "Medicine Sample X", med_type = "Vitamins", uom = "mg", price=32.12)
    
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

    
    #Create Mandatory Vaccine and Prevention
    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='Rabies Immune Globulin', med_type='Vaccine', immunization='Anti-Rabies', price=randomizer)
    
    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='Bronchicine CAe', med_type='Vaccine', immunization='Bordetella Bronchiseptica Bacterin', price=randomizer)
    
    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='VANGUARD PLUS 5 L4 CV', med_type='Vaccine', immunization='DHPPiL+CV', price=randomizer)
    
    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='Versican Plus DHPPi/L4', med_type='Vaccine', immunization='DHPPiL4', price=randomizer)
    
    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='PetArmor Sure Shot 2x', med_type='Preventive', immunization='Deworming', price=randomizer)
    
    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='Heartgard', med_type='Preventive', immunization='Heartworm', price=randomizer)
    randomizer = random.randint(100, 1000)

    randomizer = random.randint(100, 1000)
    Medicine.objects.create(medicine='Frontline', med_type='Preventive', immunization='Tick and Flea', price=randomizer)

    return None

