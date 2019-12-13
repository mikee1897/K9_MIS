from __future__ import absolute_import, unicode_literals
from celery import shared_task, task
import time
from K9_insys.celery import app
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from datetime import timedelta, date, datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta

# @periodic_task(run_every=crontab(hour=9, minute=0))
# def test():
#    Notification.objects.create(message='meassage sent')
       
