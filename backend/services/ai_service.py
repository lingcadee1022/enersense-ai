"""
Create a service layer that connects FastAPI routes with ML model.

Requirements:
- Function: get_ai_result(power, current)
- Call prediction model from ml/predict.py
- Return structured JSON:
  {
    cluster,
    message,
    energy_status
  }
- Add simple rules:
  cluster 0 = low usage
  cluster 1 = normal usage
  cluster 2 = high usage
"""

from ml.predict import predict, get_cluster_description
from typing import Dict, Any

def get_ai_result(power: float, current: float) -> Dict[str, Any]:
    """
    Get AI prediction result with structured output.
    
    Args:
        power (float): Power consumption in watts
        current (float): Current in amperes
    
    Returns:
        dict: AI result with cluster, message, and energy status
    """
    try:
        # Get prediction from ML model
        prediction = predict(power, current)
        cluster = prediction["cluster"]
        
        # Map cluster to energy status
        energy_status_map = {
            0: "low",
            1: "normal",
            2: "high"
        }
        energy_status = energy_status_map.get(cluster, "unknown")
        
        # Generate message based on cluster
        messages = {
            0: "✅ Low energy usage detected. Excellent efficiency!",
            1: "ℹ️ Normal energy usage. Operating within expected ranges.",
            2: "⚠️ High energy usage detected. Consider optimizing consumption."
        }
        message = messages.get(cluster, "Unable to determine energy status")
        
        # Generate detailed message with values
        detailed_message = f"{message} (Power: {power:.2f}W, Current: {current:.2f}A)"
        
        # Additional recommendations
        recommendations = {
            0: "Continue with current usage patterns",
            1: "Monitor usage trends and maintain current efficiency",
            2: "Consider identifying high-consumption appliances and reduce usage"
        }
        recommendation = recommendations.get(cluster, "")
        
        return {
            "cluster": cluster,
            "energy_status": energy_status,
            "message": detailed_message,
            "recommendation": recommendation,
            "cluster_description": get_cluster_description(cluster),
            "power": prediction["power"],
            "current": prediction["current"],
            "model_available": prediction["model_available"]
        }
    
    except Exception as e:
        return {
            "cluster": -1,
            "energy_status": "error",
            "message": f"Error processing AI result: {str(e)}",
            "recommendation": "Please try again later",
            "power": power,
            "current": current,
            "model_available": False
        }

def get_energy_status_color(cluster: int) -> str:
    """
    Get color code for energy status visualization.
    
    Args:
        cluster (int): Cluster label
    
    Returns:
        str: Color code (hex)
    """
    colors = {
        0: "#4CAF50",  # Green - Low usage
        1: "#2196F3",  # Blue - Normal usage
        2: "#F44336"   # Red - High usage
    }
    return colors.get(cluster, "#9E9E9E")  # Gray - Unknown

def get_energy_savings_potential(power: float, cluster: int) -> Dict[str, Any]:
    """
    Calculate potential energy savings.
    
    Args:
        power (float): Current power consumption
        cluster (int): Current cluster
    
    Returns:
        dict: Savings potential analysis
    """
    if cluster == 0:
        return {
            "potential_savings": "Minimal",
            "percentage": 0,
            "suggestions": ["Maintain current usage patterns"]
        }
    elif cluster == 1:
        return {
            "potential_savings": "Moderate",
            "percentage": 10,
            "suggestions": [
                "Monitor peak usage times",
                "Consider using energy-efficient appliances",
                "Schedule usage during off-peak hours"
            ]
        }
    else:  # cluster == 2
        target_power = power * 0.7  # 30% reduction target
        savings = power - target_power
        percentage = (savings / power) * 100 if power > 0 else 0
        
        return {
            "potential_savings": f"{savings:.2f}W",
            "percentage": round(percentage, 2),
            "target_power": round(target_power, 2),
            "suggestions": [
                "Identify and reduce high-consumption appliances",
                "Turn off devices when not in use",
                "Use smart power strips to eliminate standby power",
                "Consider scheduling usage to distribute load"
            ]
        }

def batch_ai_analysis(records: list) -> Dict[str, Any]:
    """
    Analyze multiple records and provide batch insights.
    
    Args:
        records (list): List of energy records with power and current
    
    Returns:
        dict: Batch analysis results
    """
    if not records:
        return {
            "status": "failed",
            "message": "No records to analyze"
        }
    
    results = []
    total_power = 0
    cluster_distribution = {}
    
    for record in records:
        power = record.get("power", 0)
        current = record.get("current", 0)
        
        ai_result = get_ai_result(power, current)
        results.append(ai_result)
        
        total_power += power
        cluster = ai_result["cluster"]
        cluster_distribution[cluster] = cluster_distribution.get(cluster, 0) + 1
    
    avg_power = total_power / len(records)
    dominant_cluster = max(cluster_distribution, key=cluster_distribution.get) if cluster_distribution else -1
    
    return {
        "status": "success",
        "total_records": len(records),
        "average_power": round(avg_power, 2),
        "total_power": round(total_power, 2),
        "dominant_cluster": dominant_cluster,
        "cluster_distribution": cluster_distribution,
        "analysis_results": results
    }
