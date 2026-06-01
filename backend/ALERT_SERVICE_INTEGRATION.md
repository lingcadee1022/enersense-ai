"""
ALERT SERVICE INTEGRATION GUIDE

This document explains how to integrate the Alert Service with existing
endpoints and how to use it in production.
"""

# ==================== INTEGRATION OVERVIEW ====================
"""
The Alert Service can be integrated at multiple points:

1. POST /sensor-data Endpoint (Recommended)
   - Generate alerts when new sensor data arrives
   - Automatic real-time alert detection
   
2. Manual Endpoint (For testing)
   - POST /alerts/generate
   - Manually trigger alert generation
   
3. Scheduled Background Tasks
   - Periodically check for alerts
   - Clean up old alerts
"""

# ==================== INTEGRATION EXAMPLE 1: SENSOR ENDPOINT ====================
"""
Modify backend/api/sensor.py to generate alerts automatically:

```python
from services.alert_service import AlertService

@router.post("/sensor-data", response_model=SuccessResponse)
async def receive_sensor_data(data: SensorDataRequest) -> SuccessResponse:
    """Receive sensor data and generate alerts."""
    
    try:
        # Store sensor data
        log_id = db_client.insert_energy_log(
            device_id=data.device_id,
            current=data.current,
            power=data.power
        )
        
        # Get previous reading for spike detection
        previous_log = db_client.get_latest_energy_log(data.device_id)
        previous_power = previous_log.get("power") if previous_log else None
        
        # Generate alert
        alert_response = AlertService.generate_alert(
            device_id=data.device_id,
            current_power=data.power,
            previous_power=previous_power,
            hours_window=24
        )
        
        return SuccessResponse(
            success=True,
            message="Sensor data stored and processed",
            data={
                "energy_log_id": log_id,
                "alert": alert_response
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```
"""

# ==================== INTEGRATION EXAMPLE 2: MANUAL ALERT GENERATION ====================
"""
Add a new endpoint to manually generate alerts for testing:

File: backend/api/alerts.py

```python
from fastapi import APIRouter, HTTPException, status, Body
from services.alert_service import AlertService

@router.post("/alerts/generate", response_model=AlertResponse)
async def generate_alert_manual(
    device_id: str = Query("esp32_01"),
    current_power: float = Body(..., description="Current power reading in Watts"),
    previous_power: Optional[float] = Body(None, description="Previous power reading"),
    hours_window: int = Body(24, description="Hours of historical data to analyze")
) -> AlertResponse:
    '''
    Manually generate an alert for testing purposes.
    
    Request body:
    {
        "current_power": 1800.0,
        "previous_power": 1200.0,
        "hours_window": 24
    }
    
    Returns: AlertResponse
    '''
    try:
        alert = AlertService.generate_alert(
            device_id=device_id,
            current_power=current_power,
            previous_power=previous_power,
            hours_window=hours_window
        )
        return AlertResponse(**alert)
    except Exception as e:
        logger.error(f"Error generating alert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
```
"""

# ==================== INTEGRATION EXAMPLE 3: BACKGROUND TASK ====================
"""
Use APScheduler for periodic alert checks:

File: backend/tasks.py

```python
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from db.mongo import db_client
from services.alert_service import AlertService

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def cleanup_old_alerts():
    '''Remove alerts older than 30 days.'''
    try:
        db = db_client.get_db()
        result = db.alerts.delete_many({
            "timestamp": {"$lt": (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"}
        })
        logger.info(f"Cleanup: Removed {result.deleted_count} old alerts")
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")

def check_device_alerts():
    '''Periodically check for alerts on all devices.'''
    try:
        db = db_client.get_db()
        
        # Get all unique device IDs
        devices = db.energy_logs.distinct("device_id")
        
        for device_id in devices:
            # Get latest reading
            latest_log = db_client.get_latest_energy_log(device_id)
            
            if not latest_log:
                continue
            
            # Generate alert
            alert = AlertService.generate_alert(
                device_id=device_id,
                current_power=latest_log.get("power", 0),
                hours_window=24
            )
            
            logger.info(f"Periodic check - Device {device_id}: alert={alert.get('alert')}")
            
    except Exception as e:
        logger.error(f"Periodic check error: {str(e)}")

def start_scheduler():
    '''Start the background scheduler.'''
    # Check for alerts every 5 minutes
    scheduler.add_job(
        check_device_alerts,
        'interval',
        minutes=5,
        id='check_alerts'
    )
    
    # Cleanup old alerts daily at 2 AM
    scheduler.add_job(
        cleanup_old_alerts,
        'cron',
        hour=2,
        minute=0,
        id='cleanup_alerts'
    )
    
    scheduler.start()
    logger.info("Background scheduler started")

def stop_scheduler():
    '''Stop the background scheduler.'''
    scheduler.shutdown()
    logger.info("Background scheduler stopped")
```

In main.py:

```python
from contextlib import asynccontextmanager
from tasks import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db_client.connect()
    start_scheduler()
    yield
    
    # Shutdown
    stop_scheduler()
    db_client.disconnect()
```
"""

