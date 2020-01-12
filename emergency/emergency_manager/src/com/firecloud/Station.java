package com.firecloud;

public class Station extends Entity {
    int longitude;
    int latitude;
    String name;

    public Station(int pLongitude, int pLatitude, String pName){
        longitude = pLongitude;
        latitude = pLatitude;
        name = pName;
    }
}
