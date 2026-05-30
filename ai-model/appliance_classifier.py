"""
Appliance Classifier - NILM Prediction
Predicts which appliance is running based on power characteristics
"""

import joblib
import os
import numpy as np
from typing import Dict, Any, Optional

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')


class ApplianceClassifier:
    """Classifies appliances using power, voltage, and current"""
    
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.appliance_ranges = {
            'Lighting': {'power': (0, 500), 'current': (0, 2.5)},
            'Refrigerator': {'power': (80, 150), 'current': (0.3, 0.7)},
            'Television': {'power': (600, 1000), 'current': (2.5, 4.2)},
            'Washing Machine': {'power': (1000, 2000), 'current': (4.2, 8.3)},
            'Oven': {'power': (1800, 3500), 'current': (7.5, 14.6)},
            'Air Conditioner': {'power': (1200, 2000), 'current': (5.0, 8.3)},
        }
        self.load_models()
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            model_path = os.path.join(MODELS_DIR, 'appliance_classifier.pkl')
            encoder_path = os.path.join(MODELS_DIR, 'label_encoder.pkl')
            
            if os.path.exists(model_path) and os.path.exists(encoder_path):
                self.model = joblib.load(model_path)
                self.label_encoder = joblib.load(encoder_path)
                print("✓ Models loaded successfully")
            else:
                print("⚠ Models not found. Using rule-based fallback.")
        except Exception as e:
            print(f"⚠ Error loading models: {e}. Using rule-based fallback.")
    
    def predict(self, power: float, voltage: float, current: float) -> str:
        """
        Predict appliance based on power characteristics
        
        Args:
            power: Power consumption in watts
            voltage: Voltage in volts
            current: Current in amperes
            
        Returns:
            Predicted appliance name
        """
        # Use ML model if available
        if self.model is not None:
            try:
                features = np.array([[power, voltage, current]])
                prediction = self.model.predict(features)[0]
                return prediction
            except:
                pass
        
        # Fallback to rule-based detection
        return self._rule_based_prediction(power, current)
    
    def _rule_based_prediction(self, power: float, current: float) -> str:
        """Rule-based appliance detection as fallback"""
        # Match against power/current ranges
        for appliance, ranges in self.appliance_ranges.items():
            power_min, power_max = ranges['power']
            current_min, current_max = ranges['current']
            
            if power_min <= power <= power_max and current_min <= current <= current_max:
                return appliance
        
        # Default classification based on power
        if power < 500:
            return 'Lighting'
        elif 500 <= power < 1200:
            return 'Television'
        elif 1200 <= power < 1800:
            return 'Air Conditioner'
        elif 1800 <= power < 2500:
            return 'Washing Machine'
        else:
            return 'Oven'
    
    def get_energy_score(self, power: float, max_power: float = 3500) -> int:
        """
        Calculate energy score (0-100) based on power consumption
        
        Args:
            power: Current power consumption in watts
            max_power: Maximum typical power consumption
            
        Returns:
            Energy score from 0-100 (lower is better)
        """
        score = int((power / max_power) * 100)
        return min(100, max(0, score))


# Global classifier instance
classifier = ApplianceClassifier()


def predict_appliance(power: float, voltage: float, current: float) -> str:
    """Helper function to predict appliance"""
    return classifier.predict(power, voltage, current)


def get_energy_score(power: float) -> int:
    """Helper function to get energy score"""
    return classifier.get_energy_score(power)
