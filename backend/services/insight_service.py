"""
AI insight generation service for EnerSense AI.

Generates human-readable insights and recommendations based on:
- Latest sensor data
- Anomaly detection results
- User behavior profile
- Cost estimation
- Energy efficiency score
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def calculate_energy_score(
    current_usage: float,
    profile: Optional[Dict[str, Any]] = None
) -> int:
    """
    Calculate energy efficiency score (0-100).
    
    Args:
        current_usage: Current power consumption in Watts
        profile: User behavior profile
        
    Returns:
        Energy score (0-100)
        
    Logic:
    - 100: Usage 20% below average
    - 75: Usage within normal range (avg ± 20%)
    - 50: Usage 20-50% above average
    - 25: Usage 50-100% above average
    - 0: Usage 100%+ above average
    """
    if profile is None or "avg_power" not in profile:
        # Default scoring without profile
        if current_usage < 100:
            return 100
        elif current_usage < 200:
            return 75
        elif current_usage < 400:
            return 50
        else:
            return 25

    avg_power = profile.get("avg_power", 150)
    threshold_20_below = avg_power * 0.8
    threshold_normal_min = avg_power * 0.8
    threshold_normal_max = avg_power * 1.2
    threshold_moderate = avg_power * 1.5
    threshold_high = avg_power * 2.0

    if current_usage <= threshold_20_below:
        return 100
    elif current_usage <= threshold_normal_max:
        return 75
    elif current_usage <= threshold_moderate:
        return 50
    elif current_usage <= threshold_high:
        return 25
    else:
        return 0


def generate_insights(
    current_power: float,
    current_current: float,
    profile: Optional[Dict[str, Any]] = None,
    anomaly_result: Optional[Dict[str, Any]] = None,
    cost_estimate: Optional[Dict[str, float]] = None,
) -> List[str]:
    """
    Generate human-readable insights based on current data and profile.
    
    Args:
        current_power: Current power reading in Watts
        current_current: Current current reading in Amperes
        profile: User behavior profile
        anomaly_result: Anomaly detection result
        cost_estimate: Cost estimation result
        
    Returns:
        List of insight strings
        
    Example:
        >>> insights = generate_insights(
        ...     current_power=180,
        ...     current_current=0.78,
        ...     profile={
        ...         "avg_power": 150,
        ...         "peak_hour": 19,
        ...         "usage_pattern": "normal"
        ...     },
        ...     cost_estimate={"energy_kwh": 4.32, "estimated_cost_rm": 2.46}
        ... )
        >>> print(insights[0])
        'Your current power consumption is 180W, which is 20% higher than your average.'
    """
    insights = []

    # Current usage insight
    if profile and "avg_power" in profile:
        avg_power = profile["avg_power"]
        diff_percent = ((current_power - avg_power) / avg_power * 100) if avg_power != 0 else 0
        
        if diff_percent < -20:
            insights.append(
                f"💡 Your power consumption is {abs(diff_percent):.0f}% lower than your average. Good job!"
            )
        elif diff_percent > 20:
            insights.append(
                f"⚡ Your current power consumption ({current_power}W) is {diff_percent:.0f}% "
                f"higher than your average ({avg_power}W)."
            )
        else:
            insights.append(
                f"✓ Your current power consumption ({current_power}W) is within normal range."
            )
    else:
        insights.append(f"📊 Current power consumption: {current_power}W, Current: {current_current}A")

    # Anomaly insight
    if anomaly_result and anomaly_result.get("is_anomaly"):
        insights.append(
            f"⚠️ {anomaly_result.get('message', 'Anomaly detected in energy usage.')}"
        )
    elif anomaly_result:
        insights.append("✓ Energy consumption pattern is normal.")

    # Peak hour insight
    if profile and "peak_hour" in profile:
        peak_hour = profile["peak_hour"]
        insights.append(
            f"📈 Your peak usage hour is {peak_hour}:00 ({peak_hour}:00). "
            f"Consider shifting high-consumption tasks to off-peak hours."
        )

    # Usage pattern insight
    if profile and "usage_pattern" in profile:
        pattern = profile["usage_pattern"]
        if pattern == "low":
            insights.append("✓ Your usage pattern is low. You are energy efficient!")
        elif pattern == "normal":
            insights.append("ℹ️ Your usage pattern is normal for your device.")
        elif pattern == "high":
            insights.append(
                "⚠️ Your usage pattern is high. Consider implementing energy-saving measures."
            )

    # Cost insights
    if cost_estimate:
        monthly_cost = cost_estimate.get("estimated_cost_rm", 0) * 720  # Approximate monthly
        annual_cost = monthly_cost * 12
        
        if current_power > 300:
            potential_savings = (current_power - 200) / current_power * monthly_cost
            insights.append(
                f"💰 You could save approximately RM{potential_savings:.2f}/month "
                f"by reducing high-usage periods."
            )
        
        insights.append(
            f"💸 Estimated cost: RM{cost_estimate.get('estimated_cost_rm', 0):.4f}/hour "
            f"(RM{monthly_cost:.2f}/month, RM{annual_cost:.2f}/year based on current usage)"
        )

    # Energy efficiency recommendations
    if current_power > 400:
        insights.append(
            "🔧 High power consumption detected. Check for connected appliances "
            "and consider unplugging unused devices."
        )
    elif current_power < 50:
        insights.append(
            "✓ Very low power consumption. Device may be in standby or sleep mode."
        )

    return insights


def generate_ai_insights_response(
    device_id: str,
    current_power: float,
    current_current: float,
    profile: Optional[Dict[str, Any]] = None,
    anomaly_result: Optional[Dict[str, Any]] = None,
    cost_estimate: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Generate complete AI insights response.
    
    Args:
        device_id: Device identifier
        current_power: Current power reading
        current_current: Current current reading
        profile: User behavior profile
        anomaly_result: Anomaly detection result
        cost_estimate: Cost estimation result
        
    Returns:
        Complete insights response with score, cost, profile, and insights list
    """
    # Calculate energy score
    energy_score = calculate_energy_score(current_power, profile)
    
    # Generate insights
    insights_list = generate_insights(
        current_power=current_power,
        current_current=current_current,
        profile=profile,
        anomaly_result=anomaly_result,
        cost_estimate=cost_estimate,
    )
    
    # Prepare response
    response = {
        "energy_score": energy_score,
        "estimated_cost_rm": cost_estimate.get("estimated_cost_rm", 0.0) if cost_estimate else 0.0,
        "insights": insights_list,
    }
    
    # Include profile if available
    if profile:
        response["behavior_profile"] = {
            "avg_power": profile.get("avg_power", 0),
            "avg_current": profile.get("avg_current", 0),
            "peak_hour": profile.get("peak_hour", 0),
            "usage_pattern": profile.get("usage_pattern", "unknown"),
        }
    
    logger.info(f"Generated AI insights for device {device_id}: score={energy_score}")
    
    return response


def get_recommendations(
    energy_score: int,
    usage_pattern: str,
    avg_power: Optional[float] = None,
) -> List[str]:
    """
    Get energy-saving recommendations based on energy score and usage pattern.
    
    Args:
        energy_score: Energy efficiency score (0-100)
        usage_pattern: Usage pattern ('low', 'normal', 'high')
        avg_power: Average power consumption
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Score-based recommendations
    if energy_score >= 80:
        recommendations.append("Excellent! Maintain your current energy usage habits.")
    elif energy_score >= 60:
        recommendations.append("Good energy efficiency. Consider implementing more energy-saving measures.")
    elif energy_score >= 40:
        recommendations.append("Your energy consumption is moderate. Several optimization opportunities exist.")
    else:
        recommendations.append("High energy consumption detected. Immediate action recommended.")
    
    # Pattern-based recommendations
    if usage_pattern == "high":
        recommendations.append("Switch to energy-efficient appliances.")
        recommendations.append("Use power strips to eliminate standby power draw.")
        recommendations.append("Adjust thermostat by 2-3 degrees to reduce HVAC usage.")
    elif usage_pattern == "normal":
        recommendations.append("Continue monitoring your energy usage regularly.")
    
    return recommendations
