from rest_framework import serializers
from .models import Data, Sensor

class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = ('macAddress', 'humidity', 'temperature')

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ('__all__')
