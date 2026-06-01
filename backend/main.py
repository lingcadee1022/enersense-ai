"""
FastAPI main application module for EnerSense AI backend.

Initializes and configures:
- FastAPI application
- CORS middleware for Flutter mobile app
- MongoDB connection
- API routers
- Logging
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import routers
from api import sensor, live_usage, history, insights, alerts
from db.mongo import db_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan: startup and shutdown.
    
    Startup:
    - Connect to MongoDB
    - Initialize database
    
    Shutdown:
    - Close MongoDB connection
    """
    # Startup
    logger.info("🚀 Starting EnerSense AI backend...")
    try:
        db_client.connect()
        health = db_client.health_check()
        logger.info(f"Database health: {health}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down EnerSense AI backend...")
    db_client.disconnect()


# ==================== APP INITIALIZATION ====================

app = FastAPI(
    title="EnerSense AI Backend",
    description="IoT energy monitoring system with AI insights",
    version="1.0.0",
    lifespan=lifespan,
)

# ==================== CORS CONFIGURATION ====================

# Allow CORS for Flutter mobile app and web dashboard
cors_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
    "http://192.168.1.1",
    "*",  # Allow all origins in development (restrict in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("✓ CORS middleware configured")

# ==================== ROUTER REGISTRATION ====================

# Routers already include the /api/v1 prefix.
app.include_router(sensor.router)
app.include_router(live_usage.router)
app.include_router(history.router)
app.include_router(insights.router)
app.include_router(alerts.router)

logger.info("✓ API routers registered")

# ==================== ROOT ENDPOINT ====================

@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint for health check.
    
    Response:
    {
        "project": "EnerSense AI",
        "status": "running",
        "version": "1.0.0"
    }
    """
    return {
        "project": "EnerSense AI",
        "status": "running",
        "version": "1.0.0",
        "message": "Welcome to EnerSense AI Backend"
    }


# ==================== HEALTH CHECK ENDPOINT ====================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns:
    - API status
    - Database status
    - Collections count
    - System uptime
    """
    try:
        db_health = db_client.health_check()
        
        return {
            "status": "healthy",
            "api": "running",
            "database": db_health,
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# ==================== READY ENDPOINT ====================

@app.get("/ready", tags=["Health"])
async def ready():
    """
    Readiness probe endpoint for Kubernetes/Docker.
    
    Returns 200 if service is ready to accept traffic.
    """
    try:
        # Check database connectivity
        db_health = db_client.health_check()
        if db_health.get("status") != "healthy":
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"ready": False, "reason": "Database not ready"}
            )
        
        return {"ready": True, "status": "service_ready"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"ready": False, "reason": str(e)}
        )


# ==================== API DOCUMENTATION ====================

@app.get("/docs-custom", tags=["Documentation"])
async def custom_docs():
    """
    Custom API documentation.
    """
    return {
        "title": "EnerSense AI Backend API",
        "version": "1.0.0",
        "description": "IoT energy monitoring system with ML-powered insights",
        "endpoints": {
            "sensor": {
                "POST /api/v1/sensor-data": "Receive ESP32 sensor data",
                "POST /api/v1/sensor-data/batch": "Receive batch of sensor readings"
            },
            "usage": {
                "GET /api/v1/live-usage": "Get latest sensor reading"
            },
            "history": {
                "GET /api/v1/history": "Get historical energy logs (query: hours or days)",
                "GET /api/v1/history/summary": "Get summary statistics"
            },
            "insights": {
                "GET /api/v1/insights": "Generate AI insights",
                "POST /api/v1/insights/train-profile": "Train user profile",
                "GET /api/v1/insights/profile": "Get user profile"
            },
            "health": {
                "GET /": "Root endpoint",
                "GET /health": "Comprehensive health check",
                "GET /ready": "Readiness probe"
            }
        },
        "database": "MongoDB (enersense)",
        "collections": ["energy_logs", "user_profiles", "ai_insights"],
        "features": [
            "Real-time sensor data ingestion",
            "Historical data analysis",
            "Behavior pattern learning",
            "Anomaly detection",
            "Cost estimation",
            "AI-powered insights"
        ]
    }


# ==================== ERROR HANDLERS ====================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": "Endpoint not found",
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("ENVIRONMENT") == "development" else "An error occurred"
        }
    )


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    logger.info(f"Starting server at {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
