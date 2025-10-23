import logging
import time
from datetime import datetime
import threading
from config import *
from src.data_fetcher import MarketDataFetcher
from src.technical_indicators import TechnicalIndicators

logger = logging.getLogger(__name__)

class SimpleTradingBot:
    def __init__(self):
        self.data_fetcher = MarketDataFetcher()
        self.capital = INITIAL_CAPITAL
        self.initial_capital = INITIAL_CAPITAL
        self.positions = {}  # {symbol: {'amount': 0.1, 'entry_price': 50000, 'stop_loss': 48000, 'take_profit': 55000}}
        self.trades = []
        self.running = False
        self.thread = None
        
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
        for symbol in list(self.positions.keys()):
            try:
                # Get current price
                df = self.data_fetcher.get_ohlcv(symbol, timeframe='1m', limit=1)
                if df is None or len(df) == 0 or df.empty:
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
                    
            except Exception as e:
                logger.error(f"Error checking SL/TP for {symbol}: {e}")
    
    def trading_cycle(self):
        """Main trading cycle"""
        try:
            logger.info(f"=== TRADING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            
            # Check existing positions for stop loss / take profit
            self.check_stop_loss_take_profit()
            
            # Analyze each trading pair
            for symbol in TRADING_PAIRS:
                try:
                    # Skip if we already have a position in this symbol
                    if symbol in self.positions:
                        logger.info(f"{symbol}: Already in position, skipping")
                        continue
                    
                    # Fetch data
                    df = self.data_fetcher.get_ohlcv(symbol, timeframe='15m', limit=100)
                    if df is None or len(df) < 50 or df.empty:
                        logger.warning(f"{symbol}: Not enough data")
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
                        
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {e}")
                    
            # Log portfolio status
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
            
            logger.info(f"Portfolio: ${total_value:.2f} | Profit: ${profit:.2f} ({profit_pct:.2f}%) | Positions: {len(self.positions)}")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
    
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
        
        # Run first cycle immediately
        self.trading_cycle()
        
        # Then run on schedule
        while self.running:
            try:
                time.sleep(TRADING_CYCLE_MINUTES * 60)
                if self.running:
                    self.trading_cycle()
            except Exception as e:
                logger.error(f"Error in bot loop: {e}")
                time.sleep(60)
    
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
        
        return {
            'running': self.running,
            'capital': self.capital,
            'total_value': total_value,
            'profit': profit,
            'profit_pct': profit_pct,
            'num_positions': len(self.positions),
            'num_trades': len(self.trades)
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

