import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from config import Config

logger = logging.getLogger(__name__)

class MarketDataFetcher:
    """Fetches real-time and historical crypto market data"""
    
    def __init__(self, exchange_name: str = 'auto'):
        self.config = Config()
        self.exchange_name = exchange_name
        self.exchange = self._initialize_exchange()
        
    def _initialize_exchange(self):
        """Initialize exchange connection with automatic fallback"""
        # Try exchanges in order - Binance first (works for most regions)
        exchanges_to_try = [
            ('binance', 'Binance'),
            ('kucoin', 'KuCoin'),
            ('okx', 'OKX'),
            ('bybit', 'Bybit'),
            ('kraken', 'Kraken'),
        ]
        
        # If specific exchange requested, try it first
        if self.exchange_name != 'auto' and self.exchange_name != 'binance':
            exchanges_to_try.insert(0, (self.exchange_name, self.exchange_name.title()))
        
        for exchange_id, exchange_name in exchanges_to_try:
            try:
                logger.info(f"Trying to connect to {exchange_name}...")
                exchange_class = getattr(ccxt, exchange_id)
                exchange = exchange_class({
                    'enableRateLimit': True,
                    'timeout': 10000,  # 10 second timeout
                    'options': {'defaultType': 'spot'}  # Use spot markets
                })
                
                # Quick test connection with timeout
                import signal
                def timeout_handler(signum, frame):
                    raise TimeoutError("Exchange connection timeout")
                
                # Test connection with 5 second timeout
                try:
                    exchange.load_markets()
                except:
                    # Just try to fetch ticker as backup test
                    exchange.fetch_ticker('BTC/USDT')
                
                self.exchange_name = exchange_id
                logger.info(f"✓ Successfully connected to {exchange_name}!")
                return exchange
                
            except Exception as e:
                error_msg = str(e)[:150]
                logger.warning(f"✗ {exchange_name} failed: {error_msg}")
                continue
        
        # If all fail, raise error
        logger.error("Failed to connect to any exchange! Check your internet connection.")
        raise Exception("Could not connect to any cryptocurrency exchange")
    
    def get_ohlcv(self, symbol: str, timeframe: str = '15m', 
                   limit: int = 500, since: Optional[int] = None) -> pd.DataFrame:
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe (e.g., '1m', '5m', '15m', '1h', '4h', '1d')
            limit: Number of candles to fetch
            since: Timestamp in milliseconds
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker information"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': ticker.get('last', 0),
                'bid': ticker.get('bid', 0),
                'ask': ticker.get('ask', 0),
                'volume': ticker.get('quoteVolume', 0),
                'baseVolume': ticker.get('baseVolume', 0),
                'percentage': ticker.get('percentage', 0),
                'change_24h': ticker.get('percentage', 0),
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None
    
    def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """Get order book data"""
        try:
            order_book = self.exchange.fetch_order_book(symbol, limit)
            return {
                'bids': order_book['bids'],
                'asks': order_book['asks'],
                'timestamp': order_book['timestamp']
            }
        except Exception as e:
            logger.error(f"Error fetching order book for {symbol}: {e}")
            return {'bids': [], 'asks': []}
    
    def get_recent_trades(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        """Get recent trades"""
        try:
            trades = self.exchange.fetch_trades(symbol, limit=limit)
            df = pd.DataFrame(trades)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df[['timestamp', 'price', 'amount', 'side']]
        except Exception as e:
            logger.error(f"Error fetching trades for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_multi_timeframe_data(self, symbol: str, timeframes: List[str] = None) -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple timeframes"""
        if timeframes is None:
            timeframes = self.config.TIMEFRAMES
        
        multi_data = {}
        for tf in timeframes:
            try:
                df = self.get_ohlcv(symbol, tf, limit=500)
                if not df.empty:
                    multi_data[tf] = df
                    logger.info(f"Fetched {len(df)} candles for {symbol} on {tf}")
            except Exception as e:
                logger.error(f"Error fetching {tf} data for {symbol}: {e}")
        
        return multi_data
    
    def get_market_sentiment(self, symbol: str) -> Dict:
        """Calculate market sentiment from order book and recent trades"""
        try:
            order_book = self.get_order_book(symbol, limit=50)
            trades = self.get_recent_trades(symbol, limit=100)
            
            # Calculate bid/ask pressure
            total_bids = sum([bid[1] for bid in order_book['bids']])
            total_asks = sum([ask[1] for ask in order_book['asks']])
            
            bid_ask_ratio = total_bids / (total_asks + 1e-10)
            
            # Calculate buy/sell pressure from trades
            if not trades.empty:
                buy_volume = trades[trades['side'] == 'buy']['amount'].sum()
                sell_volume = trades[trades['side'] == 'sell']['amount'].sum()
                buy_sell_ratio = buy_volume / (sell_volume + 1e-10)
            else:
                buy_sell_ratio = 1.0
            
            # Overall sentiment score (0-100, 50 is neutral)
            sentiment_score = min(100, max(0, 50 * (bid_ask_ratio + buy_sell_ratio)))
            
            return {
                'sentiment_score': sentiment_score,
                'bid_ask_ratio': bid_ask_ratio,
                'buy_sell_ratio': buy_sell_ratio,
                'interpretation': self._interpret_sentiment(sentiment_score)
            }
            
        except Exception as e:
            logger.error(f"Error calculating sentiment for {symbol}: {e}")
            return {'sentiment_score': 50, 'interpretation': 'neutral'}
    
    def _interpret_sentiment(self, score: float) -> str:
        """Interpret sentiment score"""
        if score >= 70:
            return 'very_bullish'
        elif score >= 55:
            return 'bullish'
        elif score >= 45:
            return 'neutral'
        elif score >= 30:
            return 'bearish'
        else:
            return 'very_bearish'

