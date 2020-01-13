from django.contrib.auth.models import User, Group
from manserver.api.models import *
from rest_framework import serializers

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class UserSerializer(serializers.HyperlinkedModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email', 'groups']

class StationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Station
        fields = ['id', 'latitude', 'longitude', 'name', 'trucks']
        depth = 1

class TruckSerializer(serializers.HyperlinkedModelSerializer):
    #station = StationSerializer(read_only=True)
    class Meta:
        model = Truck
        fields = ['id', 'latitude', 'longitude', 'strength', 'station', 'fire']

class SensorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sensor
        fields = ['id', 'posx', 'posy', 'latitude', 'longitude', 'fires']

class FireSerializer(serializers.HyperlinkedModelSerializer):
    #sensor = SensorSerializer(read_only=True)
    class Meta:
        model = Fire
        fields = ['id', 'latitude', 'longitude', 'intensity', 'radius', 'created', 'updated', 'sensor', 'trucks']