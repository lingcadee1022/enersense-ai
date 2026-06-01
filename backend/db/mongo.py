"""
MongoDB connection and operations module for EnerSense AI.

This module handles all database operations including:
- Connection management
- Energy log storage and retrieval
- User profile management
- AI insights storage
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


class MongoDBClient:
    """MongoDB client for EnerSense AI backend."""

    _instance = None
    _client: Optional[MongoClient] = None
    _db = None

    def __new__(cls):
        """Singleton pattern to ensure single database connection."""
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
        return cls._instance

    def connect(self) -> None:
        """
        Establish MongoDB connection using MONGODB_URI from environment.
        
        Raises:
            ConnectionFailure: If unable to connect to MongoDB
            ValueError: If MONGODB_URI not set in environment
        """
        if self._client is not None:
            return

        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        
        try:
            logger.info(f"Connecting to MongoDB: {mongo_uri}")
            self._client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self._client.admin.command("ping")
            self._db = self._client["enersense"]
            self.create_indexes()
            logger.info("✓ Connected to MongoDB successfully")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise ConnectionFailure(f"Failed to connect to MongoDB: {str(e)}")

    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("✓ Disconnected from MongoDB")

    def get_db(self):
        """Get database instance."""
        if self._db is None:
            self.connect()
        return self._db

    # ==================== ENERGY LOGS ====================

    def insert_energy_log(
        self,
        device_id: str,
        current: float,
        power: float,
        voltage: float = 240.0,
    ) -> str:
        """
        Insert energy log with auto-generated timestamp.
        
        Args:
            device_id: ESP32 device identifier
            current: Current reading in Amperes
            power: Power reading in Watts
            voltage: Voltage reading in Volts
            
        Returns:
            Document ID of inserted log
        """
        db = self.get_db()
        log_doc = {
            "device_id": device_id,
            "voltage": voltage,
            "current": current,
            "power": power,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        result = db.energy_logs.insert_one(log_doc)
        logger.info(f"Inserted energy log for {device_id}")
        return str(result.inserted_id)

    def get_latest_energy_log(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest energy log for a device.
        
        Args:
            device_id: ESP32 device identifier
            
        Returns:
            Latest energy log document or None if not found
        """
        db = self.get_db()
        log = db.energy_logs.find_one(
            {"device_id": device_id},
            sort=[("timestamp", -1)],
        )
        return log

    def get_energy_logs_by_hours(
        self, device_id: str, hours: int
    ) -> List[Dict[str, Any]]:
        """
        Get energy logs for the past N hours.
        
        Args:
            device_id: ESP32 device identifier
            hours: Number of hours to retrieve
            
        Returns:
            List of energy log documents sorted by timestamp (ascending)
        """
        db = self.get_db()
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        logs = list(
            db.energy_logs.find(
                {
                    "device_id": device_id,
                    "timestamp": {"$gte": cutoff_time.isoformat() + "Z"},
                },
                sort=[("timestamp", 1)],
            )
        )
        logger.info(f"Retrieved {len(logs)} logs for {device_id} in past {hours} hours")
        return logs

    def get_energy_logs_by_days(
        self, device_id: str, days: int
    ) -> List[Dict[str, Any]]:
        """
        Get energy logs for the past N days.
        
        Args:
            device_id: ESP32 device identifier
            days: Number of days to retrieve
            
        Returns:
            List of energy log documents sorted by timestamp (ascending)
        """
        db = self.get_db()
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        logs = list(
            db.energy_logs.find(
                {
                    "device_id": device_id,
                    "timestamp": {"$gte": cutoff_time.isoformat() + "Z"},
                },
                sort=[("timestamp", 1)],
            )
        )
        logger.info(f"Retrieved {len(logs)} logs for {device_id} in past {days} days")
        return logs

    def get_all_energy_logs(self, device_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get all energy logs for a device (for ML training).
        
        Args:
            device_id: ESP32 device identifier
            limit: Maximum number of records to retrieve
            
        Returns:
            List of energy log documents sorted by timestamp (ascending)
        """
        db = self.get_db()
        logs = list(
            db.energy_logs.find(
                {"device_id": device_id},
                sort=[("timestamp", -1)],
            ).limit(limit)
        )
        return list(reversed(logs))  # Return in ascending order

    # ==================== USER PROFILES ====================

    def upsert_user_profile(self, device_id: str, profile: Dict[str, Any]) -> None:
        """
        Insert or update user profile for a device.
        
        Args:
            device_id: ESP32 device identifier
            profile: Profile data containing behavior analytics
        """
        db = self.get_db()
        profile_doc = {
            "device_id": device_id,
            **profile,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        db.user_profiles.update_one(
            {"device_id": device_id},
            {"$set": profile_doc},
            upsert=True,
        )
        logger.info(f"Updated user profile for {device_id}")

    def get_user_profile(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile for a device.
        
        Args:
            device_id: ESP32 device identifier
            
        Returns:
            Profile document or None if not found
        """
        db = self.get_db()
        profile = db.user_profiles.find_one({"device_id": device_id})
        return profile

    # ==================== AI INSIGHTS ====================

    def insert_insight(self, device_id: str, insight_data: Dict[str, Any]) -> str:
        """
        Insert AI insight record.
        
        Args:
            device_id: ESP32 device identifier
            insight_data: Insight data with energy score, cost, and insights list
            
        Returns:
            Document ID of inserted insight
        """
        db = self.get_db()
        insight_doc = {
            "device_id": device_id,
            **insight_data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        result = db.ai_insights.insert_one(insight_doc)
        logger.info(f"Inserted AI insight for {device_id}")
        return str(result.inserted_id)

    def get_latest_insight(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest AI insight for a device.
        
        Args:
            device_id: ESP32 device identifier
            
        Returns:
            Latest insight document or None if not found
        """
        db = self.get_db()
        insight = db.ai_insights.find_one(
            {"device_id": device_id},
            sort=[("timestamp", -1)],
        )
        return insight

    # ==================== ALERTS ====================

    def insert_alert(self, device_id: str, alert_data: Dict[str, Any]) -> str:
        """
        Insert energy alert record.
        
        Args:
            device_id: ESP32 device identifier
            alert_data: Alert data containing alert level, type, message, and readings
            
        Returns:
            Document ID of inserted alert
        """
        db = self.get_db()
        alert_doc = {
            "device_id": device_id,
            **alert_data,
            "inserted_at": datetime.utcnow().isoformat() + "Z",
        }
        result = db.alerts.insert_one(alert_doc)
        logger.info(f"Inserted alert for {device_id}: {alert_data.get('type', 'UNKNOWN')}")
        return str(result.inserted_id)

    def get_latest_alert(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest alert for a device.
        
        Args:
            device_id: ESP32 device identifier
            
        Returns:
            Latest alert document or None if not found
        """
        db = self.get_db()
        alert = db.alerts.find_one(
            {"device_id": device_id},
            sort=[("timestamp", -1)],
        )
        return alert

    def get_alerts_by_level(
        self, device_id: str, level: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get alerts by alert level.
        
        Args:
            device_id: ESP32 device identifier
            level: Alert level ("warning" or "critical")
            limit: Maximum number of alerts to retrieve
            
        Returns:
            List of alert documents
        """
        db = self.get_db()
        alerts = list(
            db.alerts.find(
                {"device_id": device_id, "level": level},
                sort=[("timestamp", -1)],
            ).limit(limit)
        )
        logger.info(f"Retrieved {len(alerts)} {level} alerts for {device_id}")
        return alerts

    def get_recent_alerts(
        self, device_id: str, hours: int = 24, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent alerts within specified time window.
        
        Args:
            device_id: ESP32 device identifier
            hours: Number of hours to look back
            limit: Maximum number of alerts to retrieve
            
        Returns:
            List of alert documents
        """
        db = self.get_db()
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        alerts = list(
            db.alerts.find(
                {
                    "device_id": device_id,
                    "timestamp": {"$gte": cutoff_time.isoformat() + "Z"},
                },
                sort=[("timestamp", -1)],
            ).limit(limit)
        )
        logger.info(f"Retrieved {len(alerts)} recent alerts for {device_id}")
        return alerts

    def get_all_alerts(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all alerts for a device.
        
        Args:
            device_id: ESP32 device identifier
            limit: Maximum number of alerts to retrieve
            
        Returns:
            List of alert documents sorted by timestamp (descending)
        """
        db = self.get_db()
        alerts = list(
            db.alerts.find(
                {"device_id": device_id},
                sort=[("timestamp", -1)],
            ).limit(limit)
        )
        logger.info(f"Retrieved {len(alerts)} alerts for {device_id}")
        return alerts

    # ==================== HOUSEHOLD PROFILE ====================

    def insert_household_profile(self, profile_doc: Dict[str, Any]) -> str:
        """
        Insert a new household profile.
        
        Args:
            profile_doc: Household profile document with user_id and profile data
            
        Returns:
            Document ID of inserted profile
        """
        db = self.get_db()
        result = db.household_profiles.insert_one(profile_doc)
        logger.info(f"Inserted household profile for {profile_doc.get('user_id')}")
        return str(result.inserted_id)

    def get_household_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get household profile for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Household profile document or None if not found
        """
        db = self.get_db()
        profile = db.household_profiles.find_one({"user_id": user_id})
        return profile

    def update_household_profile(
        self, user_id: str, profile_data: Dict[str, Any]
    ) -> None:
        """
        Update existing household profile.
        
        Args:
            user_id: User identifier
            profile_data: Updated profile data
        """
        db = self.get_db()
        db.household_profiles.update_one(
            {"user_id": user_id},
            {"$set": profile_data},
            upsert=True,
        )
        logger.info(f"Updated household profile for {user_id}")

    # ==================== COLLECTION MANAGEMENT ====================

    def create_indexes(self) -> None:
        """Create necessary database indexes for performance."""
        db = self.get_db()

        # Energy logs indexes
        db.energy_logs.create_index("device_id")
        db.energy_logs.create_index("timestamp")
        db.energy_logs.create_index([("device_id", 1), ("timestamp", -1)])

        # User profiles index
        db.user_profiles.create_index("device_id", unique=True)

        # AI insights indexes
        db.ai_insights.create_index("device_id")
        db.ai_insights.create_index("timestamp")
        db.ai_insights.create_index([("device_id", 1), ("timestamp", -1)])

        # Alerts indexes
        db.alerts.create_index("device_id")
        db.alerts.create_index("timestamp")
        db.alerts.create_index("level")
        db.alerts.create_index([("device_id", 1), ("timestamp", -1)])
        db.alerts.create_index([("device_id", 1), ("level", 1), ("timestamp", -1)])

        # Household profiles index
        db.household_profiles.create_index("user_id", unique=True)

        logger.info("✓ Database indexes created")

    def get_all_collections(self) -> List[str]:
        """Get list of all collections in database."""
        db = self.get_db()
        return db.list_collection_names()

    def health_check(self) -> Dict[str, Any]:
        """
        Check MongoDB connection health.
        
        Returns:
            dict: Health check result
        """
        try:
            db = self.get_db()
            db.admin.command("ping")
            
            collections = db.list_collection_names()
            energy_logs_count = db.energy_logs.count_documents({})
            user_profiles_count = db.user_profiles.count_documents({})
            ai_insights_count = db.ai_insights.count_documents({})
            alerts_count = db.alerts.count_documents({})
            household_profiles_count = db.household_profiles.count_documents({})
            
            return {
                "status": "healthy",
                "database": "enersense",
                "collections": collections,
                "energy_logs_count": energy_logs_count,
                "user_profiles_count": user_profiles_count,
                "ai_insights_count": ai_insights_count,
                "alerts_count": alerts_count,
                "household_profiles_count": household_profiles_count,
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "database": "enersense",
            }


# Global database client instance
db_client = MongoDBClient()
