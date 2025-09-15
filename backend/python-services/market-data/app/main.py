# app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
import uvicorn
from typing import Dict, Any

from app.core.config import settings
from app.core.websocket_manager import WebSocketManager
from app.api.v1.endpoints import router as api_router
from app.api.v1.websocket import websocket_router
from app.services.redis_service import RedisService
from app.services.data_collector import DataCollector

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

# Global instances
redis_service = None
data_collector = None
websocket_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global redis_service, data_collector, websocket_manager
    
    logger.info("Starting Market Data Service...")
    
    try:
        # Initialize Redis connection
        redis_service = RedisService()
        await redis_service.connect()
        logger.info("Redis connection established")
        
        # Initialize WebSocket manager
        websocket_manager = WebSocketManager()
        
        # Initialize and start data collector
        data_collector = DataCollector(redis_service)
        await data_collector.start()
        logger.info("Data collector started")
        
        # Store instances in app state
        app.state.redis = redis_service
        app.state.websocket_manager = websocket_manager
        app.state.data_collector = data_collector
        
        logger.info("Market Data Service started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Shutting down Market Data Service...")
        
        if data_collector:
            await data_collector.stop()
            logger.info("Data collector stopped")
        
        if redis_service:
            await redis_service.disconnect()
            logger.info("Redis connection closed")
        
        logger.info("Market Data Service shutdown complete")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Real-time cryptocurrency market data service",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Include routers
app.include_router(api_router, prefix="/api/v1", tags=["market-data"])
app.include_router(websocket_router, prefix="/ws", tags=["websocket"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "endpoints": {
            "api": "/api/v1",
            "websocket": "/ws",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }
    
    try:
        # Check Redis connection
        if hasattr(app.state, 'redis') and app.state.redis:
            await app.state.redis.ping()
            health_status["redis"] = "connected"
        else:
            health_status["redis"] = "disconnected"
            health_status["status"] = "degraded"
        
        # Check data collector
        if hasattr(app.state, 'data_collector') and app.state.data_collector:
            health_status["data_collector"] = "running"
        else:
            health_status["data_collector"] = "stopped"
            health_status["status"] = "degraded"
        
        # Check WebSocket manager
        if hasattr(app.state, 'websocket_manager') and app.state.websocket_manager:
            connection_count = len(app.state.websocket_manager.active_connections)
            health_status["websocket_connections"] = connection_count
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    return health_status

@app.get("/info")
async def service_info():
    """Service information endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": "docker" if settings.redis_host == "redis" else "local",
        "supported_exchanges": settings.exchanges,
        "default_symbols": settings.default_symbols,
        "features": [
            "Real-time price streaming",
            "Historical data",
            "WebSocket connections",
            "Multiple exchange support",
            "Redis caching"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )