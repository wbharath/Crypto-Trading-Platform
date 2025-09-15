# app/core/websocket_manager.py
import json
import logging
from typing import Dict, Set, List
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time market data streaming"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.symbol_subscriptions: Dict[str, Set[WebSocket]] = {}
        self.connection_metadata: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            
            # Store connection metadata
            self.connection_metadata[websocket] = {
                "connected_at": datetime.now(),
                "subscriptions": set(),
                "message_count": 0
            }
            
            logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
            
            # Send welcome message
            await self.send_personal_message(websocket, {
                "type": "connection_established",
                "message": "Connected to Market Data Service",
                "timestamp": datetime.now().isoformat(),
                "available_symbols": settings.default_symbols
            })
            
        except Exception as e:
            logger.error(f"Error accepting WebSocket connection: {e}")
            await self.disconnect(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect and clean up a WebSocket connection"""
        try:
            # Remove from active connections
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            
            # Remove from all symbol subscriptions
            if websocket in self.connection_metadata:
                subscriptions = self.connection_metadata[websocket].get("subscriptions", set())
                for symbol in subscriptions:
                    if symbol in self.symbol_subscriptions:
                        self.symbol_subscriptions[symbol].discard(websocket)
                        if not self.symbol_subscriptions[symbol]:
                            del self.symbol_subscriptions[symbol]
            
            # Remove metadata
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]
            
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
            
        except Exception as e:
            logger.error(f"Error during WebSocket disconnect: {e}")
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message, default=str))
            
            # Update message count
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["message_count"] += 1
                
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            await self.disconnect(websocket)
    
    async def broadcast_to_all(self, message: Dict):
        """Broadcast a message to all connected WebSocket clients"""
        if not self.active_connections:
            return
        
        disconnected = []
        message_json = json.dumps(message, default=str)
        
        for websocket in self.active_connections:
            try:
                await websocket.send_text(message_json)
                
                # Update message count
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]["message_count"] += 1
                    
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            await self.disconnect(websocket)
    
    async def broadcast_to_symbol_subscribers(self, symbol: str, message: Dict):
        """Broadcast a message to all clients subscribed to a specific symbol"""
        if symbol not in self.symbol_subscriptions:
            return
        
        subscribers = self.symbol_subscriptions[symbol].copy()
        disconnected = []
        message_json = json.dumps(message, default=str)
        
        for websocket in subscribers:
            try:
                await websocket.send_text(message_json)
                
                # Update message count
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]["message_count"] += 1
                    
            except Exception as e:
                logger.error(f"Error broadcasting to symbol subscriber: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            await self.disconnect(websocket)
    
    async def subscribe_to_symbol(self, websocket: WebSocket, symbol: str):
        """Subscribe a WebSocket connection to a specific symbol"""
        try:
            # Initialize symbol subscription set if needed
            if symbol not in self.symbol_subscriptions:
                self.symbol_subscriptions[symbol] = set()
            
            # Add WebSocket to symbol subscriptions
            self.symbol_subscriptions[symbol].add(websocket)
            
            # Update connection metadata
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["subscriptions"].add(symbol)
            
            logger.info(f"WebSocket subscribed to {symbol}. Subscribers: {len(self.symbol_subscriptions[symbol])}")
            
            # Send confirmation
            await self.send_personal_message(websocket, {
                "type": "subscription_confirmed",
                "symbol": symbol,
                "message": f"Subscribed to {symbol}",
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to symbol {symbol}: {e}")
            return False
    
    async def unsubscribe_from_symbol(self, websocket: WebSocket, symbol: str):
        """Unsubscribe a WebSocket connection from a specific symbol"""
        try:
            # Remove from symbol subscriptions
            if symbol in self.symbol_subscriptions:
                self.symbol_subscriptions[symbol].discard(websocket)
                
                # Remove empty subscription sets
                if not self.symbol_subscriptions[symbol]:
                    del self.symbol_subscriptions[symbol]
            
            # Update connection metadata
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["subscriptions"].discard(symbol)
            
            logger.info(f"WebSocket unsubscribed from {symbol}")
            
            # Send confirmation
            await self.send_personal_message(websocket, {
                "type": "unsubscription_confirmed",
                "symbol": symbol,
                "message": f"Unsubscribed from {symbol}",
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error unsubscribing from symbol {symbol}: {e}")
            return False
    
    async def handle_message(self, websocket: WebSocket, data: str):
        """Handle incoming WebSocket messages"""
        try:
            message = json.loads(data)
            message_type = message.get("type")
            
            if message_type == "subscribe":
                symbol = message.get("symbol")
                if symbol:
                    await self.subscribe_to_symbol(websocket, symbol)
                else:
                    await self.send_personal_message(websocket, {
                        "type": "error",
                        "message": "Symbol required for subscription",
                        "timestamp": datetime.now().isoformat()
                    })
            
            elif message_type == "unsubscribe":
                symbol = message.get("symbol")
                if symbol:
                    await self.unsubscribe_from_symbol(websocket, symbol)
                else:
                    await self.send_personal_message(websocket, {
                        "type": "error",
                        "message": "Symbol required for unsubscription",
                        "timestamp": datetime.now().isoformat()
                    })
            
            elif message_type == "ping":
                await self.send_personal_message(websocket, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_type == "get_subscriptions":
                subscriptions = list(self.connection_metadata.get(websocket, {}).get("subscriptions", set()))
                await self.send_personal_message(websocket, {
                    "type": "subscriptions",
                    "subscriptions": subscriptions,
                    "timestamp": datetime.now().isoformat()
                })
            
            else:
                await self.send_personal_message(websocket, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now().isoformat()
                })
                
        except json.JSONDecodeError:
            await self.send_personal_message(websocket, {
                "type": "error",
                "message": "Invalid JSON format",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send_personal_message(websocket, {
                "type": "error",
                "message": "Internal server error",
                "timestamp": datetime.now().isoformat()
            })
    
    def get_connection_stats(self) -> Dict:
        """Get statistics about WebSocket connections"""
        total_subscriptions = sum(len(subs) for subs in self.symbol_subscriptions.values())
        
        return {
            "total_connections": len(self.active_connections),
            "total_subscriptions": total_subscriptions,
            "subscribed_symbols": list(self.symbol_subscriptions.keys()),
            "connections_per_symbol": {
                symbol: len(subs) for symbol, subs in self.symbol_subscriptions.items()
            }
        }
    
    async def broadcast_price_update(self, symbol: str, price_data: Dict):
        """Broadcast price update to symbol subscribers"""
        message = {
            "type": "price_update",
            "symbol": symbol,
            "data": price_data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast_to_symbol_subscribers(symbol, message)