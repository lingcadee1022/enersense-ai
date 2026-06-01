"""
Create a training script for energy usage pattern detection.

Requirements:
- Load data from MongoDB 'energy_logs'
- Use pandas for data preprocessing
- Train a simple KMeans clustering model (3 clusters)
- Save model as model.pkl using joblib
- Features: power, current
- Include function train_model()
"""

import pandas as pd
import joblib
import os
import logging
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from db.mongo import get_db

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

def train_model(n_clusters: int = 3) -> dict:
    """
    Train a KMeans clustering model on energy data from MongoDB.
    
    Args:
        n_clusters (int): Number of clusters (default: 3)
    
    Returns:
        dict: Training results with metrics
    """
    try:
        logger.info("Starting model training...")
        
        # Connect to MongoDB
        db = get_db()
        
        # Fetch data from energy_logs collection
        logger.info("Fetching data from MongoDB...")
        records = list(db.energy_logs.find())
        
        if len(records) < 10:
            logger.warning("Not enough data for training. Need at least 10 samples.")
            return {
                "status": "failed",
                "message": "Insufficient data for training",
                "records_found": len(records)
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        
        # Select features: power and current
        if "power" not in df.columns or "current" not in df.columns:
            logger.error("Required columns 'power' and 'current' not found in data")
            return {
                "status": "failed",
                "message": "Missing required columns: power, current"
            }
        
        # Prepare data for training
        X = df[["power", "current"]].values
        
        # Handle any missing values
        df_features = pd.DataFrame(X, columns=["power", "current"])
        df_features = df_features.dropna()
        X = df_features.values
        
        if len(X) == 0:
            logger.error("No valid data after preprocessing")
            return {
                "status": "failed",
                "message": "No valid data after preprocessing"
            }
        
        logger.info(f"Training data shape: {X.shape}")
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train KMeans model
        logger.info(f"Training KMeans model with {n_clusters} clusters...")
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        model.fit(X_scaled)
        
        # Save model
        joblib.dump(model, MODEL_PATH)
        logger.info(f"Model saved to {MODEL_PATH}")
        
        # Calculate metrics
        inertia = model.inertia_
        n_samples = len(X)
        
        # Store training info
        training_info = {
            "model_path": MODEL_PATH,
            "n_clusters": n_clusters,
            "n_samples": n_samples,
            "features": ["power", "current"],
            "inertia": float(inertia),
            "cluster_centers": model.cluster_centers_.tolist()
        }
        
        # Save training info to MongoDB
        db.ai_insights.insert_one({
            "type": "training_info",
            "timestamp": pd.Timestamp.utcnow().to_pydatetime(),
            "info": training_info
        })
        
        logger.info("Model training completed successfully")
        
        return {
            "status": "success",
            "message": "Model trained and saved successfully",
            "training_info": training_info
        }
    
    except Exception as e:
        logger.error(f"Error during model training: {str(e)}")
        return {
            "status": "failed",
            "message": f"Error during training: {str(e)}"
        }

def evaluate_model() -> dict:
    """
    Evaluate the trained model on MongoDB data.
    
    Returns:
        dict: Evaluation metrics
    """
    try:
        if not os.path.exists(MODEL_PATH):
            logger.warning("Model file not found")
            return {
                "status": "failed",
                "message": "Model file not found"
            }
        
        # Load model
        model = joblib.load(MODEL_PATH)
        
        # Fetch data
        db = get_db()
        records = list(db.energy_logs.find())
        
        if len(records) == 0:
            return {
                "status": "failed",
                "message": "No data available for evaluation"
            }
        
        # Prepare data
        df = pd.DataFrame(records)
        X = df[["power", "current"]].values
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Predictions
        predictions = model.predict(X_scaled)
        inertia = model.inertia_
        
        return {
            "status": "success",
            "n_samples": len(predictions),
            "inertia": float(inertia),
            "cluster_distribution": {
                str(i): int((predictions == i).sum()) for i in range(len(model.cluster_centers_))
            }
        }
    
    except Exception as e:
        logger.error(f"Error during model evaluation: {str(e)}")
        return {
            "status": "failed",
            "message": f"Error during evaluation: {str(e)}"
        }

if __name__ == "__main__":
    # Run training
    result = train_model()
    print(result)
