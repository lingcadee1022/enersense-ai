"""
Real-time energy alerts API endpoint for EnerSense AI.

Endpoints:
- GET /alerts/latest - Get the latest alert for a device
- GET /alerts/history - Get alert history with filters
- GET /alerts/critical - Get critical alerts
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query
from db.mongo import db_client
from api.models import AlertResponse, LatestAlertResponse
from services.alert_service import AlertService
from typing import List, Optional, Literal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Alerts"])


@router.get("/alerts/latest", response_model=LatestAlertResponse)
async def get_latest_alert(
    device_id: str = Query("esp32_01", description="ESP32 device identifier")
) -> LatestAlertResponse:
    """
    Get the latest alert for a device.
    
    Query Parameters:
    - device_id: ESP32 device identifier (default: esp32_01)
    
    Returns:
    {
        "device_id": "esp32_01",
        "has_active_alert": true,
        "alert_data": {
            "alert": true,
            "level": "warning",
            "type": "HIGH_USAGE",
            "message": "WARNING: Energy consumption is 1500W...",
            "current_power": 1500.0,
            "avg_power": 800.5,
            "std_power": 150.25,
            "timestamp": "2026-05-31T15:30:00Z",
            "threshold_exceeded": 300.0
        }
    }
    
    Status Codes:
    - 200: Success (alert data retrieved)
    - 404: Device not found
    - 500: Server error
    """
    try:
        logger.info(f"Fetching latest alert for device: {device_id}")
        
        # Get latest alert from database
        alert_doc = AlertService.get_latest_active_alert(device_id)
        
        if alert_doc is None:
            logger.info(f"No alerts found for device {device_id}")
            return LatestAlertResponse(
                device_id=device_id,
                has_active_alert=False,
                alert_data=None,
            )
        
        # Map MongoDB document to AlertResponse
        alert_response = AlertResponse(
            alert=alert_doc.get("alert", False),
            level=alert_doc.get("level"),
            type=alert_doc.get("type"),
            message=alert_doc.get("message", ""),
            current_power=alert_doc.get("current_power", 0.0),
            avg_power=alert_doc.get("avg_power", 0.0),
            std_power=alert_doc.get("std_power", 0.0),
            timestamp=alert_doc.get("timestamp", ""),
            threshold_exceeded=alert_doc.get("threshold_exceeded"),
            spike_percentage=alert_doc.get("spike_percentage"),
        )
        
        return LatestAlertResponse(
            device_id=device_id,
            has_active_alert=alert_response.alert,
            alert_data=alert_response,
        )
        
    except Exception as e:
        logger.error(f"Error fetching latest alert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching alert: {str(e)}",
        )


@router.get("/alerts/history", response_model=List[AlertResponse])
async def get_alert_history(
    device_id: str = Query("esp32_01", description="ESP32 device identifier"),
    level: Optional[Literal["warning", "critical"]] = Query(
        None, description="Filter by alert level"
    ),
    hours: int = Query(
        24, description="Number of hours to look back (default: 24)", ge=1, le=720
    ),
    limit: int = Query(10, description="Maximum alerts to retrieve", ge=1, le=100),
) -> List[AlertResponse]:
    """
    Get alert history for a device with optional filters.
    
    Query Parameters:
    - device_id: ESP32 device identifier (default: esp32_01)
    - level: Filter by level - "warning" or "critical" (optional)
    - hours: Number of hours to look back (default: 24, max: 720)
    - limit: Maximum alerts to retrieve (default: 10, max: 100)
    
    Returns:
    List of AlertResponse objects sorted by timestamp (newest first)
    
    Examples:
    GET /api/v1/alerts/history?device_id=esp32_01
    GET /api/v1/alerts/history?device_id=esp32_01&level=critical&hours=48&limit=20
    
    Status Codes:
    - 200: Success
    - 400: Invalid parameters
    - 500: Server error
    """
    try:
        logger.info(
            f"Fetching alert history for device: {device_id}, "
            f"level: {level}, hours: {hours}, limit: {limit}"
        )
        
        alerts = []
        
        if level:
            # Get alerts filtered by level
            alert_docs = AlertService.get_alerts_by_level(device_id, level, limit)
        else:
            # Get recent alerts
            alert_docs = AlertService.get_recent_alerts(device_id, hours, limit)
        
        # Map MongoDB documents to AlertResponse
        for alert_doc in alert_docs:
            alert_response = AlertResponse(
                alert=alert_doc.get("alert", False),
                level=alert_doc.get("level"),
                type=alert_doc.get("type"),
                message=alert_doc.get("message", ""),
                current_power=alert_doc.get("current_power", 0.0),
                avg_power=alert_doc.get("avg_power", 0.0),
                std_power=alert_doc.get("std_power", 0.0),
                timestamp=alert_doc.get("timestamp", ""),
                threshold_exceeded=alert_doc.get("threshold_exceeded"),
                spike_percentage=alert_doc.get("spike_percentage"),
            )
            alerts.append(alert_response)
        
        logger.info(f"Retrieved {len(alerts)} alerts for device {device_id}")
        return alerts
        
    except Exception as e:
        logger.error(f"Error fetching alert history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching alert history: {str(e)}",
        )


@router.get("/alerts/critical", response_model=List[AlertResponse])
async def get_critical_alerts(
    device_id: str = Query("esp32_01", description="ESP32 device identifier"),
    limit: int = Query(10, description="Maximum alerts to retrieve", ge=1, le=100),
) -> List[AlertResponse]:
    """
    Get critical alerts for a device.
    
    Query Parameters:
    - device_id: ESP32 device identifier (default: esp32_01)
    - limit: Maximum critical alerts to retrieve (default: 10, max: 100)
    
    Returns:
    List of critical AlertResponse objects
    
    Status Codes:
    - 200: Success
    - 500: Server error
    """
    try:
        logger.info(f"Fetching critical alerts for device: {device_id}")
        
        # Get critical alerts
        alert_docs = AlertService.get_alerts_by_level(device_id, "critical", limit)
        
        alerts = []
        for alert_doc in alert_docs:
            alert_response = AlertResponse(
                alert=alert_doc.get("alert", False),
                level=alert_doc.get("level"),
                type=alert_doc.get("type"),
                message=alert_doc.get("message", ""),
                current_power=alert_doc.get("current_power", 0.0),
                avg_power=alert_doc.get("avg_power", 0.0),
                std_power=alert_doc.get("std_power", 0.0),
                timestamp=alert_doc.get("timestamp", ""),
                threshold_exceeded=alert_doc.get("threshold_exceeded"),
                spike_percentage=alert_doc.get("spike_percentage"),
            )
            alerts.append(alert_response)
        
        logger.info(f"Retrieved {len(alerts)} critical alerts for device {device_id}")
        return alerts
        
    except Exception as e:
        logger.error(f"Error fetching critical alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching critical alerts: {str(e)}",
        )
