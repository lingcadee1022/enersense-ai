# EnerSense AI/ML Module

Complete AI/ML pipeline for energy analysis, appliance prediction (NILM), anomaly detection, and recommendations.

## Project Structure

```
ai-model/
├── model_training.py          # Train and save ML models
├── appliance_classifier.py     # NILM - Appliance prediction
├── anomaly_detection.py        # Detect unusual energy patterns
├── recommendation_engine.py    # Generate energy-saving recommendations
├── forecasting.py              # Energy consumption forecasting
├── api_service.py              # FastAPI endpoints
├── sample_data.csv             # Training data
├── requirements.txt            # Python dependencies
├── models/                     # Trained model files (generated)
└── README.md                   # This file
```

## Installation

### 1. Install Dependencies

```bash
cd ai-model
pip install -r requirements.txt
```

### 2. Train Models

```bash
python model_training.py
```

This will generate trained models in the `models/` directory:
- `appliance_classifier.pkl` - Random Forest classifier for appliance prediction
- `anomaly_detector.pkl` - Isolation Forest for anomaly detection
- `label_encoder.pkl` - Label encoder for appliance names

## Usage

### Running the API

```bash
python api_service.py
```

The API will start at `http://localhost:8000`

Access the interactive documentation at: `http://localhost:8000/docs`

### API Endpoints

#### 1. POST `/sensor-data`
Process sensor reading from ESP32

**Request:**
```json
{
  "timestamp": "2026-05-12T15:30:00",
  "power": 1200,
  "voltage": 240,
  "current": 5.0
}
```

**Response:**
```json
{
  "timestamp": "2026-05-12T15:30:00",
  "power": 1200,
  "voltage": 240,
  "current": 5.0,
  "predicted_appliance": "Air Conditioner",
  "energy_score": 34,
  "is_anomaly": false,
  "anomaly_insight": null
}
```

#### 2. GET `/live-usage`
Get latest live usage data

**Response:**
```json
{
  "timestamp": "2026-05-12T15:30:00",
  "power": 1200,
  "voltage": 240,
  "current": 5.0,
  "predicted_appliance": "Air Conditioner",
  "energy_score": 34,
  "is_anomaly": false
}
```

#### 3. GET `/insights`
Get AI-generated recommendations

**Response:**
```json
{
  "insights": [
    "AC usage is high. Consider using eco mode or adjusting temperature.",
    "Turn off TV when not actively watching."
  ],
  "recommendations": [
    {
      "type": "high_usage",
      "appliance": "Air Conditioner",
      "recommendation": "AC usage is high...",
      "potential_savings": "RM 45.60/month"
    }
  ],
  "appliance_breakdown": [
    {
      "appliance": "Air Conditioner",
      "avg_power": 1500,
      "readings": 5,
      "total_consumption": 7500
    }
  ]
}
```

#### 4. GET `/forecast`
Get energy consumption forecast

**Response:**
```json
{
  "estimated_daily_kwh": 28.8,
  "estimated_monthly_kwh": 864.0,
  "estimated_monthly_cost": 388.8,
  "peak_hours": [18, 19, 20, 21],
  "currency": "RM"
}
```

#### 5. GET `/appliances`
Get appliance usage breakdown

**Response:**
```json
{
  "appliances": [
    {
      "appliance": "Air Conditioner",
      "avg_power": 1500,
      "readings": 10,
      "total_consumption": 15000
    }
  ],
  "total_readings": 50,
  "timestamp": "2026-05-13T04:40:00"
}
```

#### 6. GET `/health`
Health check

**Response:**
```json
{
  "status": "healthy",
  "service": "EnerSense AI API",
  "timestamp": "2026-05-13T04:40:00",
  "readings_processed": 25
}
```

## Core Features

### 1. Appliance Prediction (NILM)
- Uses power, voltage, and current to identify appliances
- Implements Random Forest classification
- Fallback to rule-based detection if models unavailable
- Supports: AC, Oven, Washing Machine, Television, Lighting, Refrigerator

