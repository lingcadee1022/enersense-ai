# Integration Guide - AI/ML with Backend & Frontend

## Architecture Overview

```
┌─────────────────┐
│   ESP32/Sensor  │
└────────┬────────┘
         │ WiFi/MQTT
         ↓
┌─────────────────────────────┐
│   Backend Server            │
│  (Node.js / Python / Go)    │
│  - Data validation          │
│  - Database storage         │
│  - Request routing          │
└────────┬────────────────────┘
         │ HTTP/REST
         ↓
┌─────────────────────────────┐
│   AI/ML Service             │
│   (FastAPI - port 8000)     │
│  - Appliance prediction     │
│  - Anomaly detection        │
│  - Recommendations          │
│  - Forecasting              │
└────────┬────────────────────┘
         │ JSON Response
         ↓
┌─────────────────────────────┐
│   Flutter Frontend          │
│   (Mobile Dashboard)        │
│  - Live usage display       │
│  - Recommendations UI       │
│  - Appliance breakdown      │
│  - Cost predictions         │
└─────────────────────────────┘
```

## Integration Points

### 1. Backend to AI/ML Service

#### Incoming Request (from Backend)
```
POST /sensor-data
{
  "timestamp": "2026-05-12T15:30:00",
  "power": 1200,
  "voltage": 240,
  "current": 5.0
}
```

#### Processing Flow
```python
# In ai-model/api_service.py
@app.post("/sensor-data")
async def process_sensor_data(reading: SensorReading):
    # 1. Predict appliance
    appliance = predict_appliance(power, voltage, current)
    
    # 2. Detect anomalies
    anomaly_result = analyze_reading(power, appliance)
    
    # 3. Track for recommendations
    add_rec_reading(power, appliance)
    
    # 4. Update forecasts
    add_forecast_reading(power)
    
    # 5. Return response
    return LiveUsageResponse(...)
```

#### Response (back to Backend)
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

### 2. Backend to Frontend

The Backend acts as a relay and may enhance the response:

```
Backend receives from AI ↓
  {
    "predicted_appliance": "Air Conditioner",
    "energy_score": 34,
    ...
  }
↓
Backend adds context:
  {
    "predicted_appliance": "Air Conditioner",
    "energy_score": 34,
    "user_id": "user123",           // From database
    "timestamp": "2026-05-12T...",
    "device_id": "sensor001",       // From database
    ...
  }
↓
Frontend displays in UI
```

### 3. Pulling Data (Frontend asks Backend for insights)

#### Request
```
GET /api/insights
Authorization: Bearer <token>
```

#### Backend queries AI
```python
# Backend code
response = requests.get('http://localhost:8000/insights')
insights = response.json()
```

#### Backend returns to Frontend
```json
{
  "insights": [
    "AC usage unusually high today",
    "Potential monthly savings: RM 20"
  ],
  "recommendations": [...],
  "timestamp": "2026-05-12T15:30:00"
}
```

## Step-by-Step Integration

### Phase 1: Backend Setup (Teammate 2)

1. **Start AI/ML Service**
```bash
cd ai-model
python api_service.py  # Runs on http://localhost:8000
```

2. **Create Backend Endpoint**
```python
# Example: Node.js/Express
const axios = require('axios');

app.post('/api/sensor-data', async (req, res) => {
    try {
        // Forward to AI service
        const response = await axios.post(
            'http://localhost:8000/sensor-data',
            {
                timestamp: req.body.timestamp,
                power: req.body.power,
                voltage: req.body.voltage,
                current: req.body.current
            }
        );
        
        // Enhance with database info
        const result = {
            ...response.data,
            user_id: req.user.id,
            device_id: req.body.device_id
        };
        
        // Store in database
        await saveSensorReading(result);
        
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});
```

3. **Test Integration**
```bash
curl -X POST http://localhost:3000/api/sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-05-12T15:30:00",
    "power": 1200,
    "voltage": 240,
    "current": 5.0,
    "device_id": "sensor001"
  }'
```

### Phase 2: Frontend Integration (Teammate 3)

1. **Create Flutter Service**
```dart
// lib/services/energy_service.dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class EnergyService {
  static const String apiUrl = 'http://your-backend-url/api';
  
  // Get live usage
  Future<LiveUsage> getLiveUsage() async {
    final response = await http.get(
      Uri.parse('$apiUrl/live-usage'),
      headers: {'Authorization': 'Bearer $token'},
    );
    
    if (response.statusCode == 200) {
      return LiveUsage.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to load live usage');
  }
  
  // Get insights
  Future<Insights> getInsights() async {
    final response = await http.get(
      Uri.parse('$apiUrl/insights'),
      headers: {'Authorization': 'Bearer $token'},
    );
    
    if (response.statusCode == 200) {
      return Insights.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to load insights');
  }
  
  // Get forecast
  Future<Forecast> getForecast() async {
    final response = await http.get(
      Uri.parse('$apiUrl/forecast'),
      headers: {'Authorization': 'Bearer $token'},
    );
    
    if (response.statusCode == 200) {
      return Forecast.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to load forecast');
  }
}
```

