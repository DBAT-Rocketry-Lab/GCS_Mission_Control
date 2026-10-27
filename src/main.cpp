#include <WiFi.h>
#include <HX711_ADC.h>
#include <ArduinoOTA.h>

// ================= PIN DEFINITIONS =================
#define BTS_R_PWM     27
#define HX711_DOUT    33
#define HX711_SCK     32
#define AUX_PIN       26
#define LED           

// ================= WIFI CONFIG =================
const char* ssid     = "dogra";
const char* password = "nomnom123";

WiFiServer server(8080);
WiFiClient client;

// ================= GLOBALS =================
bool armed = false;
unsigned long t = 0;

HX711_ADC LoadCell(HX711_DOUT, HX711_SCK);

// ================= SETUP =================
void setup() {
  pinMode(AUX_PIN, OUTPUT);
  pinMode(BTS_R_PWM, OUTPUT);

  digitalWrite(BTS_R_PWM, LOW);
  digitalWrite(AUX_PIN, LOW);

  Serial.begin(115200);

  // ---------- WIFI ----------
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  server.begin();

  // ---------- OTA SETUP ----------
  ArduinoOTA.setHostname("ESP32-LAUNCH");

  ArduinoOTA.onStart([]() {
    Serial.println("OTA Start");
  });

  ArduinoOTA.onEnd([]() {
    Serial.println("\nOTA End");
  });

  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress * 100) / total);
  });

  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });

  ArduinoOTA.begin();
  Serial.println("OTA Ready");

  // ---------- LOAD CELL ----------
  LoadCell.begin();
  LoadCell.setCalFactor(66.42);

  unsigned long stabilizingtime = 2000;
  LoadCell.start(stabilizingtime, true);

  if (LoadCell.getTareTimeoutFlag()) {
    Serial.println("HX711 timeout — check wiring");
    while (1);
  }

  Serial.println("System DISARMED");
  Serial.println("Load cell ready");
}

// ================= LOOP =================
void loop() {
  ArduinoOTA.handle();

  // ---------- ACCEPT CLIENT ----------
  if (!client || !client.connected()) {
    client = server.available();
    if (client) {
      Serial.println("Client connected");
    }
  }

  // ---------- LOAD CELL UPDATE ----------
  static unsigned long lastSend = 0;
  const unsigned long sendInterval = 50;

  if (LoadCell.update() && millis() - lastSend >= sendInterval) {
    float value = LoadCell.getData();

    Serial.print("Loadcell: ");
    Serial.println(value, 1);

    if (client && client.connected()) {
      client.println(value, 1);
    }

    lastSend = millis();
  }

  if (LoadCell.getTareStatus()) {
    Serial.println("Tare complete");
  }

  // ---------- WIFI COMMAND HANDLING ----------
  if (client && client.connected() && client.available()) {
    String cmd = client.readStringUntil('\n');
    cmd.trim();

    Serial.print("CMD: ");
    Serial.println(cmd);

    if (cmd == "arm") {
      armed = true;
      client.println("ARMED");
    }

    else if (cmd == "disarm") {
      armed = false;
      digitalWrite(BTS_R_PWM, LOW);
      digitalWrite(AUX_PIN, LOW);
      client.println("DISARMED");
    }

    else if (cmd == "1" && armed) {
      client.println("FIRING");

      digitalWrite(BTS_R_PWM, HIGH);
      digitalWrite(AUX_PIN, HIGH);
      delay(5000);
      digitalWrite(BTS_R_PWM, LOW);
      digitalWrite(AUX_PIN, LOW);

      armed = false;
      client.println("DONE - DISARMED");
    }

    else if (cmd == "1" && !armed) {
      client.println("IGNORED - NOT ARMED");
    }

    else if (cmd == "t") {
      LoadCell.tareNoDelay();
      client.println("TARE STARTED");
    }

    else {
      client.println("UNKNOWN COMMAND");
    }
  }
}
