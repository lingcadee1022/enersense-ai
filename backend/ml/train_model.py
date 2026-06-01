"""
ML model training module for EnerSense AI.

Trains KMeans clustering model for usage pattern classification:
- Low usage cluster
- Normal usage cluster  
- High usage cluster

Features:
- Power (Watts)
- Current (Amperes)

Models are saved as pickle files for production use.
"""

import logging
import os
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

# Model paths
ML_MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "ml")
KMEANS_MODEL_PATH = os.path.join(ML_MODELS_DIR, "kmeans_model.pkl")
SCALER_PATH = os.path.join(ML_MODELS_DIR, "scaler.pkl")


class UsagePatternClusterer:
    """KMeans clusterer for usage pattern classification."""

    def __init__(self, n_clusters: int = 3, model_path: str = KMEANS_MODEL_PATH):
        """
        Initialize clusterer.
        
        Args:
            n_clusters: Number of clusters (default: 3 for low/normal/high)
            model_path: Path to saved model
        """
        self.n_clusters = n_clusters
        self.model_path = model_path
        self.scaler_path = SCALER_PATH
        self.model = None
        self.scaler = StandardScaler()
        self.cluster_names = {
            0: "low_usage",
            1: "normal_usage",
            2: "high_usage",
        }
        self.load_or_create_model()

    def load_or_create_model(self) -> None:
        """Load existing models or create new ones."""
        models_exist = os.path.exists(self.model_path) and os.path.exists(self.scaler_path)
        
        if models_exist:
            try:
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                logger.info(f"✓ Loaded KMeans model from {self.model_path}")
            except Exception as e:
                logger.warning(f"Failed to load models: {str(e)}, creating new ones")
                self._create_default_model()
        else:
            logger.info("No existing models found, creating new ones")
            self._create_default_model()

    def _create_default_model(self) -> None:
        """Create default KMeans model with sample data."""
        self.model = KMeans(
            n_clusters=self.n_clusters,
            random_state=42,
            n_init=10,
        )
        # Create dummy scaler
        self.scaler = StandardScaler()
        logger.info(f"Created new KMeans model with {self.n_clusters} clusters")

    def train(self, logs: List[Dict[str, Any]]) -> bool:
        """
        Train KMeans model on historical data.
        
        Args:
            logs: List of energy log documents
            
        Returns:
            True if training successful, False otherwise
            
        Example:
            >>> logs = [
            ...     {"power": 150, "current": 0.65},
            ...     {"power": 180, "current": 0.78},
            ... ]
            >>> clusterer = UsagePatternClusterer()
            >>> clusterer.train(logs)
            True
        """
        if not logs or len(logs) < 10:
            logger.warning("Insufficient data for training (need at least 10 samples)")
            return False

        try:
            # Extract features
            df = pd.DataFrame(logs)
            X = df[["power", "current"]].values
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled)
            
            # Save models
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            # Log cluster centers
            centers = self.scaler.inverse_transform(self.model.cluster_centers_)
            logger.info(f"✓ Trained KMeans on {len(logs)} samples")
            for i, center in enumerate(centers):
                logger.info(f"  Cluster {i} ({self.cluster_names.get(i, 'unknown')}): Power={center[0]:.1f}W, Current={center[1]:.2f}A")
            
            return True
            
        except Exception as e:
            logger.error(f"Error training KMeans model: {str(e)}")
            return False

    def predict_cluster(self, power: float, current: float) -> Dict[str, Any]:
        """
        Predict usage pattern cluster for a reading.
        
        Args:
            power: Power reading in Watts
            current: Current reading in Amperes
            
        Returns:
            Dictionary with cluster_id, cluster_name, and confidence
            
        Example:
            >>> clusterer = UsagePatternClusterer()
            >>> clusterer.predict_cluster(150, 0.65)
            {
                'cluster_id': 1,
                'cluster_name': 'normal_usage',
                'confidence': 0.85
            }
        """
        if self.model is None:
            logger.warning("Model not initialized")
            return {
                "cluster_id": -1,
                "cluster_name": "unknown",
                "confidence": 0.0,
            }

        try:
            # Prepare input
            X = np.array([[power, current]])
            X_scaled = self.scaler.transform(X)
            
            # Predict cluster
            cluster_id = self.model.predict(X_scaled)[0]
            
            # Calculate confidence based on distance to cluster center
            distances = np.sqrt(np.sum((X_scaled - self.model.cluster_centers_) ** 2, axis=1))
            closest_distance = distances[cluster_id]
            
            # Confidence is inverse of normalized distance
            max_distance = np.max(distances)
            confidence = 1.0 - (closest_distance / (max_distance + 1e-10))
            confidence = max(0.0, min(1.0, confidence))
            
            cluster_name = self.cluster_names.get(cluster_id, "unknown")
            
            return {
                "cluster_id": int(cluster_id),
                "cluster_name": cluster_name,
                "confidence": round(confidence, 3),
            }
            
        except Exception as e:
            logger.error(f"Error predicting cluster: {str(e)}")
            return {
                "cluster_id": -1,
                "cluster_name": "error",
                "confidence": 0.0,
            }

    def predict_batch(self, readings: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
        """
        Predict clusters for batch of readings.
        
        Args:
            readings: List of (power, current) tuples
            
        Returns:
            List of cluster predictions
        """
        return [self.predict_cluster(power, current) for power, current in readings]

    def get_cluster_info(self) -> Dict[str, Any]:
        """Get information about trained clusters."""
        if self.model is None:
            return {"status": "no_model"}
        
        try:
            centers = self.scaler.inverse_transform(self.model.cluster_centers_)
            cluster_info = {}
            
            for i in range(self.n_clusters):
                cluster_info[self.cluster_names.get(i, f"cluster_{i}")] = {
                    "center_power_w": round(centers[i][0], 2),
                    "center_current_a": round(centers[i][1], 3),
                }
            
            return {
                "n_clusters": self.n_clusters,
                "inertia": round(self.model.inertia_, 2),
                "clusters": cluster_info,
                "model_path": self.model_path,
                "exists": os.path.exists(self.model_path),
            }
        except Exception as e:
            logger.error(f"Error getting cluster info: {str(e)}")
            return {"status": "error", "error": str(e)}


# Global clusterer instance
clusterer = UsagePatternClusterer()


def predict_usage_pattern(power: float, current: float) -> Dict[str, Any]:
    """
    Convenience function to predict usage pattern.
    
    Args:
        power: Power reading in Watts
        current: Current reading in Amperes
        
    Returns:
        Dictionary with cluster prediction
    """
    return clusterer.predict_cluster(power, current)
