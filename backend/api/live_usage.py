"""
Live usage API endpoint for EnerSense AI.

Endpoint: GET /live-usage

Returns the latest sensor reading for a device.
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query
from db.mongo import db_client
from api.models import SensorDataResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Usage Data"])


@router.get("/live-usage", response_model=SensorDataResponse)
async def get_live_usage(device_id: str = Query("esp32_01", description="Device ID")) -> SensorDataResponse:
    """
    Get the latest sensor reading (live usage) for a device.
    
    Query parameters:
    - device_id: ESP32 device identifier (default: esp32_01)
    
    Response:
    {
        "device_id": "esp32_01",
        "current": 0.8,
        "power": 180,
        "timestamp": "2026-05-30T14:23:45Z"
    }
    
    Args:
        device_id: Device identifier
        
    Returns:
        Latest sensor reading
        
    Raises:
        HTTPException 404: If no data found for device
        HTTPException 500: If database operation fails
    """
    try:
        # Get latest energy log for device
        log = db_client.get_latest_energy_log(device_id)
        
        if log is None:
            logger.warning(f"No energy logs found for device: {device_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No energy data found for device {device_id}"
            )
        
        logger.info(f"✓ Retrieved live usage for {device_id}")
        
        return SensorDataResponse(
            device_id=log["device_id"],
            voltage=log.get("voltage", 240.0),
            current=log["current"],
            power=log["power"],
            timestamp=log["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving live usage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve live usage: {str(e)}"
        )
