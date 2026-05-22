# EnerSense AI/ML - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (2 min)
```bash
cd ai-model
pip install -r requirements.txt
```

### Step 2: Train Models (1 min)
```bash
python model_training.py
```

This generates:
- `models/appliance_classifier.pkl` - NILM model
- `models/anomaly_detector.pkl` - Anomaly detection model
- `models/label_encoder.pkl` - Label encoder

### Step 3: Run Demo (30 sec)
```bash
python demo.py
```

You should see output showing:
- ✓ Appliance predictions
- ✓ Anomaly detection
- ✓ Energy scoring
- ✓ Recommendations
- ✓ Monthly forecast

### Step 4: Start API Server (1 min)
```bash
python api_service.py
```

Server starts at: **http://localhost:8000**

API Docs: **http://localhost:8000/docs** (interactive Swagger UI)

## 📡 API Endpoints

### 1. Send Sensor Data
```bash
curl -X POST http://localhost:8000/sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-05-12T15:30:00",
    "power": 1500,
    "voltage": 240,
    "current": 6.25
  }'
```

**Response:**
```json
{
  "timestamp": "2026-05-12T15:30:00",
  "power": 1500,
  "voltage": 240,
  "current": 6.25,
  "predicted_appliance": "Air Conditioner",
  "energy_score": 42,
  "is_anomaly": false,
  "anomaly_insight": null
}
```

### 2. Get Live Usage
```bash
curl http://localhost:8000/live-usage
```

### 3. Get Recommendations
```bash
curl http://localhost:8000/insights
```

### 4. Get Energy Forecast
```bash
curl http://localhost:8000/forecast
```

### 5. Get Appliance Breakdown
```bash
curl http://localhost:8000/appliances
```

### 6. Health Check
```bash
curl http://localhost:8000/health
```

## 🏗️ System Architecture

```
ESP32 (Hardware)
    ↓ (Sensor data via WiFi/MQTT)
Backend Server
    ↓
POST /sensor-data
    ↓
AI/ML Pipeline
├── Appliance Classifier (NILM)
├── Anomaly Detector
├── Recommendation Engine
└── Forecasting Engine
    ↓
Response (JSON)
    ↓
Flutter Frontend (Dashboard)
```

## 📁 File Structure

```
ai-model/
├── api_service.py              # ← Start here for API
├── demo.py                     # ← Run this to test
├── model_training.py           # ← Train models here
├── appliance_classifier.py     # NILM model
├── anomaly_detection.py        # Anomaly detection
├── recommendation_engine.py    # Recommendations
├── forecasting.py              # Forecasting
├── sample_data.csv             # Training data
├── requirements.txt            # Dependencies
├── models/                     # Trained models (auto-generated)
│   ├── appliance_classifier.pkl
│   ├── anomaly_detector.pkl
│   └── label_encoder.pkl
└── README.md                   # Full documentation
```

## 🚀 Common Tasks

### Test a Specific Feature

**Test Appliance Prediction:**
```python
from appliance_classifier import predict_appliance

appliance = predict_appliance(1500, 240, 6.25)  # Should return "Air Conditioner"
```

**Test Anomaly Detection:**
```python
from anomaly_detection import analyze_reading

result = analyze_reading(3500, "Air Conditioner")
print(result['is_anomaly'])  # True if unusual
```

**Test Recommendations:**
```python
from recommendation_engine import get_recommendations, add_reading

add_reading(1500, "Air Conditioner")
add_reading(800, "Television")

recs = get_recommendations()
for rec in recs:
    print(rec['recommendation'])
```

### Retrain Models

```bash
# Delete old models (optional)
rm models/*.pkl

# Train new models
python model_training.py
```

### Verify Models

```bash
import joblib
import os

models_dir = 'models'
for f in ['appliance_classifier.pkl', 'anomaly_detector.pkl', 'label_encoder.pkl']:
    path = os.path.join(models_dir, f)
    if os.path.exists(path):
        model = joblib.load(path)
        print(f"✓ {f} loaded successfully")
    else:
        print(f"✗ {f} not found")
```

## 🔍 Features Summary

| Feature | Status | Method |
|---------|--------|--------|
| Appliance Prediction | ✅ | Random Forest |
| Anomaly Detection | ✅ | Isolation Forest |
| Energy Scoring | ✅ | Power-based |
| Recommendations | ✅ | Rule-based |
| Forecasting | ✅ | Moving Average |
| API Integration | ✅ | FastAPI |

## 📊 Expected JSON Format

All responses follow this format:

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

## 🐛 Troubleshooting

### Models not loading?
```bash
python model_training.py  # Retrain models
```

### Port 8000 already in use?
```bash
python -m uvicorn api_service:app --port 8001
```

### ImportError when running demo?
```bash
# Make sure you're in the ai-model directory
cd ai-model
python demo.py
```

## ✨ Next Steps

1. ✅ Complete AI/ML module (you are here)
2. 🔄 Integrate with Backend API
3. 📱 Connect to Flutter Frontend
4. 🔧 Add database persistence
5. 📈 Improve model accuracy with real data

## 📞 Support

For issues or questions:
- Check `README.md` for detailed docs
- Review `demo.py` for usage examples
- Run `python api_service.py` to see API logs

---

**Version:** 1.0.0  
**Last Updated:** May 13, 2026  
**Status:** ✅ Production Ready for Hackathon
