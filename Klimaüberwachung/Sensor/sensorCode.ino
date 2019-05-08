#include <DHT.h>        
#include <ArduinoHttpClient.h>
#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include <DNSServer.h>           
#include <ESP8266WebServer.h>
#include <WiFiManager.h>
#include <EEPROM.h>


// Der Sensor Typ ist DHT22
#define DHTTYPE DHT22
// Die Daten Leitung wird auf Pin D3 vom Nodemcu angeschlossen.
// Ein Sensor Objekt wird erzeugt. Mit dem Pin D3. 
DHT dht(D3, DHTTYPE); 

// Adresse für die Token-Schnittstelle
const String tokenSchnittstelle = "http://192.168.2.113:8000/token";

// Adresse für die Daten-Schnittstelle
const String datenSchnittstelle = "http://192.168.2.113:8000/sensor";

// EEPROM Adresse an der ein Boolean gespeichert wird, welcher angibt ob der Sensor ein Token bereits hat oder nicht. 
const int isTokenSet = 500;

String macAddress;
String authToken;


void setup() {
  // DHT Sensor wird gestartet.
  dht.begin();
  // Serielle Verbindung wird gestartet.
  Serial.begin(9600);
  // EEPROM Kommunikation wird gestartet und 512 Bytes vom Flashspeicher werden dafür reserviert.
  EEPROM.begin(512);
  delay(700);
  //Startet hier den Wifimanager, der einen kleinen Hotspot eröffnet um sich mit einem Wifi zu verbinden. 
  //über den die Wifi Credentials eingetragen werden können.
  startWifimanager();
  // Als erstes wird der Authtoken aus dem EEPROM gelesen sofern er vorhanden ist.
  authToken = readToken();
  Serial.println(authToken);
  Serial.println(macAddress);
}

void loop() {
  // Falls im EEPROM noch kein Token vorhanden war.
  // erfragt der Sensor so lange seinen Authtoken vom Server bis er einen bekommt. 
  while(EEPROM.read(isTokenSet) == 0) {
    Serial.println("Requesting token ... token right now: "); 
    authToken = requestToken(tokenSchnittstelle);
    Serial.println(authToken);
    delay(10000);
  }
  
  // Kommt der Code an diese Stelle hat der Sensor einen Authtoken vom Server erhalten.
  // Daraufhin wird dieser ins EEPROM geschrieben.
  // Ist schon ein Token vorhanden wird dieser einfach erneut gespeichert bzw. überschrieben.
  saveToken(authToken);

  // Schleife die permanent Daten vom Sensor liest und an den Server schickt. 
  while(EEPROM.read(isTokenSet) == 1) {
    Serial.println("Reading sensor data ...");
    readSensorData();
    delay(100000);
  }  
}

// Speichert einen Authtoken ins EEPROM.
void saveToken(String token) {
  // Ein Token ist 21 Zeichenlang.
  char token_array[21];
  // Token wird in ein Character-Array umgewandelt.
  token.toCharArray(token_array, 21);
  // Setzt in jede EEPROM Speicherzelle von 0 bis 20 einen Character. 
  for(int i = 0; i < sizeof(token_array); i++) {
    EEPROM.write(i, token_array[i]);
    EEPROM.commit();
    Serial.println(token_array[i]);
  }
}

// Methode wird aktuell nicht benutzt. 
// Kann aber benutzt werden um die Speicherzelle, welche angibt ob ein Token bereits gespeicher ist, auf 0 zu setzen. 
void clearToken() {
  EEPROM.write(isTokenSet, 0);
  EEPROM.commit();
  Serial.println(EEPROM.read(isTokenSet));
  Serial.print(" Token cleared");
}

// Liest den Authtoken aus dem EEPROM aus. 
String readToken() {
  char token[21];
  for(int i = 0; i <= 20; i++){
    char ascii = EEPROM.read(i);
    token[i] = ascii;
  }
  return token;
}

// Methode um den Wifimanager zu starten. 
void startWifimanager() {
  // Setzt den Hostnamen des Sensors.
  WiFi.hostname("TinySensor"); 
  WiFiManager wifiManager;
  // Name des Accesspoints.
  wifiManager.autoConnect("Sensor Access Point");
  Serial.println("connected successfully");
  // An dieser Stelle wird die eigene Mac-Adresse ausgelesen und gesetzt.
  macAddress = WiFi.macAddress();
}

