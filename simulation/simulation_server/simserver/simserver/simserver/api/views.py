from django.contrib.auth.models import User, Group
from simserver.api.models import Station, Truck
from rest_framework import viewsets
from simserver.api.serializers import UserSerializer, GroupSerializer, StationSerializer, TruckSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

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