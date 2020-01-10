package com.firecloud;
import com.firecloud.Fire;
import com.firecloud.Sensor;

import java.io.IOException;
import java.util.Date;
import java.util.Timer;
import java.util.TimerTask;


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

            try {
                api.sendPost();
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