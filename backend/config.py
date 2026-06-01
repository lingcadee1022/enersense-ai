"""
Configuration module for EnerSense AI Backend.

Manages all configuration settings from environment variables with sensible defaults.
"""

import os
from typing import Optional

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    """Application configuration."""
    
    # ==================== DATABASE ====================
    
    MONGODB_URI: str = os.getenv(
        "MONGODB_URI",
        "mongodb://localhost:27017/"
    )
    """MongoDB connection URI."""
    
    DATABASE_NAME: str = "enersense"
    """MongoDB database name."""
    
    # ==================== SERVER ====================
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    """Server host address."""
    
    PORT: int = int(os.getenv("PORT", "8000"))
    """Server port number."""
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    """Environment: development or production."""
    
    DEBUG: bool = ENVIRONMENT == "development"
    """Enable debug mode."""
    
    RELOAD: bool = ENVIRONMENT == "development"
    """Auto-reload on file changes."""
    
    # ==================== CORS ====================
    
    CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8081",
        "http://192.168.1.1",
        "*",  # Allow all in development
    ]
    """Allowed origins for CORS."""
    
    # ==================== LOGGING ====================
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    """Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL."""
    
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    """Log message format."""
    
    # ==================== ENERGY SETTINGS ====================
    
    DEFAULT_TARIFF_RM_PER_KWH: float = float(
        os.getenv("TARIFF_RM_PER_KWH", "0.571")
    )
    """Electricity tariff in Malaysian Ringgit per kWh (Malaysia default: 0.571)."""
    
    # ==================== ML SETTINGS ====================
    
    ANOMALY_CONTAMINATION: float = 0.05
    """Isolation Forest contamination (% expected anomalies)."""
    
    KMEANS_N_CLUSTERS: int = 3
    """Number of KMeans clusters for usage patterns."""
    
    ML_MODELS_DIR: str = os.path.join(
        os.path.dirname(__file__),
        "..",
        "ml"
    )
    """Directory for storing ML models."""
    
    # ==================== API SETTINGS ====================
    
    API_V1_PREFIX: str = "/api/v1"
    """API version 1 prefix."""
    
    API_TITLE: str = "EnerSense AI Backend"
    """API title."""
    
    API_DESCRIPTION: str = "IoT energy monitoring system with AI insights"
    """API description."""
    
    API_VERSION: str = "1.0.0"
    """API version."""
    
    # ==================== DATA RETENTION ====================
    
    MAX_HISTORY_DAYS: int = 365
    """Maximum days of history to retrieve."""
    
    MAX_HISTORY_HOURS: int = 720  # 30 days
    """Maximum hours of history to retrieve."""
    
    MIN_DATA_POINTS_FOR_ANALYSIS: int = 10
    """Minimum data points required for analysis."""
    
    # ==================== UTILITY METHODS ====================
    
    @classmethod
    def get_mongo_uri(cls) -> str:
        """Get MongoDB connection URI."""
        return cls.MONGODB_URI
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode."""
        return cls.ENVIRONMENT.lower() == "development"
    
    @classmethod
    def log_config(cls) -> None:
        """Log current configuration."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("=" * 60)
        logger.info("EnerSense AI Configuration")
        logger.info("=" * 60)
        logger.info(f"Environment: {cls.ENVIRONMENT}")
        logger.info(f"Server: {cls.HOST}:{cls.PORT}")
        logger.info(f"MongoDB: {cls.MONGODB_URI}")
        logger.info(f"Tariff: RM {cls.DEFAULT_TARIFF_RM_PER_KWH}/kWh")
        logger.info(f"Log Level: {cls.LOG_LEVEL}")
        logger.info("=" * 60)
    
    @classmethod
    def to_dict(cls) -> dict:
        """Convert configuration to dictionary."""
        return {
            "environment": cls.ENVIRONMENT,
            "host": cls.HOST,
            "port": cls.PORT,
            "database": cls.DATABASE_NAME,
            "tariff_rm_per_kwh": cls.DEFAULT_TARIFF_RM_PER_KWH,
            "log_level": cls.LOG_LEVEL,
            "api_version": cls.API_VERSION,
        }


# Create config instance
config = Config()

# Export commonly used settings
MONGODB_URI = config.MONGODB_URI
API_V1_PREFIX = config.API_V1_PREFIX
DEFAULT_TARIFF_RM_PER_KWH = config.DEFAULT_TARIFF_RM_PER_KWH
DEBUG = config.DEBUG
ENVIRONMENT = config.ENVIRONMENT
