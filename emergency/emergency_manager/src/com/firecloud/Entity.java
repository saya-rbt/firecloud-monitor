package com.firecloud;

public class Entity {
    int id;
    float latitude = 0;
    float longitude = 0;

    public void move(int pId, float pLong, float pLat){
        id = pId;
        latitude = pLat;
        longitude = pLong;
    }
}
