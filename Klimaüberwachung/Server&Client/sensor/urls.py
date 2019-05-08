from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import include

urlpatterns = [
    url(r'', include('sensorapp.urls')),
]
