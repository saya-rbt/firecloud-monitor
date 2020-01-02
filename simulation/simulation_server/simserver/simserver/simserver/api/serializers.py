from django.contrib.auth.models import User, Group
from simserver.api.models import Station, Truck
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['name']

class StationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Station
        fields = ['position', 'name']

class TruckSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Truck
        fields = ['position', 'strength', 'station']