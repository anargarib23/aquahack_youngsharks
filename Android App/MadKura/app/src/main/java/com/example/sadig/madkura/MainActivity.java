package com.example.sadig.madkura;


import android.content.Context;
import android.os.AsyncTask;
import android.os.Bundle;

import android.os.Handler;
import android.os.Looper;
import android.support.annotation.Nullable;
import android.support.design.widget.TabLayout;
import android.support.v7.app.AppCompatActivity;

import android.util.JsonReader;
import android.util.JsonToken;
import android.util.Log;
import android.view.View;
import android.webkit.WebView;

import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;


import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;


public class MainActivity extends AppCompatActivity {

    public static String JSON = "";
    public int seconds2refresh = 5;

    public void toast(CharSequence name) {
        Toast toast = Toast.makeText(getApplicationContext(),
                name,
                Toast.LENGTH_SHORT);
        toast.show();
    }

    public void initMap() {
        WebView webview;
        webview = (WebView) findViewById(R.id.webview);
        webview.getSettings().setJavaScriptEnabled(true);
        String html = "<div style=\"width: 100%; \"><iframe width=\"102%\" height=\"101%\" frameborder=\"0\" scrolling=\"no\" marginheight=\"0\" marginwidth=\"0\" src=\"https://www.google.com/maps/d/embed?mid=1Y3zTHKIvKmYDjlGu7buY_uUbVQo7jEq_\"></iframe></div>";
        webview.loadData(html, "text/html", null);
    }

    //this method is actually fetching the json string
    private void getJSON(final String urlWebService) {
        /*
         * As fetching the json string is a network operation
         * And we cannot perform a network operation in main thread
         * so we need an AsyncTask
         * The constrains defined here are
         * Void -> We are not passing anything
         * Void -> Nothing at progress update as well
         * String -> After completion it should return a string and it will be the json string
         * */
        class GetJSON extends AsyncTask<Void, Void, String> {

            //this method will be called before execution
            //you can display a progress bar or something
            //so that user can understand that he should wait
            //as network operation may take some time
            @Override
            protected void onPreExecute() {
                super.onPreExecute();
            }

            //this method will be called after execution
            //so here we are displaying a toast with the json string
            @Override
            protected void onPostExecute(String s) {
                super.onPostExecute(s);
//                Toast.makeText(getApplicationContext(), s, Toast.LENGTH_SHORT).show();
                JSON = s;
            }

            //in this method we are fetching the json string
            @Override
            protected String doInBackground(Void... voids) {


                try {
                    //creating a URL
                    URL url = new URL(urlWebService);

                    //Opening the URL using HttpURLConnection
                    HttpURLConnection con = (HttpURLConnection) url.openConnection();

                    //StringBuilder object to read the string from the service
                    StringBuilder sb = new StringBuilder();

                    //We will use a buffered reader to read the string from service
                    BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(con.getInputStream()));

                    //A simple string to read values from each line
                    String json;

                    //reading until we don't find null
                    while ((json = bufferedReader.readLine()) != null) {

                        //appending it to string builder
                        sb.append(json + "\n");
                    }

                    //finally returning the read string
                    return sb.toString().trim();
                } catch (Exception e) {
                    return null;
                }

            }
        }

        //creating asynctask object and executing it
        GetJSON getJSON = new GetJSON();
        getJSON.execute();
    }

//    public void refresh() {
//        numOfDevices = Integer.parseInt(queryServer("http://askmeair.com/aquahack/device-count").toString());
//        responses = new JSONObject[numOfDevices];
//        for (int i = 0; i < numOfDevices; i++) {
//            // get details
//            responses[i] = queryServer("http://askmeair.com/aquahack/api?device=" + i);
//
//            // flag for status
//            boolean statusON = parseValue(responses[i], "status").equals("on");
//
//        }
//    }

    public void sleep(long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {

        }
    }

    public String getJsonString(JSONObject obj, String str) {
        try {
            return obj.getString(str);
        } catch (Exception e) {

        }
        return null;
    }


    //http://askmeair.com/aquahack/device-count
//    http://askmeair.com/aquahack/api?device=1


    int textViewIDs[] = {R.id.date, R.id.lat, R.id.longt, R.id.humid, R.id.level, R.id.temp};
    HashMap<Integer, String> keys = new HashMap<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        initMap();
        keys.put(textViewIDs[0], "date");
        keys.put(textViewIDs[1], "humid");
        keys.put(textViewIDs[2], "lat");
        keys.put(textViewIDs[3], "level");
        keys.put(textViewIDs[4], "longt");
        keys.put(textViewIDs[5], "temp");

        TabLayout tabs = (TabLayout) findViewById(R.id.tabs);
        getJSON("http://askmeair.com/aquahack/device-count");
        try {
            wait();
        } catch (Exception e) {
        }
        // HARDCODED
        int n = 3;
        try {
            n = Integer.parseInt(JSON.trim());
        } catch (Exception e) {

        }

        for (int i = 0; i < n; i++) {
            tabs.addTab(tabs.newTab());
            tabs.getTabAt(i).setText("DEVICE " + (i + 1));
        }
        getJSON("http://askmeair.com/aquahack/api?device=1");
        try {
            wait();
        } catch (Exception e) {
        }
        tabs.getTabAt(0).select();


        tabs.setOnTabSelectedListener(new TabLayout.OnTabSelectedListener() {
            @Override
            public void onTabSelected(TabLayout.Tab tab) {
               refreshTable();
            }

            @Override
            public void onTabUnselected(TabLayout.Tab tab) {

            }

            @Override
            public void onTabReselected(TabLayout.Tab tab) {
                refreshTable();
            }
        });

    }


    @Override
    protected void onPostCreate(@Nullable Bundle savedInstanceState) {
        super.onPostCreate(savedInstanceState);
        handler.post(runnable);
    }
    // Create the Handler
    private Handler handler = new Handler();

    // Define the code block to be executed
    private Runnable runnable = new Runnable() {
        @Override
        public void run() {
           refreshTable();

            // Repeat every 2 seconds
            handler.postDelayed(runnable, seconds2refresh * 1000);
        }
    };
    void callJasonEmi() {
        try {
            JSONObject jobj = new JSONObject(JSON);
            TextView tv = (TextView) findViewById(R.id.date);
            TextView tv2 = (TextView) findViewById(R.id.lat);
            TextView tv3 = (TextView) findViewById(R.id.longt);
            TextView tv4 = (TextView) findViewById(R.id.humid);
            TextView tv5 = (TextView) findViewById(R.id.level);
            TextView tv6 = (TextView) findViewById(R.id.temp);
            TextView tv7 = (TextView) findViewById(R.id.stat);
            tv.setText(jobj.get("date") + "");
            tv2.setText(jobj.get("lat") + "");
            tv3.setText(jobj.get("longt") + "");
            tv4.setText(jobj.get("humid") + "");
            tv5.setText(jobj.get("level") + "");
            tv6.setText(jobj.get("temp") + "");
            tv7.setText(jobj.get("status") + "");
        } catch (JSONException e) {
        }
    }
    void refreshTable(){
        TabLayout tabs = (TabLayout) findViewById(R.id.tabs);
        int ind = tabs.getSelectedTabPosition() + 1;
        getJSON("http://askmeair.com/aquahack/api?device=" + ind);
        try {
            wait(1000);
        } catch (Exception e) {
        }
        callJasonEmi();
    }
}
