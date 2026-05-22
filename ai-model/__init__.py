"""
EnerSense AI/ML Module
Complete AI/ML pipeline for energy analysis and recommendations
"""

__version__ = "1.0.0"
__author__ = "EnerSense Team"

from appliance_classifier import predict_appliance, get_energy_score
from anomaly_detection import analyze_reading, detect_anomaly
from recommendation_engine import get_recommendations, get_appliance_insights, get_daily_summary
from forecasting import forecast_monthly, forecast_daily, get_peak_hours

__all__ = [
    'predict_appliance',
    'get_energy_score',
    'analyze_reading',
    'detect_anomaly',
    'get_recommendations',
    'get_appliance_insights',
    'get_daily_summary',
    'forecast_monthly',
    'forecast_daily',
    'get_peak_hours',
]
