from django.contrib import admin
from .models import Sensor, Data, User

class DataAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Data._meta.get_fields()]

admin.site.register(Sensor)
admin.site.register(Data, DataAdmin)
admin.site.register(User)
