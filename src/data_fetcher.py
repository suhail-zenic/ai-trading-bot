import ccxt
import pandas as pd
from datetime import datetime
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
        
        # Set API credentials if available (for authenticated requests like balance)
        if self.config.BINANCE_API_KEY and self.config.BINANCE_API_SECRET:
            self.exchange.apiKey = self.config.BINANCE_API_KEY
            self.exchange.secret = self.config.BINANCE_API_SECRET
            logger.info("API credentials configured for authenticated requests")
        
        # Configure proxy if set (for accessing Binance from restricted regions)
        from config import HTTP_PROXY, HTTPS_PROXY
        if HTTP_PROXY or HTTPS_PROXY:
            proxies = {}
            if HTTP_PROXY:
                proxies['http'] = HTTP_PROXY
            if HTTPS_PROXY:
                proxies['https'] = HTTPS_PROXY
            self.exchange.proxies = proxies
            logger.info(f"Proxy configured for exchange access")
        
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
                    'timeout': 15000,  # 15 second timeout
                    'options': {
                        'defaultType': 'spot',
                        'recvWindow': 10000  # 10 second receive window
                    }
                })
                
                # Test connection with a simple ticker fetch (faster than load_markets)
                try:
                    ticker = exchange.fetch_ticker('BTC/USDT')
                    if ticker and 'last' in ticker:
                        self.exchange_name = exchange_id
                        logger.info(f"[OK] Successfully connected to {exchange_name}!")
                        return exchange
                except Exception as test_error:
                    logger.warning(f"[FAIL] {exchange_name} connection test failed: {str(test_error)[:100]}")
                    continue
                
            except Exception as e:
                error_msg = str(e)[:150]
                logger.warning(f"[FAIL] {exchange_name} failed: {error_msg}")
                continue
        
        # If all fail, raise error
        logger.error("Failed to connect to any exchange! Check your internet connection.")
        raise Exception("Could not connect to any cryptocurrency exchange")
    
    def get_ohlcv(self, symbol: str, timeframe: str = '15m', 
                   limit: int = 500, since: Optional[int] = None, retries: int = 2) -> pd.DataFrame:
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe (e.g., '1m', '5m', '15m', '1h', '4h', '1d')
            limit: Number of candles to fetch
            since: Timestamp in milliseconds
            retries: Number of retry attempts
            
        Returns:
            DataFrame with OHLCV data
        """
        import time
        
        for attempt in range(retries + 1):
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
                
                if not ohlcv or len(ohlcv) == 0:
                    logger.warning(f"Empty OHLCV data for {symbol}")
                    return pd.DataFrame()
                
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                return df
                
            except ccxt.NetworkError as e:
                if attempt < retries:
                    logger.warning(f"Network error fetching {symbol}, retrying ({attempt + 1}/{retries})...")
                    time.sleep(2)  # Wait 2 seconds before retry
                else:
                    logger.error(f"Network error fetching OHLCV for {symbol} after {retries} retries: {e}")
                    return pd.DataFrame()
                    
            except ccxt.RateLimitExceeded as e:
                logger.warning(f"Rate limit exceeded for {symbol}, waiting...")
                time.sleep(5)  # Wait longer for rate limits
                if attempt >= retries:
                    logger.error(f"Rate limit exceeded for {symbol} after retries")
                    return pd.DataFrame()
                    
            except Exception as e:
                logger.error(f"Error fetching OHLCV for {symbol}: {e}")
                return pd.DataFrame()
        
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
    
    def get_account_balance(self, currency: str = 'USDT') -> Dict:
        """
        Fetch account balance from exchange
        
        Args:
            currency: Currency to fetch balance for (default: USDT)
            
        Returns:
            Dictionary with balance info or None if error
        """
        try:
            # Fetch balance from exchange
            balance = self.exchange.fetch_balance()
            
            if currency in balance:
                return {
                    'currency': currency,
                    'total': balance[currency].get('total', 0),
                    'free': balance[currency].get('free', 0),
                    'used': balance[currency].get('used', 0),
                    'timestamp': datetime.now()
                }
            else:
                logger.warning(f"Currency {currency} not found in balance")
                return {
                    'currency': currency,
                    'total': 0,
                    'free': 0,
                    'used': 0,
                    'timestamp': datetime.now()
                }
        except Exception as e:
            logger.error(f"Error fetching balance for {currency}: {e}")
            return None
    
    def place_market_order(self, symbol: str, side: str, amount: float, test_mode: bool = False) -> Dict:
        """
        Place a market order on the exchange
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            side: 'buy' or 'sell'
            amount: Amount in base currency (e.g., 0.001 BTC)
            test_mode: If True, use test order endpoint (Binance only)
            
        Returns:
            Order result dictionary or None if error
        """
        try:
            if not self.config.BINANCE_API_KEY or not self.config.BINANCE_API_SECRET:
                logger.error("API credentials not configured - cannot place orders")
                return None
            
            logger.info(f"{'TEST ' if test_mode else ''}Placing {side.upper()} market order: {amount} {symbol}")
            
            # Use test order for safety (Binance only)
            if test_mode and hasattr(self.exchange, 'create_test_order'):
                order = self.exchange.create_test_order(symbol, 'market', side, amount)
                logger.info(f"[OK] Test order successful: {order}")
            else:
                order = self.exchange.create_market_order(symbol, side, amount)
                logger.info(f"[OK] Live order placed: {order.get('id', 'N/A')}")
            
            return {
                'success': True,
                'order_id': order.get('id'),
                'symbol': symbol,
                'side': side,
                'type': 'market',
                'amount': order.get('amount', amount),
                'filled': order.get('filled', 0),
                'price': order.get('price', 0),
                'average': order.get('average', 0),
                'cost': order.get('cost', 0),
                'status': order.get('status', 'unknown'),
                'timestamp': datetime.now(),
                'raw_order': order
            }
            
        except ccxt.InsufficientFunds as e:
            logger.error(f"Insufficient funds for {side} {amount} {symbol}: {e}")
            return {'success': False, 'error': 'insufficient_funds', 'message': str(e)}
        except ccxt.InvalidOrder as e:
            logger.error(f"Invalid order for {symbol}: {e}")
            return {'success': False, 'error': 'invalid_order', 'message': str(e)}
        except Exception as e:
            logger.error(f"Error placing {side} order for {symbol}: {e}")
            return {'success': False, 'error': 'unknown', 'message': str(e)}
    
    def place_limit_order(self, symbol: str, side: str, amount: float, price: float, test_mode: bool = False) -> Dict:
        """
        Place a limit order on the exchange
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            side: 'buy' or 'sell'
            amount: Amount in base currency
            price: Limit price
            test_mode: If True, use test order endpoint
            
        Returns:
            Order result dictionary or None if error
        """
        try:
            if not self.config.BINANCE_API_KEY or not self.config.BINANCE_API_SECRET:
                logger.error("API credentials not configured - cannot place orders")
                return None
            
            logger.info(f"{'TEST ' if test_mode else ''}Placing {side.upper()} limit order: {amount} {symbol} @ ${price}")
            
            if test_mode and hasattr(self.exchange, 'create_test_order'):
                order = self.exchange.create_test_order(symbol, 'limit', side, amount, price)
                logger.info(f"[OK] Test limit order successful")
            else:
                order = self.exchange.create_limit_order(symbol, side, amount, price)
                logger.info(f"[OK] Live limit order placed: {order.get('id', 'N/A')}")
            
            return {
                'success': True,
                'order_id': order.get('id'),
                'symbol': symbol,
                'side': side,
                'type': 'limit',
                'amount': order.get('amount', amount),
                'price': price,
                'status': order.get('status', 'open'),
                'timestamp': datetime.now(),
                'raw_order': order
            }
            
        except Exception as e:
            logger.error(f"Error placing limit order for {symbol}: {e}")
            return {'success': False, 'error': str(e)}
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an open order"""
        try:
            self.exchange.cancel_order(order_id, symbol)
            logger.info(f"[OK] Order {order_id} cancelled for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """Get all open orders"""
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []

