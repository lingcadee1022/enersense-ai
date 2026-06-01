# EnerSense AI Backend - Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Flutter Mobile App                            │
│                                                                       │
│  Sends: POST /sensor-data, GET /insights, GET /history              │
│  CORS Enabled: Access from mobile localhost & network                │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FastAPI Application (main.py)                      │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ CORS Middleware | Error Handlers | Lifespan Management      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                          │                                           │
│  ┌───────────────────────┼───────────────────────┐                  │
│  ▼                       ▼                       ▼                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ api/sensor   │  │ api/history  │  │ api/insights │ ...           │
│  │ ├ sensor.py  │  │ └ history.py │  │ └ insights.py│               │
│  │ └ live_usage │  │              │  │              │               │
│  │   .py        │  │              │  │              │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Services Layer (Validation)                       │
│                                                                       │
│  api/models.py                                                       │
│  ├─ SensorDataRequest ─┐                                             │
│  ├─ EnergyLogResponse  │ Pydantic Models for validation              │
│  ├─ AiInsightsResponse │ Input & Output schemas                      │
│  └─ More... ───────────┘                                             │
└─────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│               Business Logic Services Layer                          │
│                                                                       │
│  ┌──────────────────────┐  ┌──────────────────────┐                 │
│  │  services/           │  │  services/           │                 │
│  │  cost_service.py     │  │  behavior_service.py │                 │
│  │                      │  │                      │                 │
│  │ • calculate_cost()   │  │ • analyze_logs()     │                 │
│  │ • monthly_estimate() │  │ • classify_usage()   │                 │
│  │ • annual_estimate()  │  │ • hourly_average()   │                 │
│  └──────────────────────┘  └──────────────────────┘                 │
│                                                                       │
│  ┌──────────────────────┐  ┌──────────────────────┐                 │
│  │  services/           │  │  services/           │                 │
│  │  anomaly_service.py  │  │  insight_service.py  │                 │
│  │                      │  │                      │                 │
│  │ • train()            │  │ • calc_score()       │                 │
│  │ • detect()           │  │ • generate_insights()│                 │
│  │ • detect_batch()     │  │ • get_recommend()    │                 │
│  └──────────────────────┘  └──────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│               Machine Learning Models Layer                          │
│                                                                       │
│  ┌──────────────────────┐  ┌──────────────────────┐                 │
│  │  Isolation Forest    │  │  KMeans Clustering   │                 │
│  │  (anomaly_service)   │  │  (train_model)       │                 │
│  │                      │  │                      │                 │
│  │ • Features: Power,   │  │ • Features: Power,   │                 │
│  │   Current            │  │   Current            │                 │
│  │ • Confidence score   │  │ • 3 Clusters:        │                 │
│  │ • Auto-trained       │  │   - Low usage        │                 │
│  │ • Saves: anomaly     │  │   - Normal usage     │                 │
│  │   _model.pkl         │  │   - High usage       │                 │
│  │                      │  │ • Manual training    │                 │
│  │                      │  │ • Saves: kmeans      │                 │
│  │                      │  │   _model.pkl         │                 │
│  └──────────────────────┘  └──────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│               Database Abstraction Layer (db/mongo.py)               │
│                                                                       │
│  MongoDBClient (Singleton Pattern)                                   │
│  ├─ connect() ─────────────────────────────────────────────┐        │
│  ├─ insert_energy_log()                                    │        │
│  ├─ get_latest_energy_log()                                │        │
│  ├─ get_energy_logs_by_hours()                             │        │
│  ├─ get_energy_logs_by_days()                              │        │
│  ├─ upsert_user_profile()                                  │        │
│  ├─ get_user_profile()                                     │        │
│  ├─ insert_insight()                                       │        │
│  ├─ get_latest_insight()                                   │        │
│  ├─ create_indexes()  ◄──── Database Optimization          │        │
│  └─ health_check() ◄─────── Connection Validation          │        │
└─────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    MongoDB Database                                   │
│                                                                       │
│  Database: "enersense"                                               │
│                                                                       │
│  ┌────────────────────────┐  ┌────────────────────────┐             │
│  │  energy_logs           │  │  user_profiles         │             │
│  │                        │  │                        │             │
│  │ • device_id (index)    │  │ • device_id (unique)   │             │
│  │ • current              │  │ • avg_power            │             │
│  │ • power                │  │ • avg_current          │             │
│  │ • timestamp (index)    │  │ • peak_hour            │             │
│  │   (UTC+Z)              │  │ • usage_pattern        │             │
│  │ • (1M+ documents)      │  │ • updated_at           │             │
│  │                        │  │                        │             │
│  └────────────────────────┘  └────────────────────────┘             │
│                                                                       │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  ai_insights                                           │         │
│  │                                                        │         │
│  │ • device_id (index)                                   │         │
│  │ • energy_score                                        │         │
│  │ • estimated_cost_rm                                   │         │
│  │ • insights (array)                                    │         │
│  │ • behavior_profile (embedded)                         │         │
│  │ • timestamp (index)                                   │         │
│  │   (UTC+Z)                                             │         │
│  └────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
ESP32 Sensor Device
        │
        │ {"device_id": "esp32_01", "current": 0.8, "power": 180}
        │
        ▼
