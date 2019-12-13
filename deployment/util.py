import datetime
from datetime import datetime, timedelta, date
from calendar import HTMLCalendar
import calendar

from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.utils.safestring import mark_safe

from deployment.models import Dog_Request, K9_Schedule
from planningandacquiring.models import K9
from django.db.models import Q

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, day, events):
        events_per_day = events.filter(Q(start_date__day__lte=day) & Q(end_date__day__gte=day))
        d = ''
        for event in events_per_day:
            link1 = '<a class = "ui button" href= "'
            link2 = 'deployment/request_dog_details/'
            link3 = '">'
            link = link1 + link2 + str(event.id) + link3
            d += f'<li> {link}{event} </a> </li>'

        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    # formats a week as a tr
    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
        #events = Event.objects.filter(start_time__year=self.year, start_time__month=self.month)
        events = Dog_Request.objects.filter(status="Approved").filter(start_date__year=self.year, start_date__month=self.month)
        print(self.year)
        print(self.month)

        print("EVENTS TEST")
        print(events)
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        return cal

class Calendar_Detailed(HTMLCalendar):
    def __init__(self, year=None, month=None, k9_id=None):
        self.year = year
        self.month = month
        self.k9_id = k9_id
        super(Calendar_Detailed, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, day, events):
        events_per_day = events.filter(Q(date_start__day__lte=day) & Q(date_end__day__gte=day))
        d = ''
        for event in events_per_day:
            dog_request = Dog_Request.objects.get(id = event.dog_request.id)
            link1 = '<a class = "ui button" href= "'
            link2 = 'deployment/request_dog_details/'
            link3 = '">'
            link = link1 + link2 + str(dog_request.id) + link3
            d += f'<li> {link}{dog_request} </a> </li>'

        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    # formats a week as a tr
    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
        k9 = K9.objects.get(id = self.k9_id)
        #events = Event.objects.filter(start_time__year=self.year, start_time__month=self.month)
        events = K9_Schedule.objects.filter(k9=k9).filter(date_start__year=self.year, date_end__month=self.month)
        print(self.year)
        print(self.month)

        print("EVENTS TEST")
        print(events)
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        return cal

def get_date(req_day):
    print("GET DAY TEST")
    print(req_day)
    if req_day:
        req_day = str(req_day)
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def select_month(d):
    new_date = datetime.strptime(d, "%Y-%m-%d").date()
    month = str(new_date.year) + '-' + str(new_date.month)

    print("TEST SELECT MONTh")
    print(month)
    return month
