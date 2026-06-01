# ESP32 to MongoDB Setup

This app now expects this flow:

ESP32 sensor -> FastAPI backend -> MongoDB -> Flutter app

## 1. Start MongoDB

Use either local MongoDB or MongoDB Atlas.

For local MongoDB, the backend default is:

```env
MONGODB_URI=mongodb://localhost:27017/
```

For MongoDB Atlas, set `MONGODB_URI` in `backend/.env` to your Atlas connection string.

## 2. Start the backend

From `enersense/backend`:

```powershell
pip install -r requirements.txt
copy .env.example .env
python main.py
```

If `python` is not installed or not in PATH, install Python 3.10+ first.

Check the backend:

```powershell
curl http://localhost:8000/health
```

## 3. Find your computer IP

On Windows:

```powershell
ipconfig
```

Use the IPv4 address on the same WiFi network as the ESP32, for example `192.168.1.23`.

## 4. Flash the ESP32

Open `ESP32_ENERSENSE_SENSOR.ino` in Arduino IDE.

Update:

```cpp
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SENSOR_ENDPOINT = "http://YOUR_PC_IP:8000/api/v1/sensor-data";
```

Example:

```cpp
const char* SENSOR_ENDPOINT = "http://192.168.1.23:8000/api/v1/sensor-data";
```

Install/select:

- Board: ESP32 Dev Module
- Libraries: WiFi and HTTPClient are included with ESP32 Arduino core

## 5. Test without ESP32 first

```powershell
curl -X POST http://localhost:8000/api/v1/sensor-data -H "Content-Type: application/json" -d "{\"device_id\":\"esp32_01\",\"voltage\":240,\"current\":0.8,\"power\":192}"
curl http://localhost:8000/api/v1/live-usage?device_id=esp32_01
```

You should see the reading stored in MongoDB collection `enersense.energy_logs`.

## Payload Format

The ESP32 should send JSON like this:

```json
{
  "device_id": "esp32_01",
  "voltage": 240.0,
  "current": 0.8,
  "power": 192.0
}
```

`voltage` is optional and defaults to `240.0`.

## Safety Note

If you are measuring AC mains, use an isolated, rated sensor module and enclosure. Do not connect mains directly to an ESP32.
