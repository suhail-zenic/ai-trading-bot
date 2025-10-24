import logging
import time
from datetime import datetime
import threading
import sys
from logging.handlers import RotatingFileHandler
from config import *
from src.data_fetcher import MarketDataFetcher
from src.technical_indicators import TechnicalIndicators

# Configure logging with immediate flush and rotation
# Rotation: Max 10 MB per file, keep 5 backup files = 50 MB total
rotating_handler = RotatingFileHandler(
    'trading_bot.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5,           # Keep 5 old files
    mode='a'
)
rotating_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        rotating_handler
    ]
)

# Force immediate log flushing
for handler in logging.root.handlers:
    handler.flush = lambda: handler.stream.flush() if hasattr(handler, 'stream') else None
    if hasattr(handler, 'stream'):
        handler.stream.reconfigure(line_buffering=True) if hasattr(handler.stream, 'reconfigure') else None

logger = logging.getLogger(__name__)
logger.info("="*60)
logger.info("SimpleTradingBot module loaded")
logger.info("="*60)

class SimpleTradingBot:
    def __init__(self):
        logger.info("Initializing SimpleTradingBot...")
        try:
            self.data_fetcher = MarketDataFetcher()
            logger.info("MarketDataFetcher initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MarketDataFetcher: {e}", exc_info=True)
            raise
        
        # Try to fetch real balance from Binance
        self.initial_capital = INITIAL_CAPITAL  # Fallback value
        self.capital = INITIAL_CAPITAL
        
        if TRADING_MODE == 'live':
            logger.info("Live mode detected - fetching real balance from Binance...")
            balance_info = self.data_fetcher.get_account_balance('USDT')
            
            if balance_info and balance_info['free'] > 0:
                real_balance = balance_info['free']
                logger.info(f"✅ Real Binance balance fetched: {real_balance:.2f} USDT")
                logger.info(f"   Total: {balance_info['total']:.2f} USDT")
                logger.info(f"   Free: {balance_info['free']:.2f} USDT")
                logger.info(f"   Used: {balance_info['used']:.2f} USDT")
                
                # Use real balance instead of .env value
                self.initial_capital = real_balance
                self.capital = real_balance
                
                logger.info(f"🚀 Bot will trade with REAL balance: ${real_balance:.2f}")
            else:
                logger.warning(f"⚠️ Could not fetch real balance, using .env value: ${INITIAL_CAPITAL:.2f}")
                logger.warning("   Make sure API key has 'Enable Reading' permission")
        else:
            logger.info(f"Paper mode - using simulated balance: ${INITIAL_CAPITAL:.2f}")
            
        self.positions = {}  # {symbol: {'amount': 0.1, 'entry_price': 50000, 'stop_loss': 48000, 'take_profit': 55000}}
        self.trades = []
        self.running = False
        self.thread = None
        self.last_heartbeat = datetime.now()
        logger.info(f"Bot initialized with ${self.capital:.2f} capital")
        
    def get_trading_signal(self, df, symbol):
        """Simple but effective trading strategy using RSI, MACD, and Bollinger Bands"""
        try:
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Get indicators
            rsi = latest['rsi']
            macd = latest['macd']
            signal = latest['macd_signal']
            bb_upper = latest['bb_upper']
            bb_lower = latest['bb_lower']
            price = latest['close']
            
            # BUY signals (ULTRA AGGRESSIVE for fast profits)
            buy_signals = 0
            if rsi < 52:  # Buy when RSI just below neutral
                buy_signals += 1
            if rsi < 40:  # Extra signal if more oversold
                buy_signals += 1
            if macd > signal:  # MACD positive (no crossover needed)
                buy_signals += 2  # Give more weight
            if price <= bb_lower * 1.05:  # Near lower band (5% tolerance)
                buy_signals += 1
                
            # SELL signals (ULTRA AGGRESSIVE for quick exits)
            sell_signals = 0
            if rsi > 48:  # Sell when RSI just above neutral
                sell_signals += 1
            if rsi > 60:  # Extra signal if more overbought
                sell_signals += 1
            if macd < signal:  # MACD negative (no crossover needed)
                sell_signals += 2  # Give more weight
            if price >= bb_upper * 0.95:  # Near upper band (5% tolerance)
                sell_signals += 1
            
            # Decision - only need 2 signals for very active trading
            if buy_signals >= 2:
                return 'BUY', latest['close']
            elif sell_signals >= 2:
                return 'SELL', latest['close']
            else:
                return 'HOLD', latest['close']
                
        except Exception as e:
            logger.error(f"Error getting signal for {symbol}: {e}")
            return 'HOLD', 0
    
    def execute_buy(self, symbol, price):
        """Execute a buy order"""
        try:
            # Calculate position size (use POSITION_SIZE_PCT of available capital)
            position_value = self.capital * POSITION_SIZE_PCT
            amount = position_value / price
            
            # Set stop loss and take profit
            stop_loss = price * (1 - STOP_LOSS_PCT)
            take_profit = price * (1 + TAKE_PROFIT_PCT)
            
            # Record position
            self.positions[symbol] = {
                'amount': amount,
                'entry_price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'entry_time': datetime.now()
            }
            
            # Update capital
            self.capital -= position_value
            
            # Record trade
            trade = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'type': 'BUY',
                'price': price,
                'amount': amount,
                'value': position_value
            }
            self.trades.append(trade)
            
            logger.info(f"BUY {symbol} - Amount: {amount:.4f} @ ${price:.2f} | SL: ${stop_loss:.2f} | TP: ${take_profit:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error executing buy for {symbol}: {e}")
            return False
    
    def execute_sell(self, symbol, price):
        """Execute a sell order"""
        try:
            if symbol not in self.positions:
                return False
                
            position = self.positions[symbol]
            amount = position['amount']
            entry_price = position['entry_price']
            
            # Calculate P&L
            position_value = amount * price
            entry_value = amount * entry_price
            profit = position_value - entry_value
            profit_pct = (profit / entry_value) * 100
            
            # Update capital
            self.capital += position_value
            
            # Record trade
            trade = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'type': 'SELL',
                'price': price,
                'amount': amount,
                'value': position_value,
                'profit': profit,
                'profit_pct': profit_pct
            }
            self.trades.append(trade)
            
            # Remove position
            del self.positions[symbol]
            
            logger.info(f"SELL {symbol} - Amount: {amount:.4f} @ ${price:.2f} | Profit: ${profit:.2f} ({profit_pct:.2f}%)")
            return True
            
        except Exception as e:
            logger.error(f"Error executing sell for {symbol}: {e}")
            return False
    
    def check_stop_loss_take_profit(self):
        """Check if any positions hit stop loss or take profit"""
        if not self.positions:
            logger.info("No open positions to check")
            return
            
        for symbol in list(self.positions.keys()):
            try:
                # Get current price
                df = self.data_fetcher.get_ohlcv(symbol, timeframe='1m', limit=1)
                if df is None or len(df) == 0 or df.empty:
                    logger.warning(f"Could not fetch price for {symbol} SL/TP check")
                    continue
                    
                current_price = df.iloc[-1]['close']
                position = self.positions[symbol]
                
                # Check stop loss
                if current_price <= position['stop_loss']:
                    logger.warning(f"STOP LOSS triggered for {symbol} @ ${current_price:.2f}")
                    self.execute_sell(symbol, current_price)
                    
                # Check take profit
                elif current_price >= position['take_profit']:
                    logger.info(f"TAKE PROFIT triggered for {symbol} @ ${current_price:.2f}")
                    self.execute_sell(symbol, current_price)
                else:
                    # Log current status
                    entry_pct = ((current_price - position['entry_price']) / position['entry_price']) * 100
                    logger.info(f"{symbol}: ${current_price:.2f} ({entry_pct:+.2f}%) | SL: ${position['stop_loss']:.2f} | TP: ${position['take_profit']:.2f}")
                
                # Small delay between checks
                time.sleep(0.3)
                    
            except Exception as e:
                logger.error(f"Error checking SL/TP for {symbol}: {e}", exc_info=True)
    
    def trading_cycle(self):
        """Main trading cycle with timeout protection"""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Trading cycle timeout - exceeded 5 minutes")
        
        try:
            # Set a 5-minute timeout for the entire cycle (longer than cycle interval to be safe)
            # This prevents the cycle from hanging indefinitely
            if hasattr(signal, 'SIGALRM'):  # Unix-like systems
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(300)  # 5 minutes timeout
            
            logger.info(f"=== TRADING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            
            # Check existing positions for stop loss / take profit
            logger.info("Checking existing positions for SL/TP...")
            self.check_stop_loss_take_profit()
            
            # Analyze each trading pair
            logger.info(f"Analyzing {len(TRADING_PAIRS)} trading pairs...")
            for symbol in TRADING_PAIRS:
                try:
                    # Skip if we already have a position in this symbol
                    if symbol in self.positions:
                        logger.info(f"{symbol}: Already in position, skipping")
                        continue
                    
                    # Fetch data with timeout
                    logger.debug(f"Fetching data for {symbol}...")
                    df = self.data_fetcher.get_ohlcv(symbol, timeframe='15m', limit=100)
                    
                    if df is None or len(df) < 50 or df.empty:
                        logger.warning(f"{symbol}: Not enough data (got {len(df) if df is not None else 0} candles)")
                        continue
                    
                    # Add indicators
                    df = TechnicalIndicators.add_all_indicators(df)
                    
                    # Get trading signal
                    signal, price = self.get_trading_signal(df, symbol)
                    
                    logger.info(f"{symbol}: Signal={signal}, Price=${price:.2f}, RSI={df.iloc[-1]['rsi']:.1f}")
                    
                    # Execute trades based on signal
                    if signal == 'BUY' and len(self.positions) < MAX_POSITIONS:
                        self.execute_buy(symbol, price)
                    elif signal == 'SELL' and symbol in self.positions:
                        self.execute_sell(symbol, price)
                    
                    # Small delay between pairs to respect rate limits
                    time.sleep(0.5)
                        
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)
                    continue
                    
            # Log portfolio status
            logger.info("Calculating portfolio status...")
            total_value = self.capital
            for symbol, pos in self.positions.items():
                try:
                    df = self.data_fetcher.get_ohlcv(symbol, timeframe='1m', limit=1)
                    if df is not None and len(df) > 0 and not df.empty:
                        current_price = df.iloc[-1]['close']
                        total_value += pos['amount'] * current_price
                except Exception as e:
                    logger.warning(f"Error getting current price for {symbol}: {e}")
                    pass
                    
            profit = total_value - self.initial_capital
            profit_pct = (profit / self.initial_capital) * 100
            
            logger.info(f"Portfolio: ${total_value:.2f} | Profit: ${profit:.2f} ({profit_pct:.2f}%) | Positions: {len(self.positions)}")
            logger.info("=== CYCLE COMPLETE ===")
            
            # Update heartbeat
            self.last_heartbeat = datetime.now()
            
        except TimeoutError as e:
            logger.error(f"Trading cycle timeout: {e}")
            logger.error("Cycle took too long - skipping to next cycle")
            self.last_heartbeat = datetime.now()
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)
            self.last_heartbeat = datetime.now()
        finally:
            # Cancel the alarm
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            # Flush logs to ensure they're written
            for handler in logging.root.handlers:
                if hasattr(handler, 'flush'):
                    handler.flush()
    
    def run(self):
        """Main bot loop"""
        logger.info("=" * 60)
        logger.info("STREAMLINED TRADING BOT STARTED")
        logger.info("=" * 60)
        logger.info(f"Trading Mode: {TRADING_MODE}")
        logger.info(f"Trading Pairs: {', '.join(TRADING_PAIRS)}")
        logger.info(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
        logger.info(f"Cycle Interval: {TRADING_CYCLE_MINUTES} minutes")
        logger.info("=" * 60)
        
        self.running = True
        cycle_count = 0
        
        # Run first cycle immediately with timeout protection
        try:
            logger.info("Starting first trading cycle...")
            self.trading_cycle()
            cycle_count += 1
        except Exception as e:
            logger.error(f"Error in first trading cycle: {e}", exc_info=True)
        
        # Then run on schedule
        while self.running:
            try:
                # Sleep in smaller intervals to allow for faster shutdown
                sleep_time = TRADING_CYCLE_MINUTES * 60
                elapsed = 0
                while elapsed < sleep_time and self.running:
                    time.sleep(min(10, sleep_time - elapsed))  # Check every 10 seconds
                    elapsed += 10
                
                if self.running:
                    cycle_count += 1
                    logger.info(f"Starting trading cycle #{cycle_count}...")
                    self.trading_cycle()
                    logger.info(f"Trading cycle #{cycle_count} completed successfully")
                    
            except KeyboardInterrupt:
                logger.info("Bot stopping due to keyboard interrupt...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in bot loop (cycle #{cycle_count}): {e}", exc_info=True)
                logger.info("Waiting 60 seconds before next attempt...")
                time.sleep(60)
        
        logger.info("Bot has been stopped gracefully")
    
    def start(self):
        """Start the bot in a separate thread"""
        if not self.running:
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            logger.info("Bot thread started")
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        logger.info("Bot stopping...")
    
    def get_status(self):
        """Get current bot status"""
        total_value = self.capital
        
        for symbol, pos in self.positions.items():
            try:
                df = self.data_fetcher.get_ohlcv(symbol, timeframe='1m', limit=1)
                if df is not None and len(df) > 0 and not df.empty:
                    current_price = df.iloc[-1]['close']
                    total_value += pos['amount'] * current_price
            except:
                pass
        
        profit = total_value - self.initial_capital
        profit_pct = (profit / self.initial_capital) * 100
        
        # Calculate time since last heartbeat
        time_since_heartbeat = (datetime.now() - self.last_heartbeat).total_seconds()
        is_healthy = time_since_heartbeat < 600  # Consider unhealthy if no heartbeat for 10 minutes
        
        return {
            'running': self.running,
            'capital': self.capital,
            'total_value': total_value,
            'profit': profit,
            'profit_pct': profit_pct,
            'num_positions': len(self.positions),
            'num_trades': len(self.trades),
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'is_healthy': is_healthy,
            'seconds_since_heartbeat': time_since_heartbeat
        }
    
    def get_positions(self):
        """Get current positions with live P&L"""
        positions_list = []
        
        for symbol, pos in self.positions.items():
            try:
                df = self.data_fetcher.get_ohlcv(symbol, timeframe='1m', limit=1)
                if df is not None and len(df) > 0 and not df.empty:
                    current_price = df.iloc[-1]['close']
                    current_value = pos['amount'] * current_price
                    entry_value = pos['amount'] * pos['entry_price']
                    profit = current_value - entry_value
                    profit_pct = (profit / entry_value) * 100
                    
                    positions_list.append({
                        'symbol': symbol,
                        'amount': pos['amount'],
                        'entry_price': pos['entry_price'],
                        'current_price': current_price,
                        'profit': profit,
                        'profit_pct': profit_pct,
                        'stop_loss': pos['stop_loss'],
                        'take_profit': pos['take_profit'],
                        'entry_time': pos['entry_time'].isoformat()
                    })
            except Exception as e:
                logger.error(f"Error getting position info for {symbol}: {e}")
        
        return positions_list
    
    def get_trades(self):
        """Get trade history"""
        return self.trades[-50:]  # Last 50 trades

