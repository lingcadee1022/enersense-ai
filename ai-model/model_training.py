"""
Model Training Script
Trains and saves ML models for appliance classification
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from datetime import datetime

# Define paths
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'sample_data.csv')


def train_appliance_classifier():
    """Train a Random Forest classifier for appliance prediction"""
    print("Training Appliance Classifier...")
    
    # Load data
    df = pd.read_csv(DATA_FILE)
    
    # Features: power, voltage, current
    X = df[['power', 'voltage', 'current']].values
    y = df['appliance'].values
    
    # Train Random Forest model
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X, y)
    
    # Save model
    model_path = os.path.join(MODELS_DIR, 'appliance_classifier.pkl')
    joblib.dump(model, model_path)
    print(f"✓ Appliance Classifier saved to {model_path}")
    
    return model


def train_anomaly_detector():
    """Train an Isolation Forest for anomaly detection"""
    print("Training Anomaly Detector...")
    
    # Load data
    df = pd.read_csv(DATA_FILE)
    
    # Features: power consumption
    X = df[['power']].values
    
    # Train Isolation Forest
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X)
    
    # Save model
    model_path = os.path.join(MODELS_DIR, 'anomaly_detector.pkl')
    joblib.dump(model, model_path)
    print(f"✓ Anomaly Detector saved to {model_path}")
    
    return model


def save_label_encoder():
    """Save label encoder for appliance names"""
    print("Saving Label Encoder...")
    
    df = pd.read_csv(DATA_FILE)
    le = LabelEncoder()
    le.fit(df['appliance'].unique())
    
    # Save label encoder
    encoder_path = os.path.join(MODELS_DIR, 'label_encoder.pkl')
    joblib.dump(le, encoder_path)
    print(f"✓ Label Encoder saved to {encoder_path}")
    
    return le


def main():
    """Train and save all models"""
    print("\n" + "="*50)
    print("EnerSense AI - Model Training")
    print("="*50 + "\n")
    
    # Train all models
    appliance_model = train_appliance_classifier()
    anomaly_model = train_anomaly_detector()
    label_encoder = save_label_encoder()
    
    print("\n" + "="*50)
    print("✓ All models trained and saved successfully!")
    print("="*50 + "\n")
    
    # Print sample predictions
    print("Sample Predictions:")
    print("-" * 50)
    sample_data = np.array([[1500, 240, 6.25]])  # AC usage
    pred = appliance_model.predict(sample_data)
    print(f"Input: power=1500, voltage=240, current=6.25")
    print(f"Predicted appliance: {pred[0]}")


if __name__ == '__main__':
    main()