POST /api/v1/sensor-data
        │
        ├─► Pydantic Validation (api/models.py)
        │
        ├─► UTC Timestamp Generation
        │
        ├─► MongoDB Insert (db/mongo.py)
        │   └─► energy_logs collection
        │
        ▼
Data Stored in MongoDB
        │
        ├─► GET /api/v1/live-usage
        │   └─► Get latest reading
        │
        ├─► GET /api/v1/history
        │   └─► Get 24/7/30 day history
        │
        └─► GET /api/v1/insights
            │
            ├─► Retrieve latest sensor data
            │
            ├─► Anomaly Detection Service
            │   ├─► Load ml/anomaly_model.pkl (Isolation Forest)
            │   ├─► Predict on (power, current)
            │   └─► Generate anomaly result
            │
            ├─► Behavior Service
            │   ├─► Fetch 7-day history
            │   ├─► Analyze with pandas
            │   ├─► Generate profile
            │   └─► Store in user_profiles
            │
            ├─► Cost Service
            │   ├─► Calculate kWh = power/1000 × hours
            │   ├─► Apply RM0.571/kWh tariff
            │   └─► Return cost estimate
            │
            ├─► Insight Service
            │   ├─► Combine all results
            │   ├─► Calculate energy score (0-100)
            │   ├─► Generate insights
            │   └─► Create recommendations
            │
            └─► Store in ai_insights collection
                │
                ▼
                Return to Flutter App with:
                {
                  "energy_score": 75,
                  "estimated_cost_rm": 1.4275,
                  "behavior_profile": {...},
                  "insights": [...]
                }
