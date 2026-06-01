"""
Real-time energy alert service for EnerSense AI.

Generates alerts when energy consumption becomes abnormal.
Logic:
- HIGH_USAGE: power > avg_power + 2 * std_power
- CRITICAL_USAGE: power > avg_power + 3 * std_power
- SUDDEN_SPIKE: latest_power > previous_power * 1.5
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
from db.mongo import db_client

logger = logging.getLogger(__name__)


class AlertService:
    """Service for generating and managing energy alerts."""

    # Alert thresholds (multiplier of standard deviation)
    HIGH_USAGE_THRESHOLD = 2.0
    CRITICAL_USAGE_THRESHOLD = 3.0
    SUDDEN_SPIKE_MULTIPLIER = 1.5

    # Minimum data points for calculating statistics
    MIN_DATA_POINTS = 5

    @staticmethod
    def calculate_statistics(
        power_readings: List[float],
    ) -> Dict[str, float]:
        """
        Calculate average power and standard deviation.

        Args:
            power_readings: List of power consumption values in Watts

        Returns:
            Dictionary with avg_power and std_power
        """
        if not power_readings or len(power_readings) < AlertService.MIN_DATA_POINTS:
            logger.warning("Insufficient data points for statistics calculation")
            return {"avg_power": 0.0, "std_power": 0.0}

        avg_power = float(np.mean(power_readings))
        std_power = float(np.std(power_readings))

        logger.debug(
            f"Statistics: avg={avg_power:.2f}W, std={std_power:.2f}W"
        )

        return {
            "avg_power": round(avg_power, 2),
            "std_power": round(std_power, 2),
        }

    @staticmethod
    def check_alert_conditions(
        current_power: float,
        previous_power: Optional[float],
        avg_power: float,
        std_power: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Check for alert conditions.

        Args:
            current_power: Latest power reading in Watts
            previous_power: Previous power reading in Watts (optional)
            avg_power: Average power consumption
            std_power: Standard deviation of power

        Returns:
            Alert dictionary or None if no alert triggered
        """
        alert = None

        # Check CRITICAL_USAGE (highest priority)
        critical_threshold = (
            avg_power + AlertService.CRITICAL_USAGE_THRESHOLD * std_power
        )
        if current_power > critical_threshold:
            alert = {
                "level": "critical",
                "type": "CRITICAL_USAGE",
                "message": (
                    f"CRITICAL: Energy consumption is {current_power:.0f}W, "
                    f"exceeding threshold of {critical_threshold:.0f}W"
                ),
                "threshold_exceeded": round(current_power - critical_threshold, 2),
            }
            logger.warning(f"Critical alert triggered: {alert['message']}")
            return alert

        # Check HIGH_USAGE
        high_threshold = avg_power + AlertService.HIGH_USAGE_THRESHOLD * std_power
        if current_power > high_threshold:
            alert = {
                "level": "warning",
                "type": "HIGH_USAGE",
                "message": (
                    f"WARNING: Energy consumption is {current_power:.0f}W, "
                    f"exceeding threshold of {high_threshold:.0f}W"
                ),
                "threshold_exceeded": round(current_power - high_threshold, 2),
            }
            logger.warning(f"High usage alert triggered: {alert['message']}")
            return alert

        # Check SUDDEN_SPIKE
        if previous_power is not None and previous_power > 0:
            spike_threshold = previous_power * AlertService.SUDDEN_SPIKE_MULTIPLIER
            if current_power > spike_threshold:
                alert = {
                    "level": "warning",
                    "type": "SUDDEN_SPIKE",
                    "message": (
                        f"WARNING: Sudden power spike detected. "
                        f"Power increased from {previous_power:.0f}W to {current_power:.0f}W "
                        f"({((current_power / previous_power - 1) * 100):.0f}% increase)"
                    ),
                    "spike_percentage": round(
                        (current_power / previous_power - 1) * 100, 1
                    ),
                }
                logger.warning(f"Spike alert triggered: {alert['message']}")
                return alert

        logger.debug("No alert conditions triggered")
        return None

    @staticmethod
    def generate_alert(
        device_id: str,
        current_power: float,
        previous_power: Optional[float] = None,
        hours_window: int = 24,
    ) -> Dict[str, Any]:
        """
        Generate alert based on current energy reading.

        Steps:
        1. Get latest sensor reading
        2. Calculate average power and standard deviation
        3. Check alert conditions
        4. Return alert data and store in MongoDB

        Args:
            device_id: ESP32 device identifier
            current_power: Latest power reading in Watts
            previous_power: Previous power reading (optional, for spike detection)
            hours_window: Hours of historical data to analyze (default: 24)

        Returns:
            Dictionary with alert data:
            {
                "alert": bool,
                "level": "warning" | "critical" | None,
                "type": "HIGH_USAGE" | "CRITICAL_USAGE" | "SUDDEN_SPIKE" | None,
                "message": str,
                "current_power": float,
                "avg_power": float,
                "std_power": float,
                "timestamp": str
            }
        """
        try:
            # Get historical logs for statistics
            logs = db_client.get_energy_logs_by_hours(device_id, hours_window)

            if not logs:
                logger.warning(f"No historical data for device {device_id}")
                return {
                    "alert": False,
                    "level": None,
                    "type": None,
                    "message": "Insufficient historical data for alert generation",
                    "current_power": round(current_power, 2),
                    "avg_power": 0.0,
                    "std_power": 0.0,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }

            # Extract power readings
            power_readings = [log.get("power", 0) for log in logs]

            # Calculate statistics
            stats = AlertService.calculate_statistics(power_readings)
            avg_power = stats["avg_power"]
            std_power = stats["std_power"]

            # Check for alert conditions
            alert_data = AlertService.check_alert_conditions(
                current_power, previous_power, avg_power, std_power
            )

            # Build response
            if alert_data:
                response = {
                    "alert": True,
                    "level": alert_data["level"],
                    "type": alert_data["type"],
                    "message": alert_data["message"],
                    "current_power": round(current_power, 2),
                    "avg_power": avg_power,
                    "std_power": std_power,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }

                # Store alert in MongoDB
                db_client.insert_alert(device_id, response)

                return response
            else:
                return {
                    "alert": False,
                    "level": None,
                    "type": None,
                    "message": "Energy consumption within normal range",
                    "current_power": round(current_power, 2),
                    "avg_power": avg_power,
                    "std_power": std_power,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }

        except Exception as e:
            logger.error(f"Error generating alert: {str(e)}")
            return {
                "alert": False,
                "level": None,
                "type": None,
                "message": f"Error generating alert: {str(e)}",
                "current_power": round(current_power, 2),
                "avg_power": 0.0,
                "std_power": 0.0,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

    @staticmethod
    def get_latest_active_alert(device_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the latest active alert for a device.

        Args:
            device_id: ESP32 device identifier

        Returns:
            Latest alert document or None
        """
        try:
            alert = db_client.get_latest_alert(device_id)
            if alert:
                logger.info(f"Retrieved latest alert for {device_id}")
            else:
                logger.info(f"No alerts found for {device_id}")
            return alert
        except Exception as e:
            logger.error(f"Error retrieving latest alert: {str(e)}")
            return None

    @staticmethod
    def get_alerts_by_level(
        device_id: str, level: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve alerts by alert level.

        Args:
            device_id: ESP32 device identifier
            level: Alert level ("warning" or "critical")
            limit: Maximum number of alerts to retrieve

        Returns:
            List of alert documents
        """
        try:
            alerts = db_client.get_alerts_by_level(device_id, level, limit)
            logger.info(f"Retrieved {len(alerts)} {level} alerts for {device_id}")
            return alerts
        except Exception as e:
            logger.error(f"Error retrieving alerts by level: {str(e)}")
            return []

    @staticmethod
    def get_recent_alerts(
        device_id: str, hours: int = 24, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent alerts within specified time window.

        Args:
            device_id: ESP32 device identifier
            hours: Number of hours to look back
            limit: Maximum number of alerts to retrieve

        Returns:
            List of alert documents
        """
        try:
            alerts = db_client.get_recent_alerts(device_id, hours, limit)
            logger.info(f"Retrieved {len(alerts)} recent alerts for {device_id}")
            return alerts
        except Exception as e:
            logger.error(f"Error retrieving recent alerts: {str(e)}")
            return []
