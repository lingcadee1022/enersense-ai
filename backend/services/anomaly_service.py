"""
Anomaly detection service for EnerSense AI.

Detects unusual energy consumption patterns using Isolation Forest algorithm.
Trains and manages ML models for real-time anomaly detection.
"""

import logging
import os
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

logger = logging.getLogger(__name__)

# Model paths
ML_MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "ml")
ANOMALY_MODEL_PATH = os.path.join(ML_MODELS_DIR, "anomaly_model.pkl")


class AnomalyDetector:
    """Anomaly detection model manager using Isolation Forest."""

    def __init__(self, model_path: str = ANOMALY_MODEL_PATH):
        """
        Initialize anomaly detector.
        
        Args:
            model_path: Path to saved model pickle file
        """
        self.model_path = model_path
        self.model = None
        self.load_or_create_model()

    def load_or_create_model(self) -> None:
        """Load existing model or create new one."""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info(f"✓ Loaded anomaly model from {self.model_path}")
            except Exception as e:
                logger.warning(f"Failed to load model: {str(e)}, creating new model")
                self._create_default_model()
        else:
            logger.info("No existing model found, creating new one")
            self._create_default_model()

    def _create_default_model(self) -> None:
        """Create a default Isolation Forest model."""
        self.model = IsolationForest(
            contamination=0.05,  # Assume 5% of data are anomalies
            random_state=42,
            n_estimators=100,
        )
        logger.info("Created new Isolation Forest model")

    def train(self, logs: List[Dict[str, Any]]) -> bool:
        """
        Train anomaly detection model on historical data.
        
        Args:
            logs: List of energy log documents
            
        Returns:
            True if training successful, False otherwise
            
        Example:
            >>> logs = [
            ...     {"power": 150, "current": 0.65},
            ...     {"power": 180, "current": 0.78},
            ... ]
            >>> detector = AnomalyDetector()
            >>> detector.train(logs)
            True
        """
        if not logs or len(logs) < 10:
            logger.warning("Insufficient data for training (need at least 10 samples)")
            return False

        try:
            # Extract features
            df = pd.DataFrame(logs)
            X = df[["power", "current"]].values
            
            # Train model
            self.model.fit(X)
            
            # Save model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            
            logger.info(f"✓ Trained anomaly model on {len(logs)} samples and saved to {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error training anomaly model: {str(e)}")
            return False

    def detect(self, power: float, current: float) -> Dict[str, Any]:
        """
        Detect if current reading is anomalous.
        
        Args:
            power: Power reading in Watts
            current: Current reading in Amperes
            
        Returns:
            Dictionary with is_anomaly (bool), confidence (0-1), and message
            
        Example:
            >>> detector = AnomalyDetector()
            >>> detector.detect(150, 0.65)
            {
                'is_anomaly': False,
                'confidence': 0.95,
                'message': 'Power consumption is within normal range'
            }
        """
        if self.model is None:
            logger.warning("Model not initialized, creating default")
            self._create_default_model()

        try:
            # Prepare input
            X = np.array([[power, current]])
            
            # Get prediction and anomaly score
            prediction = self.model.predict(X)[0]
            anomaly_score = self.model.score_samples(X)[0]
            
            # Convert to anomaly flag (-1 = anomaly, 1 = normal)
            is_anomaly = prediction == -1
            
            # Convert anomaly score to confidence (0-1)
            # Scores are typically between -1 and 1, normalize to 0-1
            confidence = 1.0 / (1.0 + np.exp(anomaly_score)) if anomaly_score else 0.5
            confidence = max(0.0, min(1.0, confidence))
            
            # Generate message
            if is_anomaly:
                message = (
                    f"⚠️ Unusual energy spike detected: {power}W, {current}A. "
                    f"Confidence: {confidence:.1%}"
                )
            else:
                message = "Power consumption is within normal range"
            
            return {
                "is_anomaly": bool(is_anomaly),
                "confidence": round(confidence, 3),
                "message": message,
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomaly: {str(e)}")
            return {
                "is_anomaly": False,
                "confidence": 0.0,
                "message": f"Error in anomaly detection: {str(e)}",
            }

    def detect_batch(self, readings: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in a batch of readings.
        
        Args:
            readings: List of (power, current) tuples
            
        Returns:
            List of anomaly detection results
        """
        return [self.detect(power, current) for power, current in readings]

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        if self.model is None:
            return {"status": "no_model"}
        
        return {
            "type": type(self.model).__name__,
            "contamination": self.model.contamination,
            "n_estimators": self.model.n_estimators,
            "path": self.model_path,
            "exists": os.path.exists(self.model_path),
        }


# Global anomaly detector instance
detector = AnomalyDetector()


def detect_anomaly(power: float, current: float) -> Dict[str, Any]:
    """
    Convenience function to detect anomaly using global detector.
    
    Args:
        power: Power reading in Watts
        current: Current reading in Amperes
        
    Returns:
        Dictionary with is_anomaly, confidence, and message
    """
    return detector.detect(power, current)
