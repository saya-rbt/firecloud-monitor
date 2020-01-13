from django.contrib.auth.models import User, Group
from manserver.api.models import *
from rest_framework import viewsets
from manserver.api.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    @action(detail=False)
    def recent_users(self, request):
        recent_users = User.objects.all().order_by('-last_login')

        page = self.paginate_queryset(recent_users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recent_users, many=True)
        return Response(serializer.data)

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class StationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Station.objects.all()
    serializer_class = StationSerializer

class TruckViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    @action(detail=False)
    def available(self, request):
        available_trucks = Truck.objects.filter(fire__isnull=True).order_by('-strength')
        serializer = self.get_serializer(available_trucks, many=True)
        return Response(serializer.data)


class SensorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

    @action(detail=False)
    def active(self, request):
        active_sensors = Sensor.objects.filter(fires__intensity__gt=0).distinct()
        serializer = self.get_serializer(active_sensors, many=True)
        return Response(serializer.data)

class FireViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Fire.objects.all()
    serializer_class = FireSerializer

    @action(detail=False)
    def active(self, request):
        active_fires = Fire.objects.filter(intensity__gt=0).order_by('-intensity')
        serializer = self.get_serializer(active_fires, many=True)
        return Response(serializer.data)