```

## Request/Response Flow for POST /sensor-data

```
┌─────────────────────────────────────────────────────────────┐
│  1. INCOMING REQUEST (Flutter App)                          │
│                                                              │
│  POST /api/v1/sensor-data                                   │
│  Content-Type: application/json                             │
│  {                                                           │
│    "device_id": "esp32_01",                                │
│    "current": 0.8,                                          │
│    "power": 180                                             │
│  }                                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  2. FASTAPI ROUTER (api/sensor.py)                          │
│                                                              │
│  ├─ Receive request                                         │
│  └─ Pass to handler function                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  3. PYDANTIC VALIDATION (api/models.py)                     │
│                                                              │
│  ├─ Parse SensorDataRequest                                │
│  ├─ Validate: device_id (str), current >= 0, power >= 0   │
│  ├─ Type checking                                           │
│  └─ Raise HTTPException if invalid                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  4. BUSINESS LOGIC (api/sensor.py handler)                  │
│                                                              │
│  ├─ Generate UTC timestamp                                  │
│  ├─ Call db_client.insert_energy_log()                      │
│  └─ Get document ID                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  5. DATABASE LAYER (db/mongo.py)                            │
│                                                              │
│  ├─ Prepare document:                                       │
│  │  {                                                       │
│  │    "device_id": "esp32_01",                             │
│  │    "current": 0.8,                                      │
│  │    "power": 180,                                        │
│  │    "timestamp": "2026-05-30T14:23:45Z"                 │
│  │  }                                                       │
│  ├─ Insert into energy_logs collection                      │
│  ├─ Return inserted_id                                      │
│  └─ Log operation                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  6. MONGODB STORAGE                                         │
│                                                              │
│  energy_logs collection:                                    │
│  {                                                           │
│    "_id": ObjectId("..."),                                 │
│    "device_id": "esp32_01",                                │
│    "current": 0.8,                                         │
│    "power": 180,                                           │
│    "timestamp": "2026-05-30T14:23:45Z"                    │
│  }                                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  7. RESPONSE (Back to Flutter)                              │
│                                                              │
│  HTTP 200 OK                                                │
│  Content-Type: application/json                             │
│  {                                                           │
│    "success": true,                                         │
│    "message": "Sensor data stored successfully",            │
│    "data": {                                                │
│      "id": "60d5ec49c1234567890abcde",                     │
│      "timestamp": "2026-05-30T14:23:45Z"                   │
│    }                                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
        Request arrives
              │
              ▼
        FastAPI Router
              │
              ├─ Pydantic Validation Error
              │  └─► HTTP 422 Unprocessable Entity
              │
              ├─ MongoDB Connection Error
              │  └─► HTTP 500 Internal Server Error
              │
              ├─ Resource Not Found
              │  └─► HTTP 404 Not Found
              │
              ├─ Invalid Query Parameters
              │  └─► HTTP 400 Bad Request
              │
              └─ Unhandled Exception
                 └─► HTTP 500 Internal Server Error
                     (Stack trace in development mode)
```

## Configuration & Environment

```
┌─────────────────────────────────────┐
│         Environment Variables        │
│                                      │
│  MONGODB_URI                        │
│  ├─ Default: mongodb://...          │
│  └─ Cloud: mongodb+srv://...        │
│                                      │
│  ENVIRONMENT                        │
│  ├─ development                     │
│  └─ production                      │
│                                      │
│  HOST, PORT                         │
│  ├─ 0.0.0.0:8000                    │
│  └─ Configurable per env            │
│                                      │
│  TARIFF_RM_PER_KWH                 │
│  └─ 0.571 (Malaysia)                │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      config.py (Settings)           │
│                                      │
│  Config class with:                 │
│  ├─ Environment loading             │
│  ├─ Default values                  │
│  ├─ Type validation                 │
│  └─ Helper methods                  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    FastAPI Application              │
│                                      │
│  Uses config for:                   │
│  ├─ DB connections                  │
│  ├─ Server setup                    │
│  ├─ CORS configuration              │
│  └─ Feature flags                   │
└─────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Development (Local)                          │
│                                                              │
│  python main.py                                             │
│  Uvicorn: http://localhost:8000                             │
│  MongoDB: localhost:27017                                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 Docker Container                             │
│                                                              │
│  ├─ Dockerfile (FastAPI app)                               │
│  └─ docker-compose.yml (FastAPI + MongoDB)                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Kubernetes Cluster                              │
│                                                              │
│  ├─ Deployment (FastAPI replicas)                          │
│  ├─ Service (Load balancer)                                │
│  ├─ StatefulSet (MongoDB)                                  │
│  └─ Probes (/health, /ready)                               │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. Singleton Pattern (Database)
```
MongoDBClient._instance
    ├─ Ensures single DB connection
    ├─ Thread-safe
    └─ Efficient resource usage
```

### 2. Repository Pattern
```
db/mongo.py provides:
    ├─ Abstraction layer
    ├─ CRUD operations
    └─ Query builders
```

### 3. Service Layer Pattern
```
services/*.py provide:
    ├─ Business logic separation
    ├─ Reusable functions
    └─ Independent testing
```

### 4. Model Validation (Pydantic)
```
api/models.py provides:
    ├─ Input validation
    ├─ Output formatting
    └─ Type safety
```

### 5. Dependency Injection Ready
```
Services can be injected:
    ├─ Easy testing
    ├─ Loose coupling
    └─ Scalable design
```

## Performance Optimization

```
Database Layer:
├─ Indexes on device_id, timestamp
├─ Composite indexes for queries
└─ Connection pooling

API Layer:
├─ Async endpoints
├─ Efficient queries
└─ Caching potential

ML Layer:
├─ Model caching (joblib)
├─ Batch predictions
└─ Efficient numpy operations

Data Processing:
├─ Pandas for large datasets
├─ Vectorized operations
└─ Minimal copies
```

---

**This architecture is designed for:**
- ✅ Scalability
- ✅ Maintainability
- ✅ Testability
- ✅ Production-readiness
- ✅ Easy deployment
