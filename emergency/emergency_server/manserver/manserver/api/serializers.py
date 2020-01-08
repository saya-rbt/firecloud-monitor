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
        fields = ['id', 'username', 'email', 'groups']

class SensorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sensor
        fields = ['id', 'posx', 'posy', 'latitude', 'longitude', 'state', 'fires']

class FireSerializer(serializers.HyperlinkedModelSerializer):
    #sensor = SensorSerializer(read_only=True)
    class Meta:
        model = Fire
        fields = ['id', 'latitude', 'longitude', 'intensity', 'radius', 'startdate', 'sensor']
        depth=1