# ==================== ALERT CONFIGURATION ====================
"""
Alert thresholds can be customized in backend/services/alert_service.py:

```python
class AlertService:
    # Thresholds (standard deviations)
    HIGH_USAGE_THRESHOLD = 2.0          # 2 sigma
    CRITICAL_USAGE_THRESHOLD = 3.0      # 3 sigma
    SUDDEN_SPIKE_MULTIPLIER = 1.5       # 1.5x previous
    
    # Minimum data points needed
    MIN_DATA_POINTS = 5
```

Production Recommendations:
- HIGH_USAGE_THRESHOLD: 2.0 (good balance between sensitivity and false positives)
- CRITICAL_USAGE_THRESHOLD: 3.0 (only for severe anomalies)
- SUDDEN_SPIKE_MULTIPLIER: 1.5-2.0 (1.5 is quite sensitive, 2.0 is more conservative)
"""

# ==================== FRONTEND INTEGRATION ====================
"""
Mobile App Integration (Flutter):

In lib/services/api_service.dart:

```dart
// Get latest alert
Future<Map<String, dynamic>> getLatestAlert() async {
  try {
    final response = await httpClient
        .get(Uri.parse('$baseUrl/api/v1/alerts/latest'))
        .timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return {};
  } catch (e) {
    print('Error fetching alert: $e');
    return {};
  }
}

// Get alert history
Future<List<dynamic>> getAlertHistory({
  String level = 'warning',
  int hours = 24,
  int limit = 10,
}) async {
  try {
    final response = await httpClient
        .get(Uri.parse(
          '$baseUrl/api/v1/alerts/history'
          '?level=$level&hours=$hours&limit=$limit'
        ))
        .timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return [];
  } catch (e) {
    print('Error fetching alerts: $e');
    return [];
  }
}
```

In UI:

```dart
// Show alert banner if active
if (latestAlert['has_active_alert']) {
  final alert = latestAlert['alert_data'];
  showAlertBanner(
    level: alert['level'],  // 'warning' or 'critical'
    message: alert['message'],
    currentPower: alert['current_power']
  );
}
```
"""

# ==================== TESTING ====================
"""
Run the example script to test the Alert Service:

```bash
cd backend
python alert_service_examples.py
```

Manual Testing with curl:

1. Get latest alert:
```bash
curl http://localhost:8000/api/v1/alerts/latest?device_id=esp32_01
```

2. Get alert history:
```bash
curl "http://localhost:8000/api/v1/alerts/history?device_id=esp32_01&hours=24&limit=10"
```

3. Get critical alerts only:
```bash
curl "http://localhost:8000/api/v1/alerts/critical?device_id=esp32_01&limit=10"
```

4. Send sensor data (which generates alerts):
```bash
curl -X POST http://localhost:8000/api/v1/sensor-data \\
  -H "Content-Type: application/json" \\
  -d '{
    "device_id": "esp32_01",
    "power": 2500,
    "current": 10.4
  }'
```
"""

# ==================== PRODUCTION CHECKLIST ====================
"""
Before deploying to production:

[ ] Review alert thresholds for your use case
[ ] Set up MongoDB indexes for optimal query performance
[ ] Configure CORS properly (restrict to known origins)
[ ] Set up SSL/TLS certificates
[ ] Implement rate limiting on alert endpoints
[ ] Set up monitoring/alerting for alert service failures
[ ] Configure log rotation and storage
[ ] Set up backup strategy for MongoDB
[ ] Test alert generation with realistic data
[ ] Document alert thresholds and meanings for users
[ ] Set up alert notification system (email, SMS, push)
[ ] Monitor database storage for alert collection growth
[ ] Plan for alert retention policy (e.g., keep 30 days)
"""

# ==================== PERFORMANCE OPTIMIZATION ====================
"""
Optimization Tips:

1. Database Indexes (Already implemented):
   - Indexes on device_id, timestamp, level
   - Composite indexes for common queries
   - Dramatically speeds up alert retrieval

2. Query Optimization:
   - Use limit() to restrict result sets
   - Use projections to exclude unnecessary fields
   - Use batch operations for bulk inserts

3. Caching:
   - Cache user profiles to avoid recalculation
   - Cache statistical values for recent data
   - Use Redis for high-frequency queries

4. Data Retention:
   - Archive old alerts to separate collection
   - Set TTL (Time To Live) on alert documents
   - Regularly clean up obsolete data

Example MongoDB TTL:
```
db.alerts.createIndex(
    {"inserted_at": 1},
    {expireAfterSeconds: 2592000}  # 30 days
)
```
"""

# ==================== TROUBLESHOOTING ====================
"""
Common Issues:

1. No Alerts Generated
   - Check if energy_logs collection has data
   - Verify device_id matches
   - Check alert thresholds aren't too high
   - Review logs: tail -f logs/backend.log

2. Alerts Not Stored
   - Verify MongoDB connection is active
   - Check DB indexes are created
   - Ensure alerts collection has write permissions

3. Slow Alert Retrieval
   - Verify indexes exist: db.alerts.getIndexes()
   - Check query performance: db.alerts.find(...).explain()
   - Consider implementing query optimization

4. False Positives
   - Increase HIGH_USAGE_THRESHOLD value
   - Increase SUDDEN_SPIKE_MULTIPLIER
   - Review MIN_DATA_POINTS requirement
   - Check device is calibrated correctly
"""

print(__doc__)
