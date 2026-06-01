"""
Cost calculation service for EnerSense AI.

Calculates energy consumption and estimated costs based on power readings.
Uses Malaysian electricity tariff (RM0.571 per kWh).
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Malaysian electricity tariff (RM per kWh)
DEFAULT_TARIFF_RM_PER_KWH = 0.571


def calculate_cost(
    power_watts: float,
    duration_hours: float,
    tariff: float = DEFAULT_TARIFF_RM_PER_KWH
) -> Dict[str, float]:
    """
    Calculate energy consumption and estimated cost.
    
    Formula:
    kWh = power (W) / 1000 × duration_hours
    cost = kWh × tariff_per_kwh
    
    Args:
        power_watts: Power consumption in Watts
        duration_hours: Duration in hours
        tariff: Electricity tariff in RM per kWh (default: 0.571)
        
    Returns:
        Dictionary with energy_kwh and estimated_cost_rm
        
    Example:
        >>> calculate_cost(180, 24)
        {'energy_kwh': 4.32, 'estimated_cost_rm': 2.46672}
    """
    # Convert watts to kilowatts and calculate energy consumption
    energy_kwh = (power_watts / 1000.0) * duration_hours
    
    # Calculate estimated cost
    estimated_cost_rm = energy_kwh * tariff
    
    logger.info(
        f"Cost calculation: {power_watts}W × {duration_hours}h = "
        f"{energy_kwh:.2f}kWh = RM{estimated_cost_rm:.4f}"
    )
    
    return {
        "energy_kwh": round(energy_kwh, 4),
        "estimated_cost_rm": round(estimated_cost_rm, 4)
    }


def estimate_monthly_cost(
    avg_power_watts: float,
    tariff: float = DEFAULT_TARIFF_RM_PER_KWH
) -> float:
    """
    Estimate monthly cost based on average power consumption.
    
    Args:
        avg_power_watts: Average power consumption in Watts
        tariff: Electricity tariff in RM per kWh (default: 0.571)
        
    Returns:
        Estimated monthly cost in RM
        
    Example:
        >>> estimate_monthly_cost(150)
        65.412
    """
    # Assume 24 hours × 30 days per month
    hours_per_month = 24 * 30
    result = calculate_cost(avg_power_watts, hours_per_month, tariff)
    return result["estimated_cost_rm"]


def estimate_annual_cost(
    avg_power_watts: float,
    tariff: float = DEFAULT_TARIFF_RM_PER_KWH
) -> float:
    """
    Estimate annual cost based on average power consumption.
    
    Args:
        avg_power_watts: Average power consumption in Watts
        tariff: Electricity tariff in RM per kWh (default: 0.571)
        
    Returns:
        Estimated annual cost in RM
        
    Example:
        >>> estimate_annual_cost(150)
        784.944
    """
    # Assume 24 hours × 365 days per year
    hours_per_year = 24 * 365
    result = calculate_cost(avg_power_watts, hours_per_year, tariff)
    return result["estimated_cost_rm"]
