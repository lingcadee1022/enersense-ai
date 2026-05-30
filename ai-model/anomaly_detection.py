"""
Anomaly Detection Module
Detects unusual or suspicious energy usage patterns
"""

import joblib
import os
import numpy as np
from typing import Dict, Any, List, Tuple
from collections import deque

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')


class AnomalyDetector:
    """Detects anomalies in energy consumption"""
    
    def __init__(self, window_size: int = 24):
        self.model = None
        self.window_size = window_size
        self.power_history = deque(maxlen=window_size)
        self.threshold_factor = 1.5  # Multiplier for anomaly detection
        self.load_model()
    
    def load_model(self):
        """Load trained anomaly detection model"""
        try:
            model_path = os.path.join(MODELS_DIR, 'anomaly_detector.pkl')
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                print("✓ Anomaly detector model loaded")
            else:
                print("⚠ Anomaly detector model not found. Using statistical detection.")
        except Exception as e:
            print(f"⚠ Error loading anomaly model: {e}. Using statistical detection.")
    
    def add_reading(self, power: float) -> bool:
        """Add a power reading to history"""
        self.power_history.append(power)
    
    def detect_anomaly(self, power: float) -> Tuple[bool, float]:
        """
        Detect if current power reading is anomalous
        
        Args:
            power: Current power consumption in watts
            
        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        # Use ML model if available
        if self.model is not None:
            try:
                features = np.array([[power]])
                prediction = self.model.predict(features)[0]
                is_anomaly = prediction == -1  # -1 indicates anomaly in Isolation Forest
                anomaly_score = abs(prediction)  # Use absolute value as score
                return is_anomaly, anomaly_score
            except:
                pass
        
        # Fallback to statistical detection
        return self._statistical_detection(power)
    
    def _statistical_detection(self, power: float) -> Tuple[bool, float]:
        """Statistical anomaly detection using z-score"""
        if len(self.power_history) < 3:
            return False, 0.0
        
        history_array = np.array(list(self.power_history))
        mean = np.mean(history_array)
        std = np.std(history_array)
        
        # Calculate z-score
        if std == 0:
            z_score = 0
        else:
            z_score = abs((power - mean) / std)
        
        # Anomaly threshold: z-score > 2.5
        is_anomaly = z_score > 2.5
        
        return is_anomaly, z_score
    
    def get_baseline_power(self) -> float:
        """Get average baseline power from history"""
        if len(self.power_history) == 0:
            return 0.0
        return np.mean(list(self.power_history))
    
    def get_power_statistics(self) -> Dict[str, float]:
        """Get statistics about power consumption"""
        if len(self.power_history) == 0:
            return {'min': 0, 'max': 0, 'mean': 0, 'std': 0}
        
        history = list(self.power_history)
        return {
            'min': float(np.min(history)),
            'max': float(np.max(history)),
            'mean': float(np.mean(history)),
            'std': float(np.std(history))
        }


class AnomalyAnalyzer:
    """Analyzes anomalies and generates insights"""
    
    def __init__(self):
        self.detector = AnomalyDetector()
        self.anomaly_history: List[Dict] = []
    
    def analyze(self, power: float, appliance: str) -> Dict[str, Any]:
        """
        Analyze power reading for anomalies
        
        Args:
            power: Power consumption in watts
            appliance: Identified appliance
            
        Returns:
            Analysis result with anomaly info
        """
        is_anomaly, score = self.detector.detect_anomaly(power)
        self.detector.add_reading(power)
        
        result = {
            'is_anomaly': is_anomaly,
            'anomaly_score': float(score),
            'insight': None
        }
        
        if is_anomaly:
            result['insight'] = self._generate_anomaly_insight(power, appliance)
            self.anomaly_history.append({
                'power': power,
                'appliance': appliance,
                'insight': result['insight']
            })
        
        return result
    
    def _generate_anomaly_insight(self, power: float, appliance: str) -> str:
        """Generate human-readable anomaly insight"""
        baseline = self.detector.get_baseline_power()
        
        if power > baseline * 1.5:
            return f"{appliance} usage unusually high - consuming {power}W (normal: ~{baseline:.0f}W)"
        elif power < baseline * 0.5 and baseline > 0:
            return f"{appliance} usage unusually low"
        else:
            return f"Unusual pattern detected for {appliance}"
    
    def get_recent_anomalies(self, limit: int = 5) -> List[Dict]:
        """Get recent anomaly events"""
        return self.anomaly_history[-limit:]


# Global analyzer instance
analyzer = AnomalyAnalyzer()


def detect_anomaly(power: float) -> Tuple[bool, float]:
    """Helper function to detect anomaly"""
    is_anomaly, score = analyzer.detector.detect_anomaly(power)
    analyzer.detector.add_reading(power)
    return is_anomaly, score


def analyze_reading(power: float, appliance: str) -> Dict[str, Any]:
    """Helper function to analyze reading"""
    return analyzer.analyze(power, appliance)
