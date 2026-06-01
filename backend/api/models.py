"""
Pydantic models for request/response validation and data representation.

Models for:
- Sensor data from ESP32
- Energy logs
- User profiles
- AI insights
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


# ==================== SENSOR DATA ====================

class SensorDataRequest(BaseModel):
    """Request model for ESP32 sensor data."""
    
    device_id: str = Field(..., description="ESP32 device identifier")
    voltage: float = Field(240.0, description="Voltage reading in Volts", ge=0)
    current: float = Field(..., description="Current reading in Amperes", ge=0)
    power: float = Field(..., description="Power reading in Watts", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "esp32_01",
                "voltage": 240.0,
                "current": 0.8,
                "power": 180
            }
        }


class SensorDataResponse(BaseModel):
    """Response model for sensor data."""
    
    device_id: str
    voltage: float = 240.0
    current: float
    power: float
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "esp32_01",
                "voltage": 240.0,
                "current": 0.8,
                "power": 180,
                "timestamp": "2026-05-30T14:23:45Z"
            }
        }


# ==================== ENERGY LOGS ====================

class EnergyLogResponse(BaseModel):
    """Response model for energy log records."""
    
    timestamp: str
    current: float
    power: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-05-30T14:23:45Z",
                "current": 0.8,
                "power": 180
            }
        }


# ==================== COST CALCULATION ====================

class CostEstimateResponse(BaseModel):
    """Response model for cost estimation."""
    
    energy_kwh: float = Field(..., description="Energy consumption in kilowatt-hours")
    estimated_cost_rm: float = Field(..., description="Estimated cost in Malaysian Ringgit")
    
    class Config:
        json_schema_extra = {
            "example": {
                "energy_kwh": 2.5,
                "estimated_cost_rm": 1.4275
            }
        }


# ==================== USER PROFILE ====================

class UserProfileResponse(BaseModel):
    """Response model for user behavior profile."""
    
    avg_power: float = Field(..., description="Average power consumption in Watts")
    avg_current: float = Field(..., description="Average current in Amperes")
    peak_hour: int = Field(..., description="Peak usage hour (0-23)")
    usage_pattern: Literal["low", "normal", "high"] = Field(..., description="Usage pattern classification")
    
    class Config:
        json_schema_extra = {
            "example": {
                "avg_power": 150.5,
                "avg_current": 0.65,
                "peak_hour": 19,
                "usage_pattern": "normal"
            }
        }


# ==================== ANOMALY DETECTION ====================

class AnomalyDetectionResponse(BaseModel):
    """Response model for anomaly detection results."""
    
    is_anomaly: bool = Field(..., description="Whether an anomaly was detected")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)", ge=0.0, le=1.0)
    message: str = Field(..., description="Human-readable anomaly message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_anomaly": False,
                "confidence": 0.95,
                "message": "Power consumption is within normal range"
            }
        }


# ==================== AI INSIGHTS ====================

class AiInsightsResponse(BaseModel):
    """Response model for AI insights."""
    
    energy_score: int = Field(..., description="Energy efficiency score (0-100)", ge=0, le=100)
    estimated_cost_rm: float = Field(..., description="Estimated cost in Malaysian Ringgit")
    behavior_profile: UserProfileResponse = Field(..., description="User behavior profile")
    insights: List[str] = Field(..., description="List of human-readable insights")
    
    class Config:
        json_schema_extra = {
            "example": {
                "energy_score": 75,
                "estimated_cost_rm": 1.4275,
                "behavior_profile": {
                    "avg_power": 150.5,
                    "avg_current": 0.65,
                    "peak_hour": 19,
                    "usage_pattern": "normal"
                },
                "insights": [
                    "Your average power consumption is 150.5W.",
                    "Peak usage occurs at 19:00 (7 PM).",
                    "You may save RM10/month by reducing high-usage periods."
                ]
            }
        }


# ==================== API RESPONSES ====================

class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""
    
    project: str
    status: str
    database: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "project": "EnerSense AI",
                "status": "running",
                "database": {
                    "status": "healthy",
                    "collections": ["energy_logs", "user_profiles", "ai_insights"]
                }
            }
        }


class SuccessResponse(BaseModel):
    """Generic success response model."""
    
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Generic error response model."""
    
    success: bool = False
    error: str
    detail: Optional[str] = None


# ==================== ALERTS ====================

class AlertResponse(BaseModel):
    """Response model for energy alerts."""
    
    alert: bool = Field(..., description="Whether an alert was triggered")
    level: Optional[Literal["warning", "critical"]] = Field(None, description="Alert severity level")
    type: Optional[Literal["HIGH_USAGE", "CRITICAL_USAGE", "SUDDEN_SPIKE"]] = Field(None, description="Alert type")
    message: str = Field(..., description="Human-readable alert message")
    current_power: float = Field(..., description="Current power consumption in Watts")
    avg_power: float = Field(..., description="Average power consumption in Watts")
    std_power: float = Field(..., description="Standard deviation of power in Watts")
    timestamp: str = Field(..., description="Alert timestamp in ISO format")
    threshold_exceeded: Optional[float] = Field(None, description="Amount threshold was exceeded by (Watts)")
    spike_percentage: Optional[float] = Field(None, description="Spike percentage increase")
    
    class Config:
        json_schema_extra = {
            "example": {
                "alert": True,
                "level": "warning",
                "type": "HIGH_USAGE",
                "message": "WARNING: Energy consumption is 1500W, exceeding threshold of 1200W",
                "current_power": 1500.0,
                "avg_power": 800.5,
                "std_power": 150.25,
                "timestamp": "2026-05-31T15:30:00Z",
                "threshold_exceeded": 300.0,
                "spike_percentage": None
            }
        }


class LatestAlertResponse(BaseModel):
    """Response model for latest alert endpoint."""
    
    device_id: str = Field(..., description="Device ID")
    alert_data: Optional[AlertResponse] = Field(None, description="Latest alert data")
    has_active_alert: bool = Field(..., description="Whether device has active alert")
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "esp32_01",
                "has_active_alert": True,
                "alert_data": {
                    "alert": True,
                    "level": "critical",
                    "type": "CRITICAL_USAGE",
                    "message": "CRITICAL: Energy consumption is 2500W, exceeding threshold of 2000W",
                    "current_power": 2500.0,
                    "avg_power": 800.5,
                    "std_power": 150.25,
                    "timestamp": "2026-05-31T15:30:00Z",
                    "threshold_exceeded": 500.0,
                    "spike_percentage": None
                }
            }
        }

