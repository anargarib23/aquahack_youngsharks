#include <Arduino.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#define DHTTYPE    DHT11
#define DHTPIN 5
DHT dht(DHTPIN, DHTTYPE);        //DHT11
int t = 0;
int h = 0;

const int n=1; //N# of destionation

long randNumber;      //Cayseviyyesi (random)

#include <SPI.h>
#include <Wire.h>

const char apn[]      = ""; // Your APN
const char gprsUser[] = ""; // User
const char gprsPass[] = ""; // Password
const char simPIN[]   = ""; // SIM card PIN code

#define MODEM_RST            5
#define MODEM_PWKEY          4
#define MODEM_POWER_ON       23
#define MODEM_TX             27
#define MODEM_RX             26
#define I2C_SDA              21
#define I2C_SCL              22

// Set serial for debug console (to the Serial Monitor, default speed 115200)
#define SerialMon Serial
// Set serial for AT commands (to the module)
#define SerialAT  Serial1

// Configure TinyGSM library
#define TINY_GSM_MODEM_SIM800      // Modem is SIM800
#define TINY_GSM_RX_BUFFER   1024  // Set RX buffer to 1Kb
#include <Wire.h>
#include <TinyGsmClient.h>

#ifdef DUMP_AT_COMMANDS
  #include <StreamDebugger.h>
  StreamDebugger debugger(SerialAT, SerialMon);
  TinyGsm modem(debugger);
#else
  TinyGsm modem(SerialAT);
#endif

const char server[] = "askmeair.com";
///aquahack/getdata/CCj5TpgOUr/dn=1ANDah=68.00ANDwl=3169ANDt=27.00ANDsend=31-02-2020-02-42-34

TinyGsmClient client(modem);
const int  port = 80;


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void setup() {
  // Set console baud rate
  SerialMon.begin(115200);
  dht.begin();
  randomSeed(analogRead(0));
  delay(10);
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void loop() {

  String resourcee="/aquahack/getdata/CCj5TpgOUr/";
  int newT = dht.readTemperature();
  t = newT;                                        
  int newH = dht.readHumidity();         //Temp+Humidity
  h = newH;                                                              //READ DATAS
  randNumber = random(60, 99);   //RiverDepth
  resourcee=(resourcee + "dn=" + n);
  resourcee=(resourcee + "ANDah=" + h);
  resourcee=(resourcee + "ANDwl=" + randNumber);
  resourcee=(resourcee + "ANDt=" + t);
//  resourcee=(resourcee + "ANDsend=" + "29-06-2020-00-00-00");
  Serial.println(resourcee);
  int str_len = resourcee.length() + 1; 
  char resource[str_len];
  resourcee.toCharArray(resource, str_len);
  delay(2000);
  
  // Keep power when running from battery
  Wire.begin(I2C_SDA, I2C_SCL);

  pinMode(MODEM_PWKEY, OUTPUT);
  pinMode(MODEM_RST, OUTPUT);
  pinMode(MODEM_POWER_ON, OUTPUT);

  digitalWrite(MODEM_PWKEY, LOW);
  digitalWrite(MODEM_RST, HIGH);
  digitalWrite(MODEM_POWER_ON, HIGH);

  SerialAT.begin(115200, SERIAL_8N1, MODEM_RX, MODEM_TX);
  delay(3000);

  // Restart takes quite some time
  // To skip it, call init() instead of restart()
  SerialMon.println("Initializing modem...");
  modem.restart();
  // Or, use modem.init() if you don't need the complete restart

  String modemInfo = modem.getModemInfo();
  SerialMon.print("Modem: ");
  SerialMon.println(modemInfo);

  // Unlock your SIM card with a PIN if needed
  if (strlen(simPIN) && modem.getSimStatus() != 3 ) {
    modem.simUnlock(simPIN);
  }

//  String resourcee = "/aquahack/getdata/CCj5TpgOUr/"; //ah air hum, andwl water level, 
    
  SerialMon.print("Waiting for network...");
  if (!modem.waitForNetwork(240000L)) {
    SerialMon.println(" fail");
    delay(10000);
    return;
  }
  SerialMon.println(" OK");

  if (modem.isNetworkConnected()) {
    SerialMon.println("Network connected");
  }

  SerialMon.print(F("Connecting to APN: "));
  SerialMon.print(apn);
  if (!modem.gprsConnect(apn, gprsUser, gprsPass)) {
    SerialMon.println(" fail");
    delay(10000);
    return;
  }
  SerialMon.println(" OK");

  SerialMon.print("Connecting to ");
  SerialMon.print(server);
  if (!client.connect(server, port)) {
    SerialMon.println(" fail");
    delay(10000);
    return;
  }
  SerialMon.println(" OK");
     
  // Make a HTTP GET request:  
  SerialMon.println("Performing HTTP GET request...");                     // here goes the data
  client.print(String("GET ") + resource + " HTTP/1.1\r\n");

  client.print(String("Host: ") + server + "\r\n");
  client.print("Connection: close\r\n\r\n");
  client.println();

  unsigned long timeout = millis();
  while (client.connected() && millis() - timeout < 10000L) {
    // Print available data
    while (client.available()) {
      char c = client.read();
      SerialMon.print(c);
      timeout = millis();
    }
  }
  SerialMon.println();

  // Shutdown

  client.stop();
  SerialMon.println(F("Server disconnected"));

  modem.gprsDisconnect();
  SerialMon.println(F("GPRS disconnected"));
  

  //wait for some time and then send again!

//delay(2000);
//    for(int i=0;i<120;i++){
//      delay(1000);              //wait 2 min
//    }

    for(int i=0;i<180;i++){
      delay(10000);             //wait 30 min
      }
    


  
}
