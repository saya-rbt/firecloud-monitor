from django.contrib.auth.models import User, Group
from manserver.api.models import *
from rest_framework import serializers
from django.db.models import Sum

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
        depth=1

class FireSerializer(serializers.HyperlinkedModelSerializer):
    #sensor = SensorSerializer(read_only=True)
    intervention_strength = serializers.SerializerMethodField()
    pending_strength = serializers.SerializerMethodField()
    class Meta:
        model = Fire
        fields = ['id', 'latitude', 'longitude', 'intensity', 'radius', 'created', 'updated', 'sensor', 'trucks', 'intervention_strength', 'pending_strength']

    def get_intervention_strength(self, obj):
        return Truck.objects.filter(fire__id=obj.id, latitude=obj.latitude, longitude=obj.latitude).aggregate(Sum('strength')).get('strength__sum')
    def get_pending_strength(self, obj):
        return Truck.objects.filter(fire__id=obj.id).exclude(latitude=obj.latitude, longitude=obj.latitude).aggregate(Sum('strength')).get('strength__sum')
        