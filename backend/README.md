# EnerSense AI Backend

A production-ready FastAPI backend for IoT energy monitoring with AI-powered insights, anomaly detection, and behavior learning.

## Features

- ✨ **Real-time Sensor Data Ingestion** - Receive ESP32 sensor data with automatic timestamping
- 📊 **Historical Data Analysis** - Retrieve and analyze energy consumption patterns
- 🤖 **Machine Learning** - Isolation Forest anomaly detection and KMeans clustering
- 💡 **AI Insights** - Generate human-readable energy-saving recommendations
- 📈 **Behavior Learning** - Learn user consumption patterns and generate profiles
- 💰 **Cost Estimation** - Calculate energy costs based on consumption
- 🔐 **Production-Ready** - Type hints, error handling, logging, CORS support
- 📱 **Flutter Compatible** - CORS enabled for mobile app integration

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB with pymongo
- **ML**: scikit-learn (Isolation Forest, KMeans)
- **Data Processing**: pandas, numpy
- **Server**: Uvicorn
- **Python**: 3.8+

## Project Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── models.py           # Pydantic request/response models
│   ├── sensor.py           # POST /sensor-data
│   ├── live_usage.py       # GET /live-usage
│   ├── history.py          # GET /history
│   └── insights.py         # GET /insights, /insights/profile, /insights/train-profile
├── db/
│   ├── __init__.py
│   └── mongo.py            # MongoDB client and operations
├── services/
│   ├── __init__.py
│   ├── cost_service.py     # Electricity cost calculation
│   ├── behavior_service.py # User behavior analysis
│   ├── anomaly_service.py  # Anomaly detection with Isolation Forest
│   └── insight_service.py  # AI insight generation
├── ml/
│   ├── __init__.py
│   ├── train_model.py      # KMeans clustering model training
│   ├── anomaly_model.pkl   # Saved Isolation Forest model
│   └── kmeans_model.pkl    # Saved KMeans model
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Installation & Setup

### 1. Prerequisites

- Python 3.8 or higher
- MongoDB (local or cloud)
- pip package manager

### 2. Clone & Environment Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# MONGODB_URI=mongodb://localhost:27017/
# ENVIRONMENT=development
# PORT=8000
```

### 5. Start MongoDB

```bash
# Local MongoDB (if installed)
mongod

# Or use MongoDB Atlas cloud: Update MONGODB_URI in .env
```

### 6. Run Backend

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health & Status

- **GET `/`** - Root endpoint, service status
  ```json
  {
    "project": "EnerSense AI",
    "status": "running",
    "version": "1.0.0"
  }
  ```

- **GET `/health`** - Comprehensive health check
- **GET `/ready`** - Readiness probe (for Docker/Kubernetes)

### Sensor Data

- **POST `/api/v1/sensor-data`** - Receive ESP32 sensor data
  ```json
  {
    "device_id": "esp32_01",
    "current": 0.8,
    "power": 180
  }
  ```

- **POST `/api/v1/sensor-data/batch`** - Batch insert multiple readings

### Usage Data

- **GET `/api/v1/live-usage?device_id=esp32_01`** - Get latest sensor reading
  ```json
  {
    "device_id": "esp32_01",
    "current": 0.8,
    "power": 180,
    "timestamp": "2026-05-30T14:23:45Z"
  }
  ```

### History

- **GET `/api/v1/history?device_id=esp32_01&hours=24`** - Get historical logs (1-720 hours)
- **GET `/api/v1/history?device_id=esp32_01&days=7`** - Get historical logs (1-365 days)
- **GET `/api/v1/history/summary?device_id=esp32_01&hours=24`** - Get summary statistics

### AI Insights

- **GET `/api/v1/insights?device_id=esp32_01`** - Generate AI insights
  ```json
  {
    "energy_score": 75,
    "estimated_cost_rm": 1.4275,
    "behavior_profile": {
      "avg_power": 150.5,
      "avg_current": 0.65,
      "peak_hour": 19,
      "usage_pattern": "normal"
    },
    "insights": [
      "Your current power consumption is 180W...",
      "Peak usage occurs at 19:00 (7 PM)..."
    ]
  }
  ```

- **POST `/api/v1/insights/train-profile?device_id=esp32_01&days=7`** - Train user profile
- **GET `/api/v1/insights/profile?device_id=esp32_01`** - Get stored user profile

## Database Collections

### energy_logs
Stores all sensor readings with timestamps.
```json
{
  "device_id": "esp32_01",
  "current": 0.8,
  "power": 180,
  "timestamp": "2026-05-30T14:23:45Z"
}
```

### user_profiles
Stores learned user behavior patterns.
```json
{
  "device_id": "esp32_01",
  "avg_power": 150.5,
  "avg_current": 0.65,
  "peak_hour": 19,
  "usage_pattern": "normal",
  "updated_at": "2026-05-30T14:23:45Z"
}
```

### ai_insights
Stores generated insights and recommendations.
```json
{
  "device_id": "esp32_01",
  "energy_score": 75,
  "estimated_cost_rm": 1.4275,
  "insights": ["..."],
  "timestamp": "2026-05-30T14:23:45Z"
}
```

## Services Overview

### Cost Service (`services/cost_service.py`)
- Calculates energy consumption in kWh
- Estimates cost using Malaysian tariff (RM0.571/kWh)
- Supports hourly, monthly, and annual calculations

### Behavior Service (`services/behavior_service.py`)
- Analyzes historical energy data using pandas
- Calculates average power/current
- Identifies peak usage hours
- Classifies usage patterns (low/normal/high)

### Anomaly Service (`services/anomaly_service.py`)
- Isolation Forest ML model for anomaly detection
- Detects unusual energy consumption spikes
- Provides confidence scores
- Auto-saves trained model using joblib

### Insight Service (`services/insight_service.py`)
- Generates AI-powered human-readable insights
- Calculates energy efficiency scores (0-100)
- Provides personalized recommendations
- Integrates data from all other services

## ML Models

### Anomaly Detection
- **Algorithm**: Isolation Forest
- **Features**: Power (W), Current (A)
- **Model File**: `ml/anomaly_model.pkl`
- **Auto-trained** when sufficient data available

### Usage Clustering
- **Algorithm**: KMeans (3 clusters)
- **Clusters**: low usage, normal usage, high usage
- **Features**: Power, Current
- **Model File**: `ml/kmeans_model.pkl`
- **Requires manual training** via API

## Training ML Models

### Train Anomaly Detection
```python
from services.anomaly_service import detector
from db.mongo import db_client

