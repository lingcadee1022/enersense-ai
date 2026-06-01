#include <WiFi.h>
#include <HTTPClient.h>

// Update these values before flashing.
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// Use your computer's LAN IP address, not localhost.
// Example: http://192.168.1.23:8000/api/v1/sensor-data
const char* SENSOR_ENDPOINT = "http://YOUR_PC_IP:8000/api/v1/sensor-data";

const char* DEVICE_ID = "esp32_01";

// Example analog current sensor wiring.
// Adjust calibration for your actual sensor module.
const int CURRENT_SENSOR_PIN = 34;
const float ADC_MAX = 4095.0;
const float ADC_REF_VOLTAGE = 3.3;
const float SENSOR_ZERO_VOLTAGE = 1.65;
const float ACS712_SENSITIVITY = 0.100; // V/A. 20A module is often 0.100.
const float MAINS_VOLTAGE = 240.0;

const unsigned long SEND_INTERVAL_MS = 5000;
unsigned long lastSendMs = 0;

float readCurrentAmps() {
  const int samples = 80;
  float total = 0.0;

  for (int i = 0; i < samples; i++) {
    int raw = analogRead(CURRENT_SENSOR_PIN);
    float voltage = (raw / ADC_MAX) * ADC_REF_VOLTAGE;
    float current = abs((voltage - SENSOR_ZERO_VOLTAGE) / ACS712_SENSITIVITY);
    total += current;
    delay(2);
  }

  return total / samples;
}

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Connected. ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

void sendReading() {
  float current = readCurrentAmps();
  float power = MAINS_VOLTAGE * current;

  HTTPClient http;
  http.begin(SENSOR_ENDPOINT);
  http.addHeader("Content-Type", "application/json");

  String payload = "{";
  payload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
  payload += "\"voltage\":" + String(MAINS_VOLTAGE, 2) + ",";
  payload += "\"current\":" + String(current, 3) + ",";
  payload += "\"power\":" + String(power, 2);
  payload += "}";

  int statusCode = http.POST(payload);
  String response = http.getString();

  Serial.print("POST ");
  Serial.print(statusCode);
  Serial.print(" ");
  Serial.println(payload);
  Serial.println(response);

  http.end();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  connectWiFi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (millis() - lastSendMs >= SEND_INTERVAL_MS) {
    lastSendMs = millis();
    sendReading();
  }
}
