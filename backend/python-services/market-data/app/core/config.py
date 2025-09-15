# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Market Data Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database settings
    database_url: str = "postgresql://trading_user:trading_password@postgres:5432/trading_platform"
    
    # Redis settings
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0
    redis_url: str = f"redis://{redis_host}:{redis_port}/{redis_db}"
    
    # Exchange API settings
    exchanges: List[str] = ["binance", "coinbasepro", "kraken"]
    default_symbols: List[str] = [
        "BTC/USDT", "ETH/USDT", "ADA/USDT", "DOT/USDT", 
        "LINK/USDT", "SOL/USDT", "AVAX/USDT", "MATIC/USDT"
    ]
    
    # API Rate limiting
    api_calls_per_minute: int = 60
    exchange_request_timeout: int = 10
    
    # WebSocket settings
    max_websocket_connections: int = 100
    websocket_ping_interval: int = 30
    websocket_ping_timeout: int = 10
    
    # Data collection intervals (seconds)
    price_update_interval: int = 5
    market_data_update_interval: int = 30
    historical_data_update_interval: int = 300
    
    # Caching settings
    price_cache_ttl: int = 10  # seconds
    market_data_cache_ttl: int = 60  # seconds
    historical_cache_ttl: int = 3600  # 1 hour
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS settings
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_headers: List[str] = ["*"]
    
    # Environment specific overrides
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Environment-specific configurations
if os.getenv("ENVIRONMENT") == "development":
    settings.debug = True
    settings.log_level = "DEBUG"
elif os.getenv("ENVIRONMENT") == "production":
    settings.debug = False
    settings.log_level = "WARNING"