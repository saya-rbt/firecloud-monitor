from django.db import models

# Create your models here.

class Station(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    name = models.CharField(max_length=100)
    def __str__(self):
        return '%s' % (self.name)

class Sensor(models.Model):
    posx = models.IntegerField()
    posy = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    class Meta:
        unique_together = ('posx', 'posy')

    def __str__(self):
        return '(%d,%d)' % (self.posx, self.posy)

class Fire(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    intensity = models.IntegerField()
    radius = models.FloatField()
    startdate = models.DateTimeField(auto_now_add=True,)
    sensor = models.ForeignKey(Sensor, related_name='fires', on_delete=models.CASCADE)

class Truck(models.Model):
    name = models.CharField(max_length=50, default="")
    latitude = models.FloatField()
    longitude = models.FloatField()
    strength = models.IntegerField()
    station = models.ForeignKey(Station, related_name='trucks', on_delete=models.CASCADE)
    fires = models.ManyToManyField(Fire)