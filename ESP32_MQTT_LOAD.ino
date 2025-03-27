#include <ESP32Servo.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <HX711.h>
#include <Arduino.h>
#include "soc/rtc.h"


Servo servo1;
int pos = 0;

// #define TEST
// #define CALIBRATE
#define SOUND_SPEED 0.034

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 19;
const int LOADCELL_SCK_PIN = 2;
const long LOADCELL_DIVIDER = 3000;

// Ultrasonic sensor 
const int TRIG_PIN = 4;
const int ECHO_PIN = 18;
long duration = 0;
float distanceCm = 0;

// Lock
const int UNLCK_PIN = 5;

// Servo
const int SERVO_PIN = 23;

// WiFi
const char* ssid = "Swag Lord";
const char* password = "123456789";

// MQTT
const char* mqtt_server = "172.20.10.10";
void connectmqtt();

// Initialise the WiFi and MQTT Client objects
WiFiClient wifiClient;
// 1883 is the listener port for the Broker
PubSubClient client(wifiClient);

int LED = 02;


HX711 scale;

void sendWeight() {
  char tempString[8];
  dtostrf(scale.get_units(5), 1, 2, tempString);
  client.publish("plastic", tempString); 
  delay(2000);
}

void unlock() {
  digitalWrite(UNLCK_PIN, HIGH);
  Serial.println("Unlocked from function");
  delay(2000);
  digitalWrite(UNLCK_PIN, LOW);
  client.publish("unlck", "unlocked from unlock"); 
}

void openPlatform() {
  client.publish("logger", "beginning sweep");
	// for (pos = 0; pos <= 180; pos += 1) { // goes from 0 degrees to 180 degrees
	// 	// in steps of 1 degree
	// 	servo1.write(pos);    // tell servo to go to position in variable 'pos'
	// 	delay(10);             // waits 15ms for the servo to reach the position
	// }
  // for (pos = 180; pos >= 0; pos -= 1) { // goes from 0 degrees to 180 degrees
	// 	// in steps of 1 degree
	// 	servo1.write(pos);    // tell servo to go to position in variable 'pos'
	// 	delay(15);             // waits 15ms for the servo to reach the position
	// }
  servo1.write(180);
  delay(400);
  servo1.write(90);
  delay(2000);
  servo1.write(0);
  delay(420);
  servo1.write(90);

}

void sendUsnd() {
  char tempString[6];
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(ECHO_PIN, HIGH);
  
  // Calculate the distance
  distanceCm = duration * SOUND_SPEED/2;
  
  dtostrf(distanceCm, 1, 2, tempString);
  client.publish("usnd", tempString);
  delay(2000);
}

void flashLed() {
  for (int i = 0;i<3;i++) {
    digitalWrite(LED, HIGH);
    delay(100);
    digitalWrite(LED, LOW);
    delay(100);
  }

}

void setup() {

  Serial.begin(115200);
  setCpuFrequencyMhz(80);
  pinMode(LED, OUTPUT);
  pinMode(UNLCK_PIN, OUTPUT);
  digitalWrite(LED, LOW);
  WiFi.begin(ssid, password);
  Serial.println("connected wifi");
  client.setServer(mqtt_server, 1883);//connecting to mqtt server
  client.setCallback(callback);
  delay(5000);
  connectmqtt();

  // configure the trigger pin to output mode
  pinMode(TRIG_PIN, OUTPUT);
  // configure the echo pin to input mode
  pinMode(ECHO_PIN, INPUT);

  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);

  scale.set_scale(LOADCELL_DIVIDER);
  scale.tare();


  delay(1000);


  ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	servo1.setPeriodHertz(50);    // standard 50 hz servo
	servo1.attach(SERVO_PIN, 900, 2100);
  servo1.write(90);
  digitalWrite(LED, LOW);
  Serial.println("setup finished");
}

void callback(char* topic, byte* payload, unsigned int length) {   //callback includes topic and payload ( from which (topic) the payload is comming)
  flashLed();
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  Serial.println();
  String messageTemp;
  
  for (int i = 0; i < length; i++)
  {
    Serial.print((char)payload[i]);
    messageTemp += (char)payload[i];
  }

   Serial.println();
  
  if ((char)topic[0] == 'u' && (char)topic[1] == 'n' && (char)topic[2] == 'l' && (char)topic[3] == 'c' &&(char)topic[4] == 'k'){
    if (messageTemp == "1") {
      Serial.println("Unlocked");
      unlock();
    }
    }

  if ((char)topic[0] == 'g' && (char)topic[1] == 't' && (char)topic[2] == 'p' && (char)topic[3] == 'c'){
  if (messageTemp == "plastic") {
    sendWeight();
    Serial.println("sent plastic");
  }
  }

  if ((char)topic[0] == 'g' && (char)topic[1] == 't' && (char)topic[2] == 'p' && (char)topic[3] == 'c'){
    if (messageTemp == "open") {
      openPlatform();
      Serial.println("Opened Platform");
      
    }
  }
  
  Serial.println();
  
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Attempting MQTT connection...");
    if (client.connect("ESP32_1")) {
      Serial.println("connected mqtt");
      client.subscribe("gtpc");
      client.subscribe("unlck");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void loop() {

  if (!client.connected())
  {
    reconnect();
  }

  client.loop();
  
  // Serial.print("HX711 reading: ");
  // Serial.println(scale.get_units(5), 1);
  // Prints the distance in the Serial Monitor
  // Serial.print("Distance: ");
  // Serial.println(distanceCm);
}

void connectmqtt(){
  client.connect("ESP32_1");  // ESP will connect to mqtt broker with clientID
  Serial.println("connected to MQTT");
  // Once connected, publish an announcement...

  // ... and resubscribe 
  client.subscribe("gtpc");
  client.subscribe("unlck");
  client.publish("plastic",  "connected to MQTT, plastic");
  client.publish("logger",  "connected to MQTT, logger");
  
  if (!client.connected())
  {
    Serial.println("Reconnecting MQTT...");
    reconnect();
  }
}
