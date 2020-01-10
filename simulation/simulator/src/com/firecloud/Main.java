package com.firecloud;
import com.firecloud.Fire;
import com.firecloud.Sensor;

import java.io.IOException;
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

            try {
                api.sendGet();
            } catch (Exception e) {
                e.printStackTrace();
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
            Map<Object, Object> data = new HashMap<>();
            data.put("latitude", "10");
            data.put("longitude", "10");
            data.put("intensity", "1");
            data.put("radius", "0");
            data.put("sensor", "http://192.168.0.10:8001/sensors/1/");
            try {
                api.sendPost(data, "http://192.168.0.10:8001/fires/");
            } catch (Exception e) {
                e.printStackTrace();
            }


            try {
                //assuming it takes 20 secs to complete the task
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
    public static void main(String[] args) {
        System.out.print("Hello World !");

        Map<Object, Object> data = new HashMap<>();
        data.put("latitude", "10");
        data.put("longitude", "10");
        data.put("posx", "10");
        data.put("posy", "10");

        ApiHelper api = new ApiHelper();

        try {
            api.sendPost(data, "http://192.168.0.10:8001/sensors/");
        } catch (Exception e) {
            e.printStackTrace();
        }


        Timer tim = new Timer();
        TimerTask moveTrucks = new MoveTrucksTask();
        TimerTask createFires = new CreateFiresTask();
        TimerTask updateFires = new UpdateFiresTask();
        //tim.scheduleAtFixedRate(moveTrucks, 0, 1000);
        tim.scheduleAtFixedRate(createFires, 0, 10000);
        //tim.scheduleAtFixedRate(updateFires, 0, 1000);

        try {
            Thread.sleep(10000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        //tim.cancel();
    }
}