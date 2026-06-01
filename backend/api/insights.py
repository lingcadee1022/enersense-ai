"""
AI insights API endpoints for EnerSense AI.

Generates insights based on:
- latest sensor data
- historical behavior profile
- anomaly detection
- cost estimation
- energy efficiency scoring
"""

import logging

from fastapi import APIRouter, HTTPException, Query, status

from api.models import AiInsightsResponse
from db.mongo import db_client
from services.anomaly_service import detect_anomaly
from services.behavior_service import analyze_energy_logs
from services.cost_service import calculate_cost
from services.insight_service import generate_ai_insights_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Insights"])


@router.get("/insights", response_model=AiInsightsResponse)
async def get_insights(
    device_id: str = Query("esp32_01", description="Device ID"),
) -> AiInsightsResponse:
    """Generate AI insights for a device."""
    try:
        latest_log = db_client.get_latest_energy_log(device_id)
        if latest_log is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No energy data found for device {device_id}",
            )

        current_power = latest_log["power"]
        current_current = latest_log["current"]

        logger.info(
            "Generating insights for %s: Power=%sW, Current=%sA",
            device_id,
            current_power,
            current_current,
        )

        profile = db_client.get_user_profile(device_id)
        if profile is None:
            logs = db_client.get_energy_logs_by_days(device_id, 7)
            if logs:
                profile = analyze_energy_logs(logs)
                if profile:
                    db_client.upsert_user_profile(device_id, profile)

        if not profile:
            profile = {
                "avg_power": current_power,
                "avg_current": current_current,
                "peak_hour": 0,
                "usage_pattern": "normal",
            }

        anomaly_result = detect_anomaly(current_power, current_current)
        cost_estimate = calculate_cost(current_power, 1.0)

        insights_response = generate_ai_insights_response(
            device_id=device_id,
            current_power=current_power,
            current_current=current_current,
            profile=profile,
            anomaly_result=anomaly_result,
            cost_estimate=cost_estimate,
        )

        db_client.insert_insight(device_id, insights_response)

        return AiInsightsResponse(
            energy_score=insights_response["energy_score"],
            estimated_cost_rm=insights_response["estimated_cost_rm"],
            behavior_profile={
                "avg_power": profile.get("avg_power", 0),
                "avg_current": profile.get("avg_current", 0),
                "peak_hour": profile.get("peak_hour", 0),
                "usage_pattern": profile.get("usage_pattern", "normal"),
            },
            insights=insights_response["insights"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error generating insights: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {str(e)}",
        )


@router.post("/insights/train-profile")
async def train_profile(
    device_id: str = Query("esp32_01", description="Device ID"),
    days: int = Query(7, ge=1, le=90, description="Days of history to analyze"),
):
    """Train or update a device behavior profile from historical data."""
    try:
        logs = db_client.get_energy_logs_by_days(device_id, days)
        if not logs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No energy data found for device {device_id}",
            )

        profile = analyze_energy_logs(logs)
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to analyze energy logs",
            )

        db_client.upsert_user_profile(device_id, profile)

        return {
            "success": True,
            "message": f"Profile trained successfully for {device_id}",
            "profile": profile,
            "samples": len(logs),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error training profile: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to train profile: {str(e)}",
        )


@router.get("/insights/profile")
async def get_profile(
    device_id: str = Query("esp32_01", description="Device ID"),
):
    """Get the stored behavior profile for a device."""
    try:
        profile = db_client.get_user_profile(device_id)
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No profile found for device {device_id}",
            )

        profile.pop("_id", None)

        return {
            "success": True,
            "device_id": device_id,
            "profile": profile,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving profile: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve profile: {str(e)}",
        )
