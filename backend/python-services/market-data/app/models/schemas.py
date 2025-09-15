from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TimeFrame(str, Enum):
    """Supported timeframes for historical data"""
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"

class PriceData(BaseModel):
    """Price data model"""
    symbol: str
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume_24h: Optional[float] = None
    change_24h: Optional[float] = None
    change_24h_percent: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    timestamp: datetime
    exchange: Optional[str] = None

class MarketData(BaseModel):
    """Comprehensive market data model"""
    symbol: str
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None
    volume_24h: Optional[float] = None
    volume_quote_24h: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    open_24h: Optional[float] = None
    close_24h: Optional[float] = None
    change_24h: Optional[float] = None
    change_24h_percent: Optional[float] = None
    vwap: Optional[float] = None
    timestamp: datetime
    exchange: str
    order_book: Optional[Dict[str, List]] = None

class CandlestickData(BaseModel):
    """OHLCV candlestick data model"""
    timestamp: int
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class HistoricalDataRequest(BaseModel):
    """Request model for historical data"""
    symbol: str = Field(..., description="Trading symbol (e.g., BTC/USDT)")
    timeframe: TimeFrame = Field(TimeFrame.ONE_HOUR, description="Timeframe for candles")
    limit: int = Field(100, ge=1, le=1000, description="Number of candles to return")
    start_date: Optional[datetime] = Field(None, description="Start date for historical data")
    end_date: Optional[datetime] = Field(None, description="End date for historical data")

class HistoricalDataResponse(BaseModel):
    """Response model for historical data"""
    symbol: str
    timeframe: str
    data: List[CandlestickData]
    count: int
    exchange: str

class PriceResponse(BaseModel):
    """Response model for price data"""
    symbol: str
    data: PriceData
    cached_at: Optional[datetime] = None

class MultiPriceResponse(BaseModel):
    """Response model for multiple price data"""
    prices: Dict[str, PriceData]
    count: int
    timestamp: datetime

class MarketDataResponse(BaseModel):
    """Response model for market data"""
    symbol: str
    data: MarketData
    cached_at: Optional[datetime] = None

class ExchangeInfo(BaseModel):
    """Exchange information model"""
    name: str
    status: str
    symbols: List[str]
    features: List[str]

class ServiceStats(BaseModel):
    """Service statistics model"""
    total_symbols: int
    active_exchanges: int
    cache_stats: Dict[str, Any]
    websocket_connections: int
    uptime_seconds: int

class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str
    symbol: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    timestamp: datetime

class SubscriptionRequest(BaseModel):
    """WebSocket subscription request"""
    type: str = Field(..., description="Message type (subscribe/unsubscribe)")
    symbol: str = Field(..., description="Symbol to subscribe/unsubscribe")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    timestamp: datetime
    status_code: int