#include <Arduino.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#define DHTTYPE    DHT11
#define DHTPIN 5
DHT dht(DHTPIN, DHTTYPE);        //DHT11
int t = 0;
int h = 0;

void setup() {
  SerialMon.begin(115200);
  dht.begin();
  delay(10);
}

void loop() {
  int newT = dht.readTemperature();
  t = newT;                                        
  int newH = dht.readHumidity();         //Temp+Humidity
  h = newH;
  Serial.println(t + " " + h);
  // put your main code here, to run repeatedly:

}
