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
    static public class AssignTrucksTask extends TimerTask {

        @Override
        public void run() {
            System.out.println("Move Trucks task started at:" + new Date());
            completeTask();
            System.out.println("Move Trucks finished at:" + new Date());
        }

        private void completeTask() {
            ApiHelper api = new ApiHelper();
            String jsonFires = "";
            String jsonTrucks = "";
            try {
                jsonFires = api.sendGet("http://192.168.0.10:8001/fires/active/");
                jsonTrucks = api.sendGet("http://192.168.0.10:8001/trucks/available/");
            } catch (Exception e) {
                e.printStackTrace();
            }

            Gson myGson = new Gson();
            Type empMapType = new TypeToken<ArrayList<Fire>>() {}.getType();
            ArrayList<Fire> fires = myGson.fromJson(jsonFires, empMapType);

            empMapType = new TypeToken<ArrayList<Truck>>() {}.getType();
            ArrayList<Truck> trucks = myGson.fromJson(jsonTrucks, empMapType);
            ArrayList<Truck> selectedTrucks = new ArrayList<>();
            ArrayList<Truck> remainingTrucks = new ArrayList<>(trucks);
            for (Fire fire : fires) {
                int strength = fire.intensity;
                if(fire.pending_strength + fire.intervention_strength > strength)
                    break;
                for (Truck truck : trucks){
                    if(truck.strength >= strength && remainingTrucks.contains(truck)){
                        truck.fireId = fire.id;
                        selectedTrucks.add(truck);
                        remainingTrucks.remove((truck));
                        break;
                    }
                    else if (truck.strength < strength && remainingTrucks.contains(truck)){
                        truck.fireId = fire.id;
                        strength -= truck.strength;
                        selectedTrucks.add(truck);
                        remainingTrucks.remove((truck));
                    }

                    if(strength <= 0){
                        break;
                    }
                }
            }
            System.out.print(selectedTrucks.size());
            for(Truck truck : selectedTrucks){
                Map<Object, Object> data = new HashMap<>();
                data.put("name", truck.name);
                data.put("strength", truck.strength);
                data.put("latitude", truck.latitude);
                data.put("longitude", truck.longitude);
                data.put("station", truck.station);
                data.put("fire", "http://192.168.0.10:8001/fires/" + truck.fireId + "/");

                try {
                    api.sendPut(data, "http://192.168.0.10:8001/trucks/" + truck.id + "/");
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }

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
                api.sendGet("/fires/");
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
        TimerTask assignTrucks = new AssignTrucksTask();
        //TimerTask createFires = new CreateFiresTask();
        //TimerTask updateFires = new UpdateFiresTask();
        tim.scheduleAtFixedRate(assignTrucks, 0, 5000);
        //tim.scheduleAtFixedRate(createFires, 0, 10000);
        //tim.scheduleAtFixedRate(updateFires, 0, 1000);
        while(true){

        }
        //tim.cancel();
    }
}