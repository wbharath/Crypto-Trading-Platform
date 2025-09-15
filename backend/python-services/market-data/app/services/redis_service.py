# app/services/redis_service.py
import json
import logging
from typing import Optional, Dict, Any, List
import redis.asyncio as redis
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisService:
    """Redis service for caching market data"""
    
    def __init__(self):
        self.redis_client = None
        self.connection_pool = None
    
    async def connect(self):
        """Establish Redis connection"""
        try:
            self.redis_client = redis.from_url(  # FIXED: Changed from aioredis.from_url
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                retry_on_timeout=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
    
    async def ping(self):
        """Test Redis connection"""
        if self.redis_client:
            return await self.redis_client.ping()
        return False
    
    # Price data methods
    async def set_price(self, symbol: str, price_data: Dict[str, Any], ttl: int = None):
        """Store price data for a symbol"""
        try:
            key = f"price:{symbol}"
            data = {
                **price_data,
                "timestamp": datetime.now().isoformat(),
                "cached_at": datetime.now().isoformat()
            }
            
            await self.redis_client.set(
                key, 
                json.dumps(data, default=str),
                ex=ttl or settings.price_cache_ttl
            )
            
            # Also store in a list for recent prices
            await self.redis_client.lpush(f"price_history:{symbol}", json.dumps(data, default=str))
            await self.redis_client.ltrim(f"price_history:{symbol}", 0, 99)  # Keep last 100 prices
            
        except Exception as e:
            logger.error(f"Failed to set price for {symbol}: {e}")
    
    async def get_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest price data for a symbol"""
        try:
            key = f"price:{symbol}"
            data = await self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            return None
    
    async def get_all_prices(self) -> Dict[str, Any]:
        """Get all cached prices"""
        try:
            keys = await self.redis_client.keys("price:*")
            prices = {}
            
            for key in keys:
                symbol = key.replace("price:", "")
                data = await self.redis_client.get(key)
                if data:
                    prices[symbol] = json.loads(data)
            
            return prices
            
        except Exception as e:
            logger.error(f"Failed to get all prices: {e}")
            return {}
    
    async def get_price_history(self, symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get price history for a symbol"""
        try:
            key = f"price_history:{symbol}"
            data = await self.redis_client.lrange(key, 0, limit - 1)
            
            return [json.loads(item) for item in data]
            
        except Exception as e:
            logger.error(f"Failed to get price history for {symbol}: {e}")
            return []
    
    # Market data methods
    async def set_market_data(self, symbol: str, market_data: Dict[str, Any], ttl: int = None):
        """Store comprehensive market data"""
        try:
            key = f"market:{symbol}"
            data = {
                **market_data,
                "cached_at": datetime.now().isoformat()
            }
            
            await self.redis_client.set(
                key,
                json.dumps(data, default=str),
                ex=ttl or settings.market_data_cache_ttl
            )
            
        except Exception as e:
            logger.error(f"Failed to set market data for {symbol}: {e}")
    
    async def get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get market data for a symbol"""
        try:
            key = f"market:{symbol}"
            data = await self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get market data for {symbol}: {e}")
            return None
    
    # Exchange data methods
    async def set_exchange_data(self, exchange: str, symbol: str, data: Dict[str, Any], ttl: int = None):
        """Store exchange-specific data"""
        try:
            key = f"exchange:{exchange}:{symbol}"
            await self.redis_client.set(
                key,
                json.dumps(data, default=str),
                ex=ttl or settings.price_cache_ttl
            )
            
        except Exception as e:
            logger.error(f"Failed to set exchange data for {exchange}:{symbol}: {e}")
    
    async def get_exchange_data(self, exchange: str, symbol: str) -> Optional[Dict[str, Any]]:
        """Get exchange-specific data"""
        try:
            key = f"exchange:{exchange}:{symbol}"
            data = await self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get exchange data for {exchange}:{symbol}: {e}")
            return None
    
    # Utility methods
    async def publish_price_update(self, symbol: str, price_data: Dict[str, Any]):
        """Publish price update to Redis pub/sub"""
        try:
            channel = f"price_updates:{symbol}"
            message = {
                "symbol": symbol,
                "data": price_data,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.redis_client.publish(channel, json.dumps(message, default=str))
            
            # Also publish to general channel
            await self.redis_client.publish("price_updates", json.dumps(message, default=str))
            
        except Exception as e:
            logger.error(f"Failed to publish price update for {symbol}: {e}")
    
    async def set_cache(self, key: str, value: Any, ttl: int = 3600):
        """Generic cache set method"""
        try:
            await self.redis_client.set(
                key,
                json.dumps(value, default=str),
                ex=ttl
            )
        except Exception as e:
            logger.error(f"Failed to set cache for {key}: {e}")
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """Generic cache get method"""
        try:
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get cache for {key}: {e}")
            return None
    
    async def delete_cache(self, key: str):
        """Delete cache entry"""
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Failed to delete cache for {key}: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis statistics"""
        try:
            info = await self.redis_client.info()
            
            # Count our specific keys
            price_keys = await self.redis_client.keys("price:*")
            market_keys = await self.redis_client.keys("market:*")
            exchange_keys = await self.redis_client.keys("exchange:*")
            
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "cached_prices": len(price_keys),
                "cached_market_data": len(market_keys),
                "cached_exchange_data": len(exchange_keys),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")
            return {}