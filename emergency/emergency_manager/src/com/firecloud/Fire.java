package com.firecloud;

import java.util.Date;

public class Fire extends Entity {
    /*
    latitude = models.FloatField()
    longitude = models.FloatField()
    intensity = models.IntegerField()
    radius = models.FloatField()
    created = models.DateTimeField(auto_now_add=True,)
    updated = models.DateTimeField(auto_now=True,)
    sensor = models.ForeignKey(Sensor, related_name='fires', on_delete=models.CASCADE)
     */

    int intensity;
    int sensorId;
    int intervention_strength;

    public Fire(int pIntensity, int pSensor, float pLongitude, float pLatitude){
        intensity = pIntensity;
        sensorId = pSensor;
        longitude = pLongitude;
        latitude = pLatitude;
    }
}
