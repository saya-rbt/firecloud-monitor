package com.firecloud;
import com.firecloud.Fire;
import com.firecloud.Sensor;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.io.IOException;
import java.lang.reflect.Array;
import java.lang.reflect.Type;
import java.util.*;


import java.util.Timer;

public class Main {
    static public class MoveTrucksTask extends TimerTask {

        @Override
        public void run() {
            System.out.println("Move Trucks task started at:" + new Date());
            completeTask();
            System.out.println("Move Trucks finished at:" + new Date());
        }

        private void completeTask() {
            try {
                //assuming it takes 20 secs to complete the task
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
    static public class UpdateFiresTask extends TimerTask {

        @Override
        public void run() {
            System.out.println("Update Fires task started at:" + new Date());
            completeTask();
            System.out.println("Update Fires task finished at:" + new Date());
        }

        private void completeTask() {
            ApiHelper api = new ApiHelper();
            String json = "";
            try {
                json = api.sendGet("http://192.168.0.10:8000/fires/active/");
            } catch (Exception e) {
                e.printStackTrace();
            }

            Gson myGson = new Gson();
            Type empMapType = new TypeToken<ArrayList<Fire>>() {}.getType();
            ArrayList<Fire> fires = myGson.fromJson(json, empMapType);
            for(Fire fire : fires){
                if(fire.intervention_strength >= fire.intensity){
                    fire.intensity--;
                }
            }

            for(Fire fire : fires){
                Map<Object, Object> data = new HashMap<>();
                data.put("latitude", fire.latitude);
                data.put("longitude", fire.longitude);
                data.put("intensity", fire.intensity);
                data.put("radius", fire.radius);
                data.put("sensor", fire.sensor);

                try {
                    api.sendPut(data, "http://192.168.0.10:8000/trucks/" + truck.id + "/");
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
            try {
                //assuming it takes 20 secs to complete the task
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
    static public class CreateFiresTask extends TimerTask {

        @Override
        public void run() {
            System.out.println("Fire Created task started at:" + new Date());
            completeTask();
            System.out.println("Fire Created task finished at:" + new Date());
        }

        private void completeTask() {
            ApiHelper api = new ApiHelper();
            String json = "";
            try {
                json = api.sendGet("http://192.168.0.10:8000/sensors/inactive/");
            } catch (Exception e) {
                e.printStackTrace();
            }

            Gson myGson = new Gson();
            Type empMapType = new TypeToken<Sensor[]>() {}.getType();
            Sensor[] sensors = myGson.fromJson(json, empMapType);
            if(sensors.length == 0)
                return;

            for (Sensor value : sensors) {
                System.out.print(value.id + " "
                        + value.posx + " "
                        + value.posy + " "
                        + value.latitude + " "
                        + value.longitude + " ");
                System.out.print("\n");
            }

            Random rand = new Random();
            Sensor sensor = sensors[rand.nextInt(((sensors.length - 1)) + 1)];
            Map<Object, Object> data = new HashMap<>();
            data.put("latitude", sensor.latitude);
            data.put("longitude", sensor.longitude);
            data.put("intensity", rand.nextInt((10 - 1) + 1) + 1);
            data.put("radius", "0");
            data.put("sensor", "/sensors/" + sensor.id + "/");
            try {
                api.sendPost(data, "http://192.168.0.10:8000/fires/");
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
    public static void main(String[] args) {
        System.out.print("Hello World !");

        Timer tim = new Timer();
        TimerTask moveTrucks = new MoveTrucksTask();
        TimerTask createFires = new CreateFiresTask();
        TimerTask updateFires = new UpdateFiresTask();
        //tim.scheduleAtFixedRate(moveTrucks, 0, 1000);
        //tim.scheduleAtFixedRate(createFires, 0, 10000);
        tim.scheduleAtFixedRate(updateFires, 0, 1000);

        try {
            Thread.sleep(10000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        //tim.cancel();
    }
}