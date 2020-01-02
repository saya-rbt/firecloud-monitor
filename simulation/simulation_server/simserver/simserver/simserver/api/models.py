from django.db import models

# Create your models here.

class Station(models.Model):
    position = models.CharField(max_length=20)
    name = models.CharField(max_length=100)

class Truck(models.Model):
    position = models.CharField(max_length=20)
    strength = models.IntegerField()
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
