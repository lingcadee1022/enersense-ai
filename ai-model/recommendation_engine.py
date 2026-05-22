"""
Recommendation Engine
Generates AI-powered energy-saving recommendations
"""

from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict


class RecommendationEngine:
    """Generates personalized energy-saving recommendations"""
    
    # Energy cost (in RM per kWh)
    COST_PER_KWH = 0.45
    
    # Appliance efficiency ratings (power reduction possible)
    APPLIANCE_EFFICIENCY = {
        'Air Conditioner': {'reduction': 0.20, 'savings': 'Use eco mode'},
        'Oven': {'reduction': 0.15, 'savings': 'Preheat less'},
        'Television': {'reduction': 0.30, 'savings': 'Turn off when not in use'},
        'Washing Machine': {'reduction': 0.25, 'savings': 'Use cold water cycle'},
        'Lighting': {'reduction': 0.40, 'savings': 'Switch to LED bulbs'},
        'Refrigerator': {'reduction': 0.10, 'savings': 'Keep door closed'},
    }
    
    # Time-based recommendations
    PEAK_HOURS = {'start': 18, 'end': 22}  # 6PM to 10PM
    
    def __init__(self):
        self.appliance_usage = defaultdict(list)
        self.total_power_consumed = 0.0
        self.readings_count = 0
    
    def add_reading(self, power: float, appliance: str):
        """Track appliance usage"""
        self.appliance_usage[appliance].append(power)
        self.total_power_consumed += power
        self.readings_count += 1
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Rule 1: High AC usage during peak hours
        if 'Air Conditioner' in self.appliance_usage:
            ac_power = sum(self.appliance_usage['Air Conditioner']) / len(self.appliance_usage['Air Conditioner'])
            if ac_power > 1500:
                recommendations.append({
                    'type': 'high_usage',
                    'appliance': 'Air Conditioner',
                    'recommendation': 'AC usage is high. Consider using eco mode or adjusting temperature by 2°C.',
                    'potential_savings': f'RM {self._calculate_savings(ac_power, 0.20):.2f}/month'
                })
        
        # Rule 2: Unused TV running
        if 'Television' in self.appliance_usage:
            recommendations.append({
                'type': 'idle_device',
                'appliance': 'Television',
                'recommendation': 'Turn off TV when not actively watching.',
                'potential_savings': f'RM {self._calculate_savings(800, 0.30):.2f}/month'
            })
        
        # Rule 3: Lighting during daytime
        if 'Lighting' in self.appliance_usage:
            recommendations.append({
                'type': 'efficiency',
                'appliance': 'Lighting',
                'recommendation': 'Consider switching to LED bulbs to reduce energy consumption.',
                'potential_savings': f'RM {self._calculate_savings(100, 0.40):.2f}/month'
            })
        
        # Rule 4: Peak hours usage
        if self.total_power_consumed > 5000:
            recommendations.append({
                'type': 'peak_hours',
                'recommendation': f'Reduce usage during peak hours (6PM - 10PM) to save up to RM 15/month.',
                'potential_savings': 'RM 15/month'
            })
        
        # Rule 5: Overall cost estimate
        monthly_kwh = (self.total_power_consumed * self.readings_count) / 1000000
        if self.readings_count > 0:
            monthly_kwh = (self.total_power_consumed / self.readings_count) * 24 * 30 / 1000
            recommendations.append({
                'type': 'cost_estimate',
                'recommendation': f'Current usage pattern: ~RM {monthly_kwh * self.COST_PER_KWH:.2f}/month',
                'potential_savings': 'Monitor usage'
            })
        
        return recommendations
    
    def get_appliance_insights(self) -> List[Dict[str, Any]]:
        """Get insights for each appliance"""
        insights = []
        
        for appliance, readings in self.appliance_usage.items():
            if not readings:
                continue
            
            avg_power = sum(readings) / len(readings)
            insights.append({
                'appliance': appliance,
                'avg_power': float(avg_power),
                'readings': len(readings),
                'total_consumption': float(sum(readings))
            })
        
        return sorted(insights, key=lambda x: x['total_consumption'], reverse=True)
    
    def _calculate_savings(self, power: float, efficiency_rate: float) -> float:
        """Calculate potential monthly savings in RM"""
        # Assume average daily usage of 6 hours
        daily_kwh = (power * 6) / 1000
        monthly_kwh = daily_kwh * 30
        savings = monthly_kwh * efficiency_rate * self.COST_PER_KWH
        return savings
    
    def get_daily_summary(self) -> Dict[str, Any]:
        """Get summary of the day"""
        if self.readings_count == 0:
            return {'total_readings': 0, 'total_power': 0, 'recommendations_count': 0}
        
        avg_power = self.total_power_consumed / self.readings_count
        recommendations = self.generate_recommendations()
        
        return {
            'total_readings': self.readings_count,
            'total_power': float(self.total_power_consumed),
            'average_power': float(avg_power),
            'recommendations_count': len(recommendations),
            'top_recommendations': recommendations[:3]
        }


# Global recommendation engine
engine = RecommendationEngine()


def add_reading(power: float, appliance: str):
    """Helper to add reading"""
    engine.add_reading(power, appliance)


def get_recommendations() -> List[Dict[str, Any]]:
    """Helper to get recommendations"""
    return engine.generate_recommendations()


def get_appliance_insights() -> List[Dict[str, Any]]:
    """Helper to get appliance insights"""
    return engine.get_appliance_insights()


def get_daily_summary() -> Dict[str, Any]:
    """Helper to get daily summary"""
    return engine.get_daily_summary()
