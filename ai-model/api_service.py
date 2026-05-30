"""
FastAPI Service - AI/ML Integration API
Provides endpoints for energy analysis and recommendations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uvicorn

from appliance_classifier import predict_appliance, get_energy_score
from anomaly_detection import analyze_reading
from recommendation_engine import add_reading as add_rec_reading, get_recommendations, get_appliance_insights
from forecasting import add_reading as add_forecast_reading, forecast_monthly, get_peak_hours

# Pydantic models
class SensorReading(BaseModel):
    """Sensor reading from ESP32"""
    timestamp: str
    power: float
    voltage: float
    current: float


class LiveUsageResponse(BaseModel):
    """Response for live usage endpoint"""
    timestamp: str
    power: float
    voltage: float
    current: float
    predicted_appliance: str
    energy_score: int
    is_anomaly: bool
    anomaly_insight: Optional[str] = None


class InsightsResponse(BaseModel):
    """Response for insights endpoint"""
    insights: List[str]
    recommendations: List[dict]
    appliance_breakdown: List[dict]


class ForecastResponse(BaseModel):
    """Response for forecast endpoint"""
    estimated_daily_kwh: float
    estimated_monthly_kwh: float
    estimated_monthly_cost: float
    peak_hours: List[int]
    currency: str


# Create FastAPI app
app = FastAPI(
    title="EnerSense AI API",
    description="AI/ML Energy Analysis Service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory storage for insights
insights_history = []


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("✓ EnerSense AI API starting...")
    print("✓ Available endpoints:")
    print("  - POST /sensor-data")
    print("  - GET /live-usage")
    print("  - GET /insights")
    print("  - GET /forecast")
    print("  - GET /appliances")


@app.post("/sensor-data", response_model=LiveUsageResponse)
async def process_sensor_data(reading: SensorReading) -> LiveUsageResponse:
    """
    Process sensor data from ESP32
    
    - **timestamp**: ISO 8601 timestamp
    - **power**: Power consumption in watts
    - **voltage**: Voltage in volts
    - **current**: Current in amperes
    """
    try:
        # Predict appliance
        appliance = predict_appliance(reading.power, reading.voltage, reading.current)
        
        # Calculate energy score
        energy_score = get_energy_score(reading.power)
        
        # Detect anomalies
        anomaly_result = analyze_reading(reading.power, appliance)
        
        # Add to recommendation engine
        add_rec_reading(reading.power, appliance)
        add_forecast_reading(reading.power)
        
        # Generate response
        response = LiveUsageResponse(
            timestamp=reading.timestamp,
            power=reading.power,
            voltage=reading.voltage,
            current=reading.current,
            predicted_appliance=appliance,
            energy_score=energy_score,
            is_anomaly=anomaly_result['is_anomaly'],
            anomaly_insight=anomaly_result.get('insight')
        )
        
        # Store for history
        insights_history.append({
            'timestamp': reading.timestamp,
            'appliance': appliance,
            'power': reading.power,
            'anomaly': anomaly_result['is_anomaly']
        })
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/live-usage", response_model=LiveUsageResponse)
async def get_live_usage() -> LiveUsageResponse:
    """
    Get latest live usage data
    Returns the most recent sensor reading with predictions
    """
    if not insights_history:
        raise HTTPException(status_code=404, detail="No readings available")
    
    latest = insights_history[-1]
    
    return LiveUsageResponse(
        timestamp=latest['timestamp'],
        power=latest.get('power', 0),
        voltage=240,
        current=latest.get('power', 0) / 240,
        predicted_appliance=latest['appliance'],
        energy_score=int((latest.get('power', 0) / 3500) * 100),
        is_anomaly=latest.get('anomaly', False),
        anomaly_insight=None
    )


@app.get("/insights", response_model=InsightsResponse)
async def get_insights() -> InsightsResponse:
    """
    Get AI-generated insights and recommendations
    Returns personalized energy-saving recommendations
    """
    try:
        recommendations = get_recommendations()
        appliance_breakdown = get_appliance_insights()
        
        # Generate text insights
        insights_text = []
        for rec in recommendations:
            if 'recommendation' in rec:
                insights_text.append(rec['recommendation'])
        
        return InsightsResponse(
            insights=insights_text,
            recommendations=recommendations,
            appliance_breakdown=appliance_breakdown
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/forecast", response_model=ForecastResponse)
async def get_forecast() -> ForecastResponse:
    """
    Get energy consumption forecast
    Returns estimated daily/monthly consumption and peak hours
    """
    try:
        forecast = forecast_monthly()
        peak_hours = get_peak_hours()
        
        return ForecastResponse(
            estimated_daily_kwh=forecast['estimated_daily_kwh'],
            estimated_monthly_kwh=forecast['estimated_monthly_kwh'],
            estimated_monthly_cost=forecast['estimated_monthly_cost'],
            peak_hours=peak_hours,
            currency=forecast.get('currency', 'RM')
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/appliances")
async def get_appliances():
    """
    Get appliance usage breakdown
    Returns historical appliance usage data
    """
    try:
        breakdown = get_appliance_insights()
        return {
            'appliances': breakdown,
            'total_readings': len(insights_history),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'EnerSense AI API',
        'timestamp': datetime.now().isoformat(),
        'readings_processed': len(insights_history)
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        'service': 'EnerSense AI API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'sensor_data': 'POST /sensor-data',
            'live_usage': 'GET /live-usage',
            'insights': 'GET /insights',
            'forecast': 'GET /forecast',
            'appliances': 'GET /appliances',
            'health': 'GET /health'
        }
    }


if __name__ == '__main__':
    print("\n" + "="*60)
    print("EnerSense AI - FastAPI Service")
    print("="*60)
    print("\nStarting API server at http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
