"""
Energy Forecasting Module
Predicts future energy consumption and cost
"""

from typing import List, Dict, Any
from collections import deque
import numpy as np


class EnergyForecaster:
    """Forecasts future energy consumption"""
    
    COST_PER_KWH = 0.45  # RM per kWh
    
    def __init__(self, history_window: int = 48):
        self.history_window = history_window
        self.power_history = deque(maxlen=history_window)
        self.hourly_averages = {}
    
    def add_reading(self, power: float, hour_of_day: int = None):
        """Add power reading to history"""
        self.power_history.append(power)
        
        if hour_of_day is not None:
            if hour_of_day not in self.hourly_averages:
                self.hourly_averages[hour_of_day] = []
            self.hourly_averages[hour_of_day].append(power)
    
    def forecast_hourly(self) -> Dict[int, float]:
        """Forecast next 24 hours of power consumption"""
        forecast = {}
        
        if len(self.power_history) == 0:
            # Return default forecast
            return {i: 500.0 for i in range(24)}
        
        # Use moving average for simple forecasting
        if len(self.hourly_averages) > 0:
            for hour in range(24):
                if hour in self.hourly_averages:
                    avg = np.mean(self.hourly_averages[hour])
                    forecast[hour] = float(avg)
                else:
                    forecast[hour] = float(np.mean(list(self.power_history)))
        else:
            # Fallback: use average of all readings
            avg = np.mean(list(self.power_history))
            for hour in range(24):
                forecast[hour] = float(avg)
        
        return forecast
    
    def forecast_daily(self, days: int = 7) -> List[Dict[str, Any]]:
        """Forecast next N days of consumption"""
        forecasts = []
        
        if len(self.power_history) == 0:
            daily_kwh = 10.0  # Default
        else:
            # Calculate average daily kWh
            avg_power = np.mean(list(self.power_history))
            daily_kwh = (avg_power * 24) / 1000
        
        for day in range(days):
            daily_cost = daily_kwh * self.COST_PER_KWH
            forecasts.append({
                'day': day + 1,
                'estimated_kwh': float(daily_kwh),
                'estimated_cost': float(daily_cost),
                'power_trend': 'stable'  # Can be enhanced with trend analysis
            })
        
        return forecasts
    
    def forecast_monthly(self) -> Dict[str, Any]:
        """Forecast monthly consumption and cost"""
        if len(self.power_history) == 0:
            daily_kwh = 10.0
            monthly_cost = 135.0  # ~300 kWh * 0.45
        else:
            avg_power = np.mean(list(self.power_history))
            daily_kwh = (avg_power * 24) / 1000
            monthly_kwh = daily_kwh * 30
            monthly_cost = monthly_kwh * self.COST_PER_KWH
        
        return {
            'estimated_daily_kwh': float(daily_kwh),
            'estimated_monthly_kwh': float(daily_kwh * 30),
            'estimated_monthly_cost': float(monthly_cost),
            'currency': 'RM',
            'cost_per_kwh': self.COST_PER_KWH
        }
    
    def get_consumption_trend(self) -> str:
        """Determine consumption trend"""
        if len(self.power_history) < 2:
            return 'insufficient_data'
        
        recent = list(self.power_history)[-10:]
        older = list(self.power_history)[:10]
        
        recent_avg = np.mean(recent) if len(recent) > 0 else 0
        older_avg = np.mean(older) if len(older) > 0 else 0
        
        if older_avg == 0:
            return 'stable'
        
        change = (recent_avg - older_avg) / older_avg
        
        if change > 0.15:
            return 'increasing'
        elif change < -0.15:
            return 'decreasing'
        else:
            return 'stable'
    
    def get_peak_hours(self) -> List[int]:
        """Identify peak usage hours"""
        if not self.hourly_averages:
            return [18, 19, 20, 21]  # Default peak hours
        
        # Find hours with highest average consumption
        sorted_hours = sorted(
            self.hourly_averages.items(),
            key=lambda x: np.mean(x[1]),
            reverse=True
        )
        
        return [hour for hour, _ in sorted_hours[:4]]
    
    def get_low_usage_hours(self) -> List[int]:
        """Identify low usage hours (best time to use major appliances)"""
        if not self.hourly_averages:
            return [2, 3, 4, 5]  # Default low hours
        
        # Find hours with lowest average consumption
        sorted_hours = sorted(
            self.hourly_averages.items(),
            key=lambda x: np.mean(x[1])
        )
        
        return [hour for hour, _ in sorted_hours[:4]]


# Global forecaster instance
forecaster = EnergyForecaster()


def add_reading(power: float, hour: int = None):
    """Helper to add reading"""
    forecaster.add_reading(power, hour)


def forecast_hourly() -> Dict[int, float]:
    """Helper to forecast hourly"""
    return forecaster.forecast_hourly()


def forecast_daily(days: int = 7) -> List[Dict[str, Any]]:
    """Helper to forecast daily"""
    return forecaster.forecast_daily(days)


def forecast_monthly() -> Dict[str, Any]:
    """Helper to forecast monthly"""
    return forecaster.forecast_monthly()


def get_consumption_trend() -> str:
    """Helper to get trend"""
    return forecaster.get_consumption_trend()


def get_peak_hours() -> List[int]:
    """Helper to get peak hours"""
    return forecaster.get_peak_hours()
