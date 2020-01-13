package com.firecloud;

public class Truck extends Entity{
    /*
    name = models.CharField(max_length=50, default="")
    latitude = models.FloatField()
    longitude = models.FloatField()
    strength = models.IntegerField()
    station = models.ForeignKey(Station, related_name='trucks', on_delete=models.CASCADE)
    fire = models.ForeignKey(Fire, related_name='trucks', on_delete=models.CASCADE, null=True, blank=True )
     */

    String name ="";
    int strength;
    int fireId;
    String station;

}
