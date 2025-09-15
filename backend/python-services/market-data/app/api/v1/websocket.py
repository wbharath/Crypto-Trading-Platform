# app/api/v1/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import asyncio
import logging
import json

from app.core.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

websocket_router = APIRouter()

async def get_websocket_manager() -> WebSocketManager:
    """Get WebSocket manager instance"""
    # This will be injected by the main app
    return WebSocketManager()

@websocket_router.websocket("/market-data")
async def websocket_market_data(websocket: WebSocket):
    """WebSocket endpoint for real-time market data streaming"""
    # Get WebSocket manager from app state
    websocket_manager = websocket.app.state.websocket_manager
    
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            await websocket_manager.handle_message(websocket, data)
            
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket_manager.disconnect(websocket)

@websocket_router.websocket("/price-feed")
async def websocket_price_feed(websocket: WebSocket):
    """WebSocket endpoint specifically for price updates"""
    websocket_manager = websocket.app.state.websocket_manager
    redis_service = websocket.app.state.redis_service
    
    await websocket_manager.connect(websocket)
    
    try:
        # Subscribe to all default symbols automatically
        from app.core.config import settings
        for symbol in settings.default_symbols:
            await websocket_manager.subscribe_to_symbol(websocket, symbol)
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            await websocket_manager.handle_message(websocket, data)
            
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Price feed WebSocket error: {e}")
        await websocket_manager.disconnect(websocket)

@websocket_router.websocket("/symbol/{symbol}")
async def websocket_symbol_specific(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for a specific symbol"""
    websocket_manager = websocket.app.state.websocket_manager
    
    await websocket_manager.connect(websocket)
    
    try:
        # Auto-subscribe to the specific symbol
        symbol = symbol.upper()
        await websocket_manager.subscribe_to_symbol(websocket, symbol)
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            await websocket_manager.handle_message(websocket, data)
            
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Symbol-specific WebSocket error for {symbol}: {e}")
        await websocket_manager.disconnect(websocket)