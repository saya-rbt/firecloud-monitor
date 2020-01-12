package com.firecloud;

public class Fire extends Entity {
    int intensity;
    Sensor sensor;

    public Fire(Sensor pSensor){
        sensor = pSensor;
    }
}
