from django.db import models

# Create your models here.
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
    created = models.DateTimeField(auto_now_add=True,)
    updated = models.DateTimeField(auto_now=True,)
    sensor = models.ForeignKey(Sensor, related_name='fires', on_delete=models.CASCADE)