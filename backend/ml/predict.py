"""
Create a machine learning inference module for EnerSense AI.

Requirements:
- Load a pre-trained model using joblib (model.pkl)
- Input: power and current values
- Output: cluster label or appliance type prediction
- Handle missing model file gracefully
- Keep function reusable for API calls
"""

import joblib
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Path to model file
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

# Cache for loaded model
_loaded_model = None

def load_model():
    """
    Load the pre-trained KMeans model from disk.
    
    Returns:
        sklearn.cluster.KMeans: Loaded model or None if not found
    """
    global _loaded_model
    
    if _loaded_model is not None:
        return _loaded_model
    
    if not os.path.exists(MODEL_PATH):
        logger.warning(f"Model file not found at {MODEL_PATH}. Using default clustering.")
        return None
    
    try:
        _loaded_model = joblib.load(MODEL_PATH)
        logger.info(f"Model loaded successfully from {MODEL_PATH}")
        return _loaded_model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return None

def predict(power: float, current: float) -> Dict[str, Any]:
    """
    Predict appliance cluster based on power and current values.
    
    Args:
        power (float): Power consumption in watts
        current (float): Current in amperes
    
    Returns:
        dict: Prediction result with cluster label and confidence
    """
    try:
        model = load_model()
        
        if model is None:
            # Default clustering if model not available
            return default_prediction(power, current)
        
        # Prepare input data
        X = [[power, current]]
        
        # Make prediction
        cluster = model.predict(X)[0]
        
        return {
            "cluster": int(cluster),
            "power": round(power, 2),
            "current": round(current, 2),
            "model_available": True
        }
    
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return default_prediction(power, current)

def default_prediction(power: float, current: float) -> Dict[str, Any]:
    """
    Default prediction using simple power thresholds when model is unavailable.
    
    Args:
        power (float): Power consumption in watts
        current (float): Current in amperes
    
    Returns:
        dict: Default cluster prediction based on power thresholds
    """
    # Simple rule-based clustering
    if power < 300:
        cluster = 0  # Low usage
    elif power < 1000:
        cluster = 1  # Normal usage
    else:
        cluster = 2  # High usage
    
    return {
        "cluster": cluster,
        "power": round(power, 2),
        "current": round(current, 2),
        "model_available": False
    }

def get_cluster_description(cluster: int) -> str:
    """
    Get human-readable description of cluster.
    
    Args:
        cluster (int): Cluster label
    
    Returns:
        str: Description of the cluster
    """
    descriptions = {
        0: "Low energy usage",
        1: "Normal energy usage",
        2: "High energy usage"
    }
    return descriptions.get(cluster, "Unknown cluster")
