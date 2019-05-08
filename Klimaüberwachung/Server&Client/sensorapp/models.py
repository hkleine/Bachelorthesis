from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from sensorapp.enums import *
from datetime import date

# ORM-Klassen, welche die Tabellen für die Datenbank darstellen.

# Dies ist eine Erweiterung des schon vorhandenen User-Objekts.
class User(AbstractUser):
    gender = models.CharField(verbose_name='Gender', max_length=255, choices=GENDER_CHOICES, default='O', null=True, blank=True)
    birthday = models.DateField(null=True, blank=True, default=date(1900, 1, 2))
    accepted_agbs = models.BooleanField(default=True)

# Sensor (Room)
class Sensor(models.Model):
    roomName =  models.CharField(max_length=20, unique=True, null=True, blank=True)
    roomType =  models.CharField(choices=ROOM_CHOICES, default='Livingroom', null=True, blank=True, max_length=255)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    macAddress = models.CharField(primary_key=True, max_length=17, unique=True)
    token = models.CharField(max_length=30, blank=True)
    state = models.CharField(verbose_name='State', max_length=255, choices=SENSOR_STATES, default='0', null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

# Messwert
class Data(models.Model):
    dataID = models.AutoField(primary_key=True)
    macAddress = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    humidity = models.FloatField()
    temperature = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
