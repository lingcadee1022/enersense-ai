"""
Behavior learning service for EnerSense AI.

Analyzes historical energy data to learn user consumption patterns.
Generates user profiles with usage statistics and pattern classification.
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


def analyze_energy_logs(logs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Analyze historical energy logs to generate behavior profile.
    
    Calculates:
    - Average power consumption
    - Average current
    - Peak usage hour
    - Usage pattern classification (low/normal/high)
    
    Args:
        logs: List of energy log documents from MongoDB
        
    Returns:
        Dictionary with behavior profile or None if insufficient data
        
    Example:
        >>> logs = [
        ...     {"power": 150, "current": 0.65, "timestamp": "2026-05-30T10:00:00Z"},
        ...     {"power": 180, "current": 0.78, "timestamp": "2026-05-30T11:00:00Z"},
        ... ]
        >>> analyze_energy_logs(logs)
        {
            'avg_power': 165.0,
            'avg_current': 0.715,
            'peak_hour': 11,
            'usage_pattern': 'normal'
        }
    """
    if not logs or len(logs) == 0:
        logger.warning("No energy logs provided for analysis")
        return None
    
    try:
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(logs)
        
        # Calculate averages
        avg_power = df["power"].mean()
        avg_current = df["current"].mean()
        
        # Extract hour from timestamp and find peak usage hour
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        peak_hour = df.groupby("hour")["power"].mean().idxmax()
        
        # Classify usage pattern based on average power
        # Low: < 100W, Normal: 100-300W, High: > 300W
        if avg_power < 100:
            usage_pattern = "low"
        elif avg_power < 300:
            usage_pattern = "normal"
        else:
            usage_pattern = "high"
        
        profile = {
            "avg_power": round(avg_power, 2),
            "avg_current": round(avg_current, 2),
            "peak_hour": int(peak_hour),
            "usage_pattern": usage_pattern,
        }
        
        logger.info(f"Generated behavior profile: {profile}")
        return profile
        
    except Exception as e:
        logger.error(f"Error analyzing energy logs: {str(e)}")
        return None


def get_usage_statistics(logs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Extract detailed usage statistics from energy logs.
    
    Args:
        logs: List of energy log documents from MongoDB
        
    Returns:
        Dictionary with detailed statistics
    """
    if not logs or len(logs) == 0:
        return None
    
    try:
        df = pd.DataFrame(logs)
        
        return {
            "total_logs": len(df),
            "avg_power_w": round(df["power"].mean(), 2),
            "max_power_w": round(df["power"].max(), 2),
            "min_power_w": round(df["power"].min(), 2),
            "std_power_w": round(df["power"].std(), 2),
            "avg_current_a": round(df["current"].mean(), 2),
            "max_current_a": round(df["current"].max(), 2),
            "min_current_a": round(df["current"].min(), 2),
        }
    except Exception as e:
        logger.error(f"Error extracting usage statistics: {str(e)}")
        return None


def classify_current_usage(
    current_power: float,
    profile: Optional[Dict[str, Any]] = None
) -> str:
    """
    Classify current power usage against profile.
    
    Args:
        current_power: Current power reading in Watts
        profile: User behavior profile (optional)
        
    Returns:
        Classification: "low", "normal", or "high"
    """
    if profile is None:
        # Use absolute thresholds if no profile
        if current_power < 100:
            return "low"
        elif current_power < 300:
            return "normal"
        else:
            return "high"
    
    # Compare against profile average
    avg_power = profile.get("avg_power", 150)
    
    if current_power < avg_power * 0.7:
        return "low"
    elif current_power < avg_power * 1.3:
        return "normal"
    else:
        return "high"


def get_hourly_average(logs: List[Dict[str, Any]]) -> Optional[Dict[int, float]]:
    """
    Get average power consumption by hour of day.
    
    Args:
        logs: List of energy log documents
        
    Returns:
        Dictionary mapping hour (0-23) to average power
    """
    if not logs or len(logs) == 0:
        return None
    
    try:
        df = pd.DataFrame(logs)
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        
        hourly_avg = df.groupby("hour")["power"].mean()
        return {int(hour): round(power, 2) for hour, power in hourly_avg.items()}
    except Exception as e:
        logger.error(f"Error calculating hourly average: {str(e)}")
        return None


def get_daily_average(logs: List[Dict[str, Any]]) -> Optional[Dict[str, float]]:
    """
    Get average power consumption by day.
    
    Args:
        logs: List of energy log documents
        
    Returns:
        Dictionary mapping date (YYYY-MM-DD) to average power
    """
    if not logs or len(logs) == 0:
        return None
    
    try:
        df = pd.DataFrame(logs)
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        
        daily_avg = df.groupby("date")["power"].mean()
        return {str(date): round(power, 2) for date, power in daily_avg.items()}
    except Exception as e:
        logger.error(f"Error calculating daily average: {str(e)}")
        return None
