from django.db import models
# from planningandacquiring.models import K9
# from inventory.models import Food, Medicine_Inventory
from profiles.models import User
from datetime import timedelta, date, datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
import re
from django.utils import timezone

# Create your models here.
class Area(models.Model):
    name = models.CharField('name', max_length=150, default='')
    commander = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Location(models.Model):

    TYPE = (
        ('Mall', 'Mall'),
        ('Airport', 'Airport'),
        ('Government Building', 'Government Building')
    )

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
        ('Zamboanga', 'Zamboanga'),
    )
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    place = models.CharField('place', max_length=500, default='Undefined')
    city = models.CharField('city', choices=CITY, max_length=100, default='None')
    #sector_type = models.CharField('sector_type', choices=TYPE, max_length=100, null=True, blank=True)
    status = models.CharField('status', max_length=100, default="unassigned")
    longtitude = models.DecimalField('longtitude', max_digits=50, decimal_places=4, null=True)
    latitude = models.DecimalField('latitude', max_digits=50, decimal_places=4, null=True)

    def __str__(self):
        return str(self.area) + ' : ' + ' - ' + str(self.place)

class Team_Assignment(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    team_leader =  models.ForeignKey(User, on_delete=models.CASCADE,  null=True, blank=True)
    team = models.CharField('team', max_length=100)
    EDD_demand = models.IntegerField('EDD_demand', default=2)
    NDD_demand = models.IntegerField('NDD_demand', default=2)
    SAR_demand = models.IntegerField('SAR_demand', default=1)
    EDD_deployed = models.IntegerField('EDD_deployed', default=0)
    NDD_deployed = models.IntegerField('NDD_deployed', default=0)
    SAR_deployed = models.IntegerField('SAR_deployed', default=0)
    total_dogs_demand = models.IntegerField('total_dogs_demand', default=0)
    total_dogs_deployed = models.IntegerField('total_dogs_deployed', default=0)
    date_added = models.DateField('date_added', auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.team)

    def generate_team_name(self):
        team_name = ""

        location = self.location
        x_list = re.split("\s", str(location.area))
        new_x = ""
        for x in x_list:
            print(x[0])
            new_x += x[0]

        team_name += new_x
        team_name += "-"
        team_name += location.city
        team_name += "-"

        words = location.place.split(",")
        team_name += words[0]

        return team_name


    def save(self, *args, **kwargs):
        self.total_dogs_demand = int(self.EDD_demand) + int(self.NDD_demand) + int(self.SAR_demand)
        self.total_dogs_deployed = int(self.EDD_deployed) + int(self.NDD_deployed) + int(self.SAR_deployed)

        if self.location:
            self.team = self.generate_team_name()

        super(Team_Assignment, self).save(*args, **kwargs)

class Dog_Request(models.Model):
    TYPE = (
        # ('Disaster', 'Disaster'),
        # ('Annual Event', 'Annual Event'),
        ('Big Event', 'Big Event'),
        ('Small Event', 'Small Event'),
    )

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
        ('Zamboanga', 'Zamboanga'),
    )

    requester = models.CharField('requester', max_length=100)
    event_name = models.CharField('event_name', max_length=100)
    location = models.CharField('location', max_length=300)
    city = models.CharField('city', choices=CITY, max_length=100, default="Manila")
    sector_type = models.CharField('sector_type', choices=TYPE, max_length=100, null=True, blank=True)
    phone_number = models.CharField('phone_number', max_length=100, default="n/a")
    email_address = models.EmailField('email', max_length=100, blank=True, null=True)
    remarks = models.CharField('remarks', max_length=500, blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    k9s_needed = models.IntegerField('k9s_needed', default=0)
    k9s_deployed = models.IntegerField('k9s_deployed', default=0)
    start_date = models.DateField('start_date', null=True, blank=True)
    end_date = models.DateField('end_date', null=True, blank=True)
    status = models.CharField('status', max_length=100, default="Pending")
    longtitude = models.DecimalField('longtitude', max_digits=50, decimal_places=4, null=True)
    latitude = models.DecimalField('latitude', max_digits=50, decimal_places=4, null=True)
    team_leader = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def due_start(self):
        notif = self.date_start - timedelta(days=7)
        return notif

    def due_end(self):
        notif = self.date_end - timedelta(days=7)
        return notif

    def duration(self):
        delta = self.end_date - self.start_date
        return delta.days

    def __str__(self):
        return str(self.requester) + ' - ' + str(self.location)

    # def save(self, *args, **kwargs):
    #     super(Dog_Request, self).save(*args, **kwargs)

#TODO retain or remove deployed
class Team_Dog_Deployed(models.Model):
    team_assignment = models.ForeignKey(Team_Assignment, on_delete=models.CASCADE, blank=True, null=True)
    team_requested = models.ForeignKey(Dog_Request, on_delete=models.CASCADE, blank=True, null=True) #Dog Rquest
    k9 = models.ForeignKey('planningandacquiring.K9', on_delete=models.CASCADE, null=True, blank=True)
    handler = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField('status', max_length=100, null=True, blank=True, default='Deployed')
    date_added = models.DateField('date_added', default=timezone.now, null=True, blank=True)
    date_pulled = models.DateField('date_pulled' , null=True, blank=True)

    def __str__(self):
        return str(self.k9) + ' - ' + str(self.team_assignment)

    def save(self, *args, **kwargs):
        self.handler = self.k9.handler
        if self.status == 'Deployed':
            # k9 = K9.objects.get(id=self.k9.id)
            self.k9.training_status = 'Deployed'
            self.k9.assignment = str(self.team_assignment)
            self.k9.save()
            try:
                ta = Team_Assignment.objects.get(id=self.team_assignment)
                if self.k9.capability == 'EDD':
                    ta.EDD_deployed = ta.EDD_deployed + 1
                elif self.k9.capability == 'NDD':
                    ta.EDD_deployed = ta.NDD_deployed + 1
                else:
                    ta.EDD_deployed = ta.SAR_deployed + 1
                ta.save()
            except:
                pass
        super(Team_Dog_Deployed, self).save(*args, **kwargs)

class K9_Schedule(models.Model):
    CHOICES = (
        ('Initial Deployment', 'Initial Deployment'),
        ('Checkup', 'Checkup'),
        ('Request', 'Request'),
        ('Arrival', 'Arrival')
    )

    k9 = models.ForeignKey('planningandacquiring.K9', on_delete=models.CASCADE, null=True, blank=True)
    dog_request = models.ForeignKey(Dog_Request, on_delete=models.CASCADE, null=True, blank=True)
    team = models.ForeignKey(Team_Assignment, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField('status', choices=CHOICES, max_length=100, null=True, blank=True, default='Pending')
    date_start = models.DateField('date_start', null=True, blank=True)
    date_end = models.DateField('date_end', null=True, blank=True)

    def due_start(self):
        notif = self.date_start - timedelta(days=7)
        return notif

    def due_end(self):
        notif = self.date_end - timedelta(days=7)
        return notif

    def __str__(self):
        return str(self.k9) + " : " + str(self.date_start) + " - " + str(self.date_end)

    def save(self, *args, **kwargs):
        if self.dog_request:
            self.date_start = self.dog_request.start_date
            self.date_end = self.dog_request.end_date
        super(K9_Schedule, self).save(*args, **kwargs)

class Incidents(models.Model):
    TYPE = (
        ('Explosives Related', 'Explosives Related'),
        ('Narcotics Related', 'Narcotics Related'),
        ('Search and Rescue Related', 'Search and Rescue Related'),
        ('Others', 'Others'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField('date', null=True, blank=True)
    incident = models.CharField('incident', max_length=100, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField('type', choices=TYPE, max_length=100, default='Others')
    remarks = models.TextField('remarks', max_length=500, blank=True, null=True)

    def __str__(self):
        return str(self.type) + " : " + str(self.date)

class Maritime(models.Model):
    BOAT_TYPE = (
        ('Domestice Passenger Vessels', 'Domestice Passenger Vessels'),
        ('Motorbancas', 'Motorbancas'),
        ('Fastcrafts', 'Fastcrafts'),
        ('Cruise Ships', 'Cruise Ships'),
        ('Tugboat', 'Tugboat'),
        ('Barge', 'Barge'),
        ('Tanker', 'Tanker')
    )

    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    boat_type = models.CharField('boat_type', choices=BOAT_TYPE, max_length=100, default='Others')
    date = models.DateField('date', null=True, blank=True)
    time = models.TimeField('time', null=True, blank=True)
    passenger_count = models.IntegerField('passenger_count', blank=True, null=True, default = 0)
    
    def save(self, *args, **kwargs):
        if self.date == None:
            self.date = date.today()
        super(Maritime, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.date)

class Daily_Refresher(models.Model):

    MAR = (
        ('MARSEC', 'MARSEC'),
        ('MARLEN', 'MARLEN'),
        ('MARSAR', 'MARSAR'),
        ('MAREP', 'MAREP')
    )

    k9 = models.ForeignKey('planningandacquiring.K9', on_delete=models.CASCADE)
    handler = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField('date', null=True, blank=True)
    rating = models.DecimalField('rating', max_length=200, blank=True, null=True, decimal_places=2, max_digits=10)
    on_leash = models.BooleanField(default=False)
    off_leash = models.BooleanField(default=False)
    obstacle_course = models.BooleanField(default=False)
    panelling = models.BooleanField(default=False)
    morning_feed_cups = models.DecimalField('morning_feed_cups', blank=True, null=True, decimal_places=2, max_digits=10)
    evening_feed_cups = models.DecimalField('evening_feed_cups', blank=True, null=True, decimal_places=2, max_digits=10)
    # plant and find
    port_plant = models.IntegerField('port_plant', blank=True, null=True, default=0)
    port_find = models.IntegerField('port_find', blank=True, null=True,default=0)
    port_time = models.TimeField('port_time', blank=True, null=True)
    building_plant = models.IntegerField('building_plant',blank=True, null=True,default=0)
    building_find = models.IntegerField('building_find', blank=True, null=True,default=0)
    building_time = models.TimeField('building_time', blank=True, null=True)
    vehicle_plant = models.IntegerField('vehicle_plant', blank=True, null=True,default=0)
    vehicle_find = models.IntegerField('vehicle_find',blank=True, null=True,default=0)
    vehicle_time = models.TimeField('vehicle_time', blank=True, null=True)
    baggage_plant = models.IntegerField('baggage_plant', blank=True, null=True,default=0)
    baggage_find = models.IntegerField('baggage_find', blank=True, null=True,default=0)
    baggage_time = models.TimeField('baggage_time', blank=True, null=True)
    others_plant = models.IntegerField('others_plant', blank=True, null=True,default=0)
    others_find = models.IntegerField('others_find', blank=True, null=True,default=0)
    others_time = models.TimeField('others_time', blank=True, null=True)
    mar =  models.CharField('mar', choices=MAR, max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
         
        find = (self.port_find+self.building_find+self.vehicle_find+self.baggage_find+self.others_find)
        plant = (self.port_plant+self.building_plant+self.vehicle_plant+self.baggage_plant+self.others_plant)
        self.rating = 100 - ((plant - find) * 5)

        if self.date == None:
            self.date = date.today()
        super(Daily_Refresher, self).save(*args, **kwargs)



class TempDeployment(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    k9 = models.ForeignKey('planningandacquiring.K9', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.k9) + ' - ' + str(self.location)

class TempCheckup(models.Model):
    k9 = models.ForeignKey('planningandacquiring.K9', on_delete=models.CASCADE)
    date = models.DateField('date', null=True, blank=True)
    deployment_date = models.DateField('deployment_date', null=True, blank=True)

    def __str__(self):
        return str(self.k9)



#TODO 1 isntance lang per k9, if bumalik pcg idelete yung luma
class K9_Pre_Deployment_Items(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Done', 'Done')
    )

    k9 = models.ForeignKey('planningandacquiring.K9', on_delete=models.CASCADE, null=True, blank=True, related_name='k9_pre_requirement')
    initial_sched = models.ForeignKey(K9_Schedule, on_delete=models.CASCADE, null=True, blank=True, related_name='sched_pre_requirement')
    phex = models.ForeignKey('unitmanagement.PhysicalExam', on_delete=models.CASCADE, null=True, blank=True, related_name='phex_pre_requirement')
    food = models.ForeignKey('inventory.Food', on_delete=models.CASCADE, null=True, blank=True, related_name='food_pre_requirement')
    vitamins = models.ForeignKey('inventory.Medicine_Inventory', on_delete=models.CASCADE, null=True, blank=True, related_name='vitamins_pre_requirement')
    collar = models.IntegerField('collar', default=0)
    vest = models.IntegerField('vest', default=0)
    leash = models.IntegerField('leash', default=0)
    shipping_crate = models.IntegerField('shipping crate', default=0)
    food_quantity = models.IntegerField('food_quantity', default=0)
    vitamins_quantity = models.IntegerField('vitamins_quantity', default=0)
    grooming_kit = models.IntegerField('grooming_kit', default=0)
    first_aid_kit = models.IntegerField('first_aid_kit', default=0)
    oral_dextrose = models.IntegerField('oral_dextrose', default=0)
    ball = models.IntegerField('ball,.', default=0)
    status = models.CharField('status', max_length=100, choices=STATUS, default='Pending')


    def __str__(self):
        return str(self.initial_sched) + "( " + str(self.status) + " )"

    def remove_old_instance(self):

        try:
            recent = K9_Pre_Deployment_Items.objects.filter(k9 = self.k9).latest()
            old_instances = K9_Pre_Deployment_Items.objects.exclude(recent)
            old_instances.delete()
        except:
            pass

        return None


    def save(self, *args, **kwargs):

        self.remove_old_instance()

        super(K9_Pre_Deployment_Items, self).save(*args, **kwargs)

# #TODO K9 SCHEDULE
# @receiver(post_save, sender=K9_Schedule)
# def create_k9_sched_notif(sender, instance, **kwargs):
#     if kwargs.get('created', False):
#         if instance.status ==