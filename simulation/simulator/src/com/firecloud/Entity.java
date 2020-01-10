package com.firecloud;

public class Entity {
    float latitude = 0;
    float longitude = 0;

    public void move(float pLong, float pLat){
        latitude = pLat;
        longitude = pLong;
    }
}