2. **Create Models**
```dart
// lib/models/energy_models.dart

class LiveUsage {
  final String timestamp;
  final double power;
  final double voltage;
  final double current;
  final String predictedAppliance;
  final int energyScore;
  final bool isAnomaly;
  final String? anomalyInsight;
  
  LiveUsage({
    required this.timestamp,
    required this.power,
    required this.voltage,
    required this.current,
    required this.predictedAppliance,
    required this.energyScore,
    required this.isAnomaly,
    this.anomalyInsight,
  });
  
  factory LiveUsage.fromJson(Map<String, dynamic> json) {
    return LiveUsage(
      timestamp: json['timestamp'],
      power: (json['power'] as num).toDouble(),
      voltage: (json['voltage'] as num).toDouble(),
      current: (json['current'] as num).toDouble(),
      predictedAppliance: json['predicted_appliance'],
      energyScore: json['energy_score'],
      isAnomaly: json['is_anomaly'],
      anomalyInsight: json['anomaly_insight'],
    );
  }
}

class Insights {
  final List<String> insights;
  final List<dynamic> recommendations;
  final List<dynamic> applianceBreakdown;
  
  Insights({
    required this.insights,
    required this.recommendations,
    required this.applianceBreakdown,
  });
  
  factory Insights.fromJson(Map<String, dynamic> json) {
    return Insights(
      insights: List<String>.from(json['insights']),
      recommendations: json['recommendations'],
      applianceBreakdown: json['appliance_breakdown'],
    );
  }
}

class Forecast {
  final double estimatedDailyKwh;
  final double estimatedMonthlyKwh;
  final double estimatedMonthlyCost;
  final List<int> peakHours;
  final String currency;
  
  Forecast({
    required this.estimatedDailyKwh,
    required this.estimatedMonthlyKwh,
    required this.estimatedMonthlyCost,
    required this.peakHours,
    required this.currency,
  });
  
  factory Forecast.fromJson(Map<String, dynamic> json) {
    return Forecast(
      estimatedDailyKwh: json['estimated_daily_kwh'],
      estimatedMonthlyKwh: json['estimated_monthly_kwh'],
      estimatedMonthlyCost: json['estimated_monthly_cost'],
      peakHours: List<int>.from(json['peak_hours']),
      currency: json['currency'],
    );
  }
}
```

3. **Display in UI**
```dart
// lib/screens/dashboard.dart
import 'package:flutter/material.dart';
import '../services/energy_service.dart';
import '../models/energy_models.dart';

class DashboardScreen extends StatefulWidget {
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  late EnergyService _energyService;
  LiveUsage? _liveUsage;
  Insights? _insights;
  Forecast? _forecast;

  @override
  void initState() {
    super.initState();
    _energyService = EnergyService();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final liveUsage = await _energyService.getLiveUsage();
      final insights = await _energyService.getInsights();
      final forecast = await _energyService.getForecast();
      
      setState(() {
        _liveUsage = liveUsage;
        _insights = insights;
        _forecast = forecast;
      });
    } catch (e) {
      print('Error loading data: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Energy Dashboard'),
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: ListView(
          padding: EdgeInsets.all(16),
          children: [
            // Live Usage Card
            if (_liveUsage != null)
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Live Usage', 
                        style: Theme.of(context).textTheme.titleLarge),
                      SizedBox(height: 8),
                      Text('Appliance: ${_liveUsage!.predictedAppliance}'),
                      Text('Power: ${_liveUsage!.power}W'),
                      Text('Energy Score: ${_liveUsage!.energyScore}/100'),
                      if (_liveUsage!.isAnomaly)
                        Padding(
                          padding: EdgeInsets.only(top: 8),
                          child: Text(
                            '⚠️ ${_liveUsage!.anomalyInsight}',
                            style: TextStyle(color: Colors.orange),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            
            // Forecast Card
            if (_forecast != null)
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Monthly Forecast',
                        style: Theme.of(context).textTheme.titleLarge),
                      SizedBox(height: 8),
                      Text('Estimated Cost: ${_forecast!.currency} ${_forecast!.estimatedMonthlyCost.toStringAsFixed(2)}'),
                      Text('Monthly Usage: ${_forecast!.estimatedMonthlyKwh.toStringAsFixed(2)} kWh'),
                    ],
                  ),
                ),
              ),
            
            // Insights Card
            if (_insights != null)
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Recommendations',
                        style: Theme.of(context).textTheme.titleLarge),
                      SizedBox(height: 8),
                      ..._insights!.insights.map(
                        (insight) => Padding(
                          padding: EdgeInsets.symmetric(vertical: 4),
                          child: Text('• $insight'),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
```

## Testing the Integration

### Test 1: Send Data End-to-End
```bash
# 1. Start AI/ML service
python api_service.py

# 2. In another terminal, test direct call
curl -X POST http://localhost:8000/sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-05-12T15:30:00",
    "power": 1500,
    "voltage": 240,
    "current": 6.25
  }'

# Expected: AC appliance predicted
```

### Test 2: Verify Flask gets all endpoints
```bash
# Get insights
curl http://localhost:8000/insights

# Get forecast
curl http://localhost:8000/forecast

# Get live usage
curl http://localhost:8000/live-usage

# Health check
curl http://localhost:8000/health
```

## Deployment Considerations

### Development
```bash
# AI runs on localhost:8000
# Backend runs on localhost:3000/5000/8080
# Frontend runs on Flutter emulator
```

### Production
```
Docker container for AI/ML service
Backend API Gateway routes requests
Flutter app targets production API
Database stores historical data
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| AI service not responding | Check if `python api_service.py` is running |
| CORS errors | Add correct origins to FastAPI middleware |
| Models not loaded | Run `python model_training.py` |
| Port already in use | Change port in `api_service.py` |
| Slow responses | Check if models are cached properly |

---

**Ready to integrate!** Follow the phases in order for smooth integration.