### 2. Anomaly Detection
- Detects unusual energy usage patterns
- Uses Isolation Forest ML model
- Fallback to statistical Z-score detection
- Maintains 24-hour sliding window of historical data

### 3. Recommendation Engine
- Rule-based recommendations for energy savings
- Identifies high AC usage during peak hours
- Suggests appliance efficiency improvements
- Calculates potential monthly savings in RM
- Generates daily summaries

### 4. Energy Forecasting
- Forecasts hourly, daily, and monthly consumption
- Uses moving average and historical patterns
- Identifies peak and low-usage hours
- Estimates monthly costs at RM 0.45/kWh

### 5. Energy Score
- Calculates appliance energy intensity (0-100)
- Higher score = more power consumption
- Helps users identify high-consumption appliances

## Data Flow

```
ESP32 → HTTP POST to /sensor-data
         ↓
    API validates & parses
         ↓
    Appliance Classifier → identifies appliance
         ↓
    Anomaly Detector → checks for unusual patterns
         ↓
    Recommendation Engine → updates recommendations
         ↓
    Forecasting Engine → updates forecasts
         ↓
    Returns JSON response → Flutter Frontend
```

## Customization

### Adjust Energy Cost
Edit `COST_PER_KWH` in:
- `recommendation_engine.py`
- `forecasting.py`

### Modify Appliance Ranges
Edit `appliance_ranges` dict in `appliance_classifier.py`

### Change Anomaly Threshold
Edit `threshold_factor` in `anomaly_detection.py`

## Testing

### Test with Sample Data

```python
from appliance_classifier import predict_appliance, get_energy_score
from anomaly_detection import analyze_reading
from recommendation_engine import get_recommendations
from forecasting import forecast_monthly

# Test appliance prediction
appliance = predict_appliance(1500, 240, 6.25)
print(f"Predicted: {appliance}")  # Should print "Air Conditioner"

# Test energy score
score = get_energy_score(1500)
print(f"Energy Score: {score}")  # Should print 42

# Test anomaly detection
result = analyze_reading(1500, "Air Conditioner")
print(f"Anomaly: {result['is_anomaly']}")

# Test recommendations
recs = get_recommendations()
print(f"Recommendations: {len(recs)} found")

# Test forecasting
forecast = forecast_monthly()
print(f"Estimated monthly cost: RM {forecast['estimated_monthly_cost']:.2f}")
```

### Test API with cURL

```bash
# Test sensor data endpoint
curl -X POST http://localhost:8000/sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-05-12T15:30:00",
    "power": 1500,
    "voltage": 240,
    "current": 6.25
  }'

# Get insights
curl http://localhost:8000/insights

# Get forecast
curl http://localhost:8000/forecast

# Health check
curl http://localhost:8000/health
```

## Integration with Flutter Frontend

### Example: Process Sensor Data

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<void> processSensorData(
  double power,
  double voltage,
  double current,
) async {
  final response = await http.post(
    Uri.parse('http://your-backend/api/sensor-data'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'timestamp': DateTime.now().toIso8601String(),
      'power': power,
      'voltage': voltage,
      'current': current,
    }),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    print('Appliance: ${data['predicted_appliance']}');
    print('Energy Score: ${data['energy_score']}');
  }
}
```

## Performance Notes

- Models are lightweight and suitable for edge deployment
- Inference is fast enough for real-time processing
- Fallback logic ensures operation even without trained models
- In-memory storage - data resets on service restart

## Future Enhancements

1. Persistent database for historical data
2. LSTM models for better forecasting
3. Personalized user behavior learning
4. Mobile push notifications for anomalies
5. Integration with smart home systems
6. Cost optimization algorithms
7. CO2 footprint tracking

## Team Assignment

- **Developed by**: AI/ML Engineer (Teammate 1)
- **Integration**: Backend Engineer (Teammate 2)
- **Frontend**: Flutter Engineer (Teammate 3)

## License

Part of EnerSense AI Project - Smart Energy Management System
