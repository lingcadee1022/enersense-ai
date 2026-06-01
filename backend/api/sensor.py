"""
Sensor data API endpoint for EnerSense AI.

Endpoint: POST /sensor-data

Receives ESP32 sensor data, validates it, and stores in MongoDB.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from db.mongo import db_client
from api.models import SensorDataRequest, SuccessResponse
from services.alert_service import AlertService
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Sensor Data"])


@router.post("/sensor-data", response_model=SuccessResponse)
async def receive_sensor_data(data: SensorDataRequest) -> SuccessResponse:
    """
    Receive and store ESP32 sensor data.
    
    Request body:
    {
        "device_id": "esp32_01",
        "current": 0.8,
        "power": 180
    }
    
    Response:
    {
        "success": true,
        "message": "Sensor data stored successfully",
        "data": {
            "id": "...",
            "timestamp": "2026-05-30T14:23:45Z"
        }
    }
    
    Args:
        data: SensorDataRequest with device_id, current, power
        
    Returns:
        SuccessResponse with inserted document ID and timestamp
        
    Raises:
        HTTPException: If database operation fails
    """
    try:
        previous_log = db_client.get_latest_energy_log(data.device_id)
        previous_power = previous_log.get("power") if previous_log else None

        # Insert energy log (timestamp is auto-generated)
        doc_id = db_client.insert_energy_log(
            device_id=data.device_id,
            voltage=data.voltage,
            current=data.current,
            power=data.power
        )
        alert = AlertService.generate_alert(
            device_id=data.device_id,
            current_power=data.power,
            previous_power=previous_power,
        )
        
        logger.info(
            f"✓ Received sensor data from {data.device_id}: "
            f"Power={data.power}W, Current={data.current}A"
        )
        
        return SuccessResponse(
            success=True,
            message="Sensor data stored successfully",
            data={
                "id": doc_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "alert": alert,
            }
        )
        
    except Exception as e:
        logger.error(f"Error storing sensor data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store sensor data: {str(e)}"
        )


@router.post("/sensor-data/batch")
async def receive_sensor_data_batch(data_list: list[SensorDataRequest]):
    """
    Receive and store multiple sensor readings at once.
    
    Args:
        data_list: List of SensorDataRequest objects
        
    Returns:
        Success response with count of inserted records
    """
    try:
        count = 0
        for data in data_list:
            db_client.insert_energy_log(
                device_id=data.device_id,
                voltage=data.voltage,
                current=data.current,
                power=data.power
            )
            count += 1
        
        logger.info(f"✓ Received {count} sensor readings")
        
        return SuccessResponse(
            success=True,
            message=f"Batch of {count} sensor readings stored successfully",
            data={"count": count}
        )
        
    except Exception as e:
        logger.error(f"Error storing batch sensor data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store batch data: {str(e)}"
        )
