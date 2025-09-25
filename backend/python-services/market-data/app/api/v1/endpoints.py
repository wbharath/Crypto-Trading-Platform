from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.models.schemas import (
    PriceResponse, MultiPriceResponse, MarketDataResponse,
    HistoricalDataRequest, HistoricalDataResponse, 
    ServiceStats, ExchangeInfo, ErrorResponse
)
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

def get_redis_service(request: Request):
    """Dependency to get Redis service from app state"""
    return request.app.state.redis

def get_data_collector(request: Request):
    """Dependency to get Data Collector from app state"""
    return request.app.state.data_collector

def get_websocket_manager(request: Request):
    """Dependency to get WebSocket Manager from app state"""
    return request.app.state.websocket_manager

@router.get("/price/{symbol}", response_model=PriceResponse)
async def get_price(
    symbol: str,
    redis_service = Depends(get_redis_service)
):
    """Get current price for a specific symbol"""
    try:
        # Validate symbol format
        symbol = symbol.upper()
        
        # Get price from Redis cache
        price_data = await redis_service.get_price(symbol)
        
        if not price_data:
            raise HTTPException(
                status_code=404,
                detail=f"Price data not found for symbol {symbol}"
            )
        
        return PriceResponse(
            symbol=symbol,
            data=price_data,
            cached_at=price_data.get("cached_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/price/{base}/{quote}", response_model=PriceResponse)
async def get_price_by_pair(
    base: str,
    quote: str,
    redis_service = Depends(get_redis_service)
):
    """Get current price for a specific trading pair (e.g., /price/BTC/USDT)"""
    try:
        # Construct full symbol from base and quote currencies
        symbol = f"{base.upper()}/{quote.upper()}"
        
        # Get price from Redis cache
        price_data = await redis_service.get_price(symbol)
        
        if not price_data:
            raise HTTPException(
                status_code=404,
                detail=f"Price data not found for {symbol}"
            )
        
        return PriceResponse(
            symbol=symbol,
            data=price_data,
            cached_at=price_data.get("cached_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price for {base}/{quote}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/prices", response_model=MultiPriceResponse)
async def get_all_prices(
    symbols: Optional[str] = None,
    redis_service = Depends(get_redis_service)
):
    """Get current prices for all symbols or specified symbols"""
    try:
        if symbols:
            # Parse comma-separated symbols
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
            prices = {}
            
            for symbol in symbol_list:
                price_data = await redis_service.get_price(symbol)
                if price_data:
                    prices[symbol] = price_data
        else:
            # Get all cached prices
            prices = await redis_service.get_all_prices()
        
        return MultiPriceResponse(
            prices=prices,
            count=len(prices),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error getting prices: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/market-data/{symbol}", response_model=MarketDataResponse)
async def get_market_data(
    symbol: str,
    exchange: Optional[str] = None,
    redis_service = Depends(get_redis_service)
):
    """Get comprehensive market data for a specific symbol"""
    try:
        symbol = symbol.upper()
        
        if exchange:
            # Get data from specific exchange
            key = f"{exchange.lower()}:{symbol}"
            market_data = await redis_service.get_market_data(key)
        else:
            # Get aggregated market data
            market_data = await redis_service.get_market_data(symbol)
        
        if not market_data:
            raise HTTPException(
                status_code=404,
                detail=f"Market data not found for {symbol}" + 
                       (f" on {exchange}" if exchange else "")
            )
        
        return MarketDataResponse(
            symbol=symbol,
            data=market_data,
            cached_at=market_data.get("cached_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/historical-data", response_model=HistoricalDataResponse)
async def get_historical_data(
    request: HistoricalDataRequest,
    data_collector = Depends(get_data_collector)
):
    """Get historical OHLCV data for a symbol"""
    try:
        symbol = request.symbol.upper()
        
        # Get historical data from data collector
        historical_data = await data_collector.get_historical_data(
            symbol=symbol,
            timeframe=request.timeframe.value,
            limit=request.limit
        )
        
        if not historical_data:
            raise HTTPException(
                status_code=404,
                detail=f"Historical data not found for {symbol}"
            )
        
        # Use first available exchange for response
        exchange_name = list(data_collector.exchanges.keys())[0] if data_collector.exchanges else "unknown"
        
        return HistoricalDataResponse(
            symbol=symbol,
            timeframe=request.timeframe.value,
            data=historical_data,
            count=len(historical_data),
            exchange=exchange_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting historical data for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/symbols")
async def get_supported_symbols(
    exchange: Optional[str] = None,
    data_collector = Depends(get_data_collector)
):
    """Get list of supported trading symbols"""
    try:
        if exchange:
            # Get symbols for specific exchange
            symbols = await data_collector.get_supported_symbols(exchange.lower())
        else:
            # Return default symbols
            symbols = settings.default_symbols
        
        return {
            "symbols": symbols,
            "count": len(symbols),
            "exchange": exchange or "all",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/exchanges", response_model=List[ExchangeInfo])
async def get_exchanges(
    data_collector = Depends(get_data_collector)
):
    """Get information about supported exchanges"""
    try:
        exchanges_info = []
        
        for exchange_name, exchange in data_collector.exchanges.items():
            try:
                # Get basic exchange info
                symbols = await data_collector.get_supported_symbols(exchange_name)
                
                exchange_info = ExchangeInfo(
                    name=exchange_name,
                    status="active",
                    symbols=symbols[:10],  # Return first 10 symbols for brevity
                    features=["spot_trading", "real_time_data", "historical_data"]
                )
                exchanges_info.append(exchange_info)
                
            except Exception as e:
                logger.warning(f"Could not get info for exchange {exchange_name}: {e}")
                continue
        
        return exchanges_info
        
    except Exception as e:
        logger.error(f"Error getting exchanges info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats", response_model=ServiceStats)
async def get_service_stats(
    redis_service = Depends(get_redis_service),
    websocket_manager = Depends(get_websocket_manager),
    data_collector = Depends(get_data_collector)
):
    """Get service statistics and health information"""
    try:
        # Get Redis stats
        redis_stats = await redis_service.get_stats()
        
        # Get WebSocket stats
        ws_stats = websocket_manager.get_connection_stats()
        
        # Calculate uptime (simplified)
        uptime_seconds = 3600  # Placeholder - you could track actual start time
        
        stats = ServiceStats(
            total_symbols=len(settings.default_symbols),
            active_exchanges=len(data_collector.exchanges),
            cache_stats=redis_stats,
            websocket_connections=ws_stats["total_connections"],
            uptime_seconds=uptime_seconds
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting service stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/price-history/{symbol}")
async def get_price_history(
    symbol: str,
    limit: int = 20,
    redis_service = Depends(get_redis_service)
):
    """Get recent price history for a symbol"""
    try:
        symbol = symbol.upper()
        
        if limit > 100:
            limit = 100  # Cap at 100 records
        
        price_history = await redis_service.get_price_history(symbol, limit)
        
        return {
            "symbol": symbol,
            "history": price_history,
            "count": len(price_history),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting price history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/exchange-data/{exchange}/{symbol}")
async def get_exchange_specific_data(
    exchange: str,
    symbol: str,
    redis_service = Depends(get_redis_service)
):
    """Get data from a specific exchange for a symbol"""
    try:
        symbol = symbol.upper()
        exchange = exchange.lower()
        
        exchange_data = await redis_service.get_exchange_data(exchange, symbol)
        
        if not exchange_data:
            raise HTTPException(
                status_code=404,
                detail=f"Data not found for {symbol} on {exchange}"
            )
        
        return {
            "exchange": exchange,
            "symbol": symbol,
            "data": exchange_data,
            "timestamp": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exchange data for {exchange}:{symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": "Market Data Service",
        "timestamp": datetime.now()
    }