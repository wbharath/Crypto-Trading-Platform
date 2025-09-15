# app/services/data_collector.py
import asyncio
import logging
from typing import Dict, List, Optional
import ccxt.async_support as ccxt
from datetime import datetime
import aiohttp

from app.core.config import settings
from app.services.redis_service import RedisService

logger = logging.getLogger(__name__)

class DataCollector:
    """Collects market data from multiple cryptocurrency exchanges"""
    
    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        self.exchanges = {}
        self.running = False
        self.tasks = []
    
    async def start(self):
        """Start the data collection service"""
        logger.info("Starting data collector...")
        
        # Initialize exchange connections
        await self._initialize_exchanges()
        
        # Start collection tasks
        self.running = True
        self.tasks = [
            asyncio.create_task(self._collect_prices_loop()),
            asyncio.create_task(self._collect_market_data_loop()),
        ]
        
        logger.info("Data collector started successfully")
    
    async def stop(self):
        """Stop the data collection service"""
        logger.info("Stopping data collector...")
        
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Close exchange connections
        await self._close_exchanges()
        
        logger.info("Data collector stopped")
    
    async def _initialize_exchanges(self):
        """Initialize cryptocurrency exchange connections"""
        logger.info("Initializing exchange connections...")
        
        exchange_configs = {
            'binance': {
                'class': ccxt.binance,
                'config': {
                    'apiKey': '',  # No API key needed for public data
                    'secret': '',
                    'sandbox': False,
                    'enableRateLimit': True,
                    'timeout': settings.exchange_request_timeout * 1000,
                }
            },
            'coinbasepro': {
                'class': ccxt.coinbasepro,
                'config': {
                    'apiKey': '',
                    'secret': '',
                    'passphrase': '',
                    'sandbox': False,
                    'enableRateLimit': True,
                    'timeout': settings.exchange_request_timeout * 1000,
                }
            },
            'kraken': {
                'class': ccxt.kraken,
                'config': {
                    'apiKey': '',
                    'secret': '',
                    'enableRateLimit': True,
                    'timeout': settings.exchange_request_timeout * 1000,
                }
            }
        }
        
        for exchange_name, config in exchange_configs.items():
            try:
                exchange = config['class'](config['config'])
                await exchange.load_markets()
                self.exchanges[exchange_name] = exchange
                logger.info(f"Successfully initialized {exchange_name} exchange")
                
            except Exception as e:
                logger.error(f"Failed to initialize {exchange_name} exchange: {e}")
                # Continue without this exchange
                continue
        
        if not self.exchanges:
            raise Exception("No exchanges could be initialized")
        
        logger.info(f"Initialized {len(self.exchanges)} exchanges")
    
    async def _close_exchanges(self):
        """Close all exchange connections"""
        for name, exchange in self.exchanges.items():
            try:
                await exchange.close()
                logger.info(f"Closed {name} exchange connection")
            except Exception as e:
                logger.error(f"Error closing {name} exchange: {e}")
    
    async def _collect_prices_loop(self):
        """Main loop for collecting price data"""
        logger.info("Starting price collection loop...")
        
        while self.running:
            try:
                await self._collect_all_prices()
                await asyncio.sleep(settings.price_update_interval)
                
            except Exception as e:
                logger.error(f"Error in price collection loop: {e}")
                await asyncio.sleep(5)  # Short delay before retry
    
    async def _collect_market_data_loop(self):
        """Main loop for collecting comprehensive market data"""
        logger.info("Starting market data collection loop...")
        
        while self.running:
            try:
                await self._collect_all_market_data()
                await asyncio.sleep(settings.market_data_update_interval)
                
            except Exception as e:
                logger.error(f"Error in market data collection loop: {e}")
                await asyncio.sleep(10)  # Longer delay for market data
    
    async def _collect_all_prices(self):
        """Collect prices from all exchanges for all symbols"""
        tasks = []
        
        for exchange_name, exchange in self.exchanges.items():
            for symbol in settings.default_symbols:
                task = asyncio.create_task(
                    self._collect_price_from_exchange(exchange_name, exchange, symbol)
                )
                tasks.append(task)
        
        if tasks:
            # Execute all price collection tasks concurrently
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _collect_price_from_exchange(self, exchange_name: str, exchange, symbol: str):
        """Collect price data from a specific exchange for a specific symbol"""
        try:
            # Get ticker data
            ticker = await exchange.fetch_ticker(symbol)
            
            price_data = {
                'exchange': exchange_name,
                'symbol': symbol,
                'price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['baseVolume'],
                'volume_quote': ticker['quoteVolume'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'change_24h': ticker['change'],
                'change_24h_percent': ticker['percentage'],
                'timestamp': datetime.now().isoformat(),
                'exchange_timestamp': ticker['timestamp']
            }
            
            # Store in Redis
            await self.redis_service.set_exchange_data(exchange_name, symbol, price_data)
            
            # Calculate and store best price across exchanges
            await self._update_best_price(symbol)
            
            logger.debug(f"Collected price for {symbol} from {exchange_name}: {ticker['last']}")
            
        except Exception as e:
            logger.error(f"Failed to collect price for {symbol} from {exchange_name}: {e}")
    
    async def _collect_all_market_data(self):
        """Collect comprehensive market data"""
        tasks = []
        
        for exchange_name, exchange in self.exchanges.items():
            for symbol in settings.default_symbols:
                task = asyncio.create_task(
                    self._collect_market_data_from_exchange(exchange_name, exchange, symbol)
                )
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _collect_market_data_from_exchange(self, exchange_name: str, exchange, symbol: str):
        """Collect comprehensive market data from a specific exchange"""
        try:
            # Get more detailed market data
            ticker = await exchange.fetch_ticker(symbol)
            
            # Try to get order book data
            try:
                order_book = await exchange.fetch_order_book(symbol, limit=5)
                bids = order_book['bids'][:5] if order_book['bids'] else []
                asks = order_book['asks'][:5] if order_book['asks'] else []
            except:
                bids, asks = [], []
            
            market_data = {
                'exchange': exchange_name,
                'symbol': symbol,
                'price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'spread': (ticker['ask'] - ticker['bid']) if ticker['ask'] and ticker['bid'] else 0,
                'volume_24h': ticker['baseVolume'],
                'volume_quote_24h': ticker['quoteVolume'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'open_24h': ticker['open'],
                'close_24h': ticker['close'],
                'change_24h': ticker['change'],
                'change_24h_percent': ticker['percentage'],
                'vwap': ticker.get('vwap'),
                'order_book': {
                    'bids': bids,
                    'asks': asks
                },
                'timestamp': datetime.now().isoformat(),
                'exchange_timestamp': ticker['timestamp']
            }
            
            # Store detailed market data
            await self.redis_service.set_market_data(f"{exchange_name}:{symbol}", market_data)
            
            logger.debug(f"Collected market data for {symbol} from {exchange_name}")
            
        except Exception as e:
            logger.error(f"Failed to collect market data for {symbol} from {exchange_name}: {e}")
    
    async def _update_best_price(self, symbol: str):
        """Calculate and store the best price across all exchanges"""
        try:
            best_bid = 0
            best_ask = float('inf')
            best_price_data = None
            exchange_prices = []
            
            # Get prices from all exchanges for this symbol
            for exchange_name in self.exchanges.keys():
                exchange_data = await self.redis_service.get_exchange_data(exchange_name, symbol)
                
                if exchange_data:
                    exchange_prices.append(exchange_data)
                    
                    # Track best bid (highest) and ask (lowest)
                    if exchange_data.get('bid', 0) > best_bid:
                        best_bid = exchange_data['bid']
                    
                    if exchange_data.get('ask', float('inf')) < best_ask:
                        best_ask = exchange_data['ask']
                        best_price_data = exchange_data
            
            if best_price_data:
                # Create consolidated price data
                avg_price = sum(p['price'] for p in exchange_prices) / len(exchange_prices)
                total_volume = sum(p.get('volume', 0) for p in exchange_prices)
                
                best_price = {
                    'symbol': symbol,
                    'price': avg_price,
                    'best_bid': best_bid,
                    'best_ask': best_ask,
                    'spread': best_ask - best_bid,
                    'volume_24h': total_volume,
                    'exchange_count': len(exchange_prices),
                    'exchanges': [p['exchange'] for p in exchange_prices],
                    'timestamp': datetime.now().isoformat()
                }
                
                # Store best price
                await self.redis_service.set_price(symbol, best_price)
                
                # Publish price update for WebSocket clients
                await self.redis_service.publish_price_update(symbol, best_price)
                
        except Exception as e:
            logger.error(f"Failed to update best price for {symbol}: {e}")
    
    async def get_supported_symbols(self, exchange_name: str) -> List[str]:
        """Get supported symbols for a specific exchange"""
        try:
            if exchange_name in self.exchanges:
                exchange = self.exchanges[exchange_name]
                markets = await exchange.load_markets()
                return list(markets.keys())
            return []
        except Exception as e:
            logger.error(f"Failed to get symbols for {exchange_name}: {e}")
            return []
    
    async def get_historical_data(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        """Get historical OHLCV data"""
        try:
            # Use the first available exchange for historical data
            exchange_name = list(self.exchanges.keys())[0]
            exchange = self.exchanges[exchange_name]
            
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            historical_data = []
            for candle in ohlcv:
                historical_data.append({
                    'timestamp': candle[0],
                    'datetime': datetime.fromtimestamp(candle[0] / 1000).isoformat(),
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            return []