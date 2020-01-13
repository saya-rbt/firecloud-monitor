from django.contrib.auth.models import User, Group
from simserver.api.models import *
from rest_framework import viewsets
from simserver.api.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

class FireFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = User
        fields = {
            'sensor__posx': ['exact'],
            'sensor__poxy': ['exact'],
        }

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

class SensorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

    @action(detail=False)
    def inactive(self, request):
        inactive_sensors = Sensor.objects.filter(Q(fires__isnull=True) | Q(fires__intensity=0)).distinct()
        serializer = self.get_serializer(inactive_sensors, many=True)
        return Response(serializer.data)

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
    filter_backends = [DjangoFilterBackend]
    filterset_class = FireFilter

    @action(detail=False)
    def active(self, request):
        active_fires = Fire.objects.filter(intensity__gt=0).order_by('-intensity')
        serializer = self.get_serializer(active_fires, many=True)
        return Response(serializer.data)