# Get historical data
logs = db_client.get_energy_logs_by_days("esp32_01", 30)

# Train model
detector.train(logs)
```

### Train KMeans Clustering
```python
from ml.train_model import clusterer
from db.mongo import db_client

# Get historical data
logs = db_client.get_energy_logs_by_days("esp32_01", 30)

# Train model
clusterer.train(logs)
```

## Usage Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Send sensor data
sensor_data = {
    "device_id": "esp32_01",
    "current": 0.8,
    "power": 180
}
response = requests.post(f"{BASE_URL}/sensor-data", json=sensor_data)
print(response.json())

# Get live usage
response = requests.get(f"{BASE_URL}/live-usage?device_id=esp32_01")
print(response.json())

# Get 24-hour history
response = requests.get(f"{BASE_URL}/history?device_id=esp32_01&hours=24")
print(response.json())

# Get AI insights
response = requests.get(f"{BASE_URL}/insights?device_id=esp32_01")
print(response.json())
```

### cURL Examples

```bash
# Send sensor data
curl -X POST http://localhost:8000/api/v1/sensor-data \
  -H "Content-Type: application/json" \
  -d '{"device_id":"esp32_01","current":0.8,"power":180}'

# Get live usage
curl http://localhost:8000/api/v1/live-usage?device_id=esp32_01

# Get history
curl http://localhost:8000/api/v1/history?device_id=esp32_01&hours=24

# Get insights
curl http://localhost:8000/api/v1/insights?device_id=esp32_01
```

## Configuration

### Environment Variables

```env
# MongoDB connection (required)
MONGODB_URI=mongodb://localhost:27017/

# Server settings
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# Electricity tariff (Malaysia)
TARIFF_RM_PER_KWH=0.571
```

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Custom Docs**: http://localhost:8000/docs-custom

## Logging

Logs are configured to show:
- Timestamp
- Logger name
- Log level (INFO, ERROR, WARNING)
- Message

Increase verbosity by setting in `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Error Handling

All endpoints return standardized error responses:

```json
{
  "success": false,
  "error": "Error message",
  "detail": "Additional details"
}
```

Common HTTP Status Codes:
- `200` - Success
- `400` - Bad request (missing parameters)
- `404` - Resource not found
- `500` - Server error

## Performance Optimization

- Database indexes on `device_id` and `timestamp`
- MongoDB connection pooling
- Efficient pandas operations for data analysis
- Model caching with joblib
- Async endpoints with FastAPI

## Security Considerations

- CORS enabled for development (restrict in production)
- Input validation with Pydantic
- SQL injection N/A (MongoDB)
- Rate limiting (add if needed)
- Authentication (implement as needed)

## Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes

Ready for deployment with `/health` and `/ready` endpoints.

### Docker Compose

```yaml
version: '3.8'
services:
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
  
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      MONGODB_URI: mongodb://mongodb:27017/
    depends_on:
      - mongodb
```

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running
- Check MONGODB_URI in .env
- Verify network connectivity

### Port Already in Use
```bash
# Find process on port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Contributing

1. Follow PEP 8 style guide
2. Add type hints to functions
3. Write docstrings for modules and functions
4. Test endpoints before committing

## License

MIT License - See LICENSE file

## Support

For issues and questions:
1. Check documentation
2. Review error logs
3. Test with provided examples
4. Check MongoDB connection
   ```

## Configuration

Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

## Running the Backend

**Start the FastAPI server:**
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /` - System status
- `GET /health` - Health check

### Sensor Data
- `POST /api/sensor-data` - Receive IoT sensor data
- `GET /api/sensor-data` - Retrieve sensor data

### Insights
- `GET /api/insights` - Generate AI insights
- `GET /api/insights/summary` - Quick summary

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Training ML Model

Run the training script:
```bash
python -m ml.train
```

This will:
1. Fetch data from MongoDB `energy_logs` collection
2. Train a KMeans clustering model
3. Save the model as `ml/model.pkl`

## Testing

Example sensor data POST request:
```bash
curl -X POST "http://localhost:8000/api/sensor-data" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32_001",
    "timestamp": "2026-05-30T10:30:00Z",
    "voltage": 230.5,
    "current": 5.2,
    "power": 1198.6
  }'
```

Get insights:
```bash
curl "http://localhost:8000/api/insights"
```

## Features

✅ Real-time sensor data ingestion
✅ MongoDB data storage
✅ AI-powered energy analysis
✅ Pattern detection with KMeans clustering
✅ RESTful API with OpenAPI documentation
✅ CORS enabled for Flutter frontend
✅ Production-ready error handling
✅ Comprehensive logging

## Development

- All code follows PEP 8 style guide
- Modular structure for easy maintenance
- Type hints for better IDE support
- Error handling with proper HTTP status codes
- MongoDB indexing for performance

## Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Use a production ASGI server (Gunicorn + Uvicorn)
3. Configure proper CORS origins
4. Use environment-specific MongoDB connection strings
5. Enable logging to file

## License

MIT License
