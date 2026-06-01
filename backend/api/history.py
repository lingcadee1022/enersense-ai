"""
History API endpoint for EnerSense AI.

Endpoint: GET /history

Returns historical energy logs for charting and analysis.
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from db.mongo import db_client
from api.models import EnergyLogResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["History"])


@router.get("/history", response_model=List[EnergyLogResponse])
async def get_energy_history(
    device_id: str = Query("esp32_01", description="Device ID"),
    hours: Optional[int] = Query(None, ge=1, le=720, description="Past hours to retrieve (1-720)"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Past days to retrieve (1-365)")
) -> List[EnergyLogResponse]:
    """
    Get historical energy logs for a device.
    
    Query parameters:
    - device_id: ESP32 device identifier (default: esp32_01)
    - hours: Get logs from past N hours (optional)
    - days: Get logs from past N days (optional)
    
    At least one of hours or days must be specified.
    
    Response: Array of energy logs sorted by timestamp (ascending)
    [
        {
            "timestamp": "2026-05-30T10:00:00Z",
            "current": 0.65,
            "power": 150
        },
        {
            "timestamp": "2026-05-30T11:00:00Z",
            "current": 0.78,
            "power": 180
        }
    ]
    
    Args:
        device_id: Device identifier
        hours: Number of past hours to retrieve
        days: Number of past days to retrieve
        
    Returns:
        List of energy log records sorted by timestamp (ascending)
        
    Raises:
        HTTPException 400: If neither hours nor days specified
        HTTPException 404: If no data found
        HTTPException 500: If database operation fails
    """
    try:
        # Validate parameters
        if hours is None and days is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either 'hours' or 'days' parameter must be specified"
            )
        
        # Retrieve logs
        if hours is not None:
            logs = db_client.get_energy_logs_by_hours(device_id, hours)
            logger.info(f"✓ Retrieved {len(logs)} logs for {device_id} from past {hours} hours")
        else:
            logs = db_client.get_energy_logs_by_days(device_id, days)
            logger.info(f"✓ Retrieved {len(logs)} logs for {device_id} from past {days} days")
        
        if not logs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No energy history found for device {device_id}"
            )
        
        # Convert to response models
        response = [
            EnergyLogResponse(
                timestamp=log["timestamp"],
                current=log["current"],
                power=log["power"]
            )
            for log in logs
        ]
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )


@router.get("/history/summary")
async def get_history_summary(
    device_id: str = Query("esp32_01", description="Device ID"),
    hours: Optional[int] = Query(None, ge=1, description="Past hours"),
    days: Optional[int] = Query(None, ge=1, description="Past days")
):
    """
    Get summary statistics of historical data.
    
    Returns min, max, average, and stddev of power and current.
    """
    try:
        if hours is None and days is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either 'hours' or 'days' parameter must be specified"
            )
        
        # Retrieve logs
        if hours is not None:
            logs = db_client.get_energy_logs_by_hours(device_id, hours)
        else:
            logs = db_client.get_energy_logs_by_days(device_id, days)
        
        if not logs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No energy history found for device {device_id}"
            )
        
        # Calculate statistics
        powers = [log["power"] for log in logs]
        currents = [log["current"] for log in logs]
        
        import statistics
        
        summary = {
            "count": len(logs),
            "power": {
                "min": min(powers),
                "max": max(powers),
                "avg": sum(powers) / len(powers),
                "stdev": statistics.stdev(powers) if len(powers) > 1 else 0,
            },
            "current": {
                "min": min(currents),
                "max": max(currents),
                "avg": sum(currents) / len(currents),
                "stdev": statistics.stdev(currents) if len(currents) > 1 else 0,
            },
            "period": f"{hours if hours else days} {'hours' if hours else 'days'}"
        }
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate summary: {str(e)}"
        )