// Methode die den Token vom Server erfragt. 
String requestToken(String url) {
    // Es wird ein JSON Object erzeugt das die Mac-Adresse des Sensor beinhaltet.
    StaticJsonDocument<128> doc;
    JsonObject& root = doc.to<JsonObject>();
    root["macAddress"] = macAddress;
    String message;
    serializeJson(doc, message);

    // Dann wird ein HTTP Client gestarteg. 
    HTTPClient http;   

    // Über HTTP Post wird dann die Token-Schnittstelle angesprochen. 
    // Und es wird erfragt ob ein Sensor mit dieser Mac-Adresse bereits registriert ist.
    http.begin(url);      
    http.addHeader("Content-Type", "text/plain");  
    int httpCode = http.POST(message);  
    String payload = http.getString();                  
    http.end();  
    // Im payload befindet sich die Antwort des Servers. Das ist enweder der Token oder ein "False".
    if (payload != "False") {
      // Die "isTokenSet"-Speicherzelle wird auf 1 gesetzt.
      EEPROM.write(isTokenSet, 1);
      EEPROM.commit();
    }
    else {
      // Wenn ein "False" zurück kam, wird "isTokenSet"-Speicherzelle auf 0 gesetzt.
      EEPROM.write(isTokenSet, 0);
      EEPROM.commit();
    }
    return payload;
}

void sendSensorData(float t, float h, String url) {
  // Es wird ein JSON Object erzeugt das die Mac-Adresse, Sensordaten und den Authtoken beinhaltet.
  // Diese müssen doe korrekte Form des Serializers an der Daten-Schnittstelle beim Server haben. 
  StaticJsonDocument<128> doc;
  JsonObject& root = doc.to<JsonObject>();
  root["macAddress"] = macAddress;
  root["humidity"] = h;
  root["temperature"] = t;
  String token = readToken();
  root["token"] = token;
  String message;
  serializeJson(doc, message);

  // HTTP Client wird gestartet.
  HTTPClient http;    

  // Es wird das JSON Objekt an die Daten-Schnittstelle gesendet. 
  http.begin(url);      
  http.addHeader("Content-Type", "text/plain");
  Serial.println("Sending data with token " + token); 
  // Per HTTP-Post wird das JSON-Objekt versendet. 
  int httpCode = http.POST(message);  
  String payload = http.getString();   
  // Response wird ausgelesen.
  Serial.println(payload);
  if (payload == "Mac and Token do not match") {
    EEPROM.write(isTokenSet, 0);
    EEPROM.commit();
    Serial.println(EEPROM.read(500));
  }
  http.end();  
}

void readSensorData() {
  // Arrays für jeweils 10 Messwerte
  float tempArray[10];
  float humidArray[10];

  // Es werden 10 Messdurchläufe gemacht und aus diesen 10 Messwerten wird dann ein Mittelwert berechnet. 
  for(int i = 0; i<=9;i++) {
    // Sensor liest die Temp und Luftfeuchtigkeit.
    float h = dht.readHumidity();
    Serial.println(h);
    Serial.print("  ");
    float t = dht.readTemperature();
    Serial.println(t); 

    // Falls der Sensor für einen der beiden Messwerte keinen Wert hat soll solange weiter gemssen werden bis eine Zahl gemessen wird.
    // (nan = Not A Number)
    while (isnan(t) && isnan(h)) {
      Serial.println("Data is NaN... reading again");
      h = dht.readHumidity();
      t = dht.readTemperature(); 
      delay(2000);
    }

    // Manchmal misst der Sensor ein "Not a Number", dies muss abgefangen werden.
    // Theoretisch sollte ein NaN nicht bis an diese Stelle kommen. 
    if(!isnan(t) && !isnan(h)){
      // Messwerte werden in die Arrays gespeichert.
      tempArray[i] = t;
      humidArray[i] = h;
      delay(60000);
    }
  }
  //Es werden Mittelwerte berechnet und bis auf eine Nachkommastelle gerundet.
  float avgTemp = calcAverage(tempArray, 10);
  float avgHumid = calcAverage(humidArray, 10);
  // Erst die Mittelwerte werden an den Server gesendet.
  Serial.println("Sending Data...");
  sendSensorData(avgTemp, avgHumid , datenSchnittstelle);
}

// Bekommt ein Array und die zugehörige Länge übergeben um den Mittelwert zu berechnen. 
float calcAverage(float a[], float sizeOfArray) {
  float sum = 0;
  for(int i = 0; i <= sizeOfArray - 1;i++) {
    sum = sum + a[i]; 
    Serial.println("Printing sum");
    Serial.println(sum);
  }
  // Runded die Summe bevor der Mittelwert berechnet wird um nur eine Nachkommastelle zu haben. 
  return round(sum)/sizeOfArray;
}
