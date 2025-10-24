import time
import schedule
import logging
from datetime import datetime
from typing import Dict, List
import pandas as pd
from colorlog import ColoredFormatter

from config import Config
from src.data_fetcher import MarketDataFetcher
from src.technical_indicators import TechnicalIndicators
from src.ml_predictor import MLPredictor
from src.trading_strategies import TradingStrategies
from src.risk_manager import RiskManager

# Setup colored logging
def setup_logger():
    """Setup colored logger"""
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logging.getLogger(__name__)

logger = setup_logger()

class CryptoTradingBot:
    """Main AI-powered crypto trading bot"""
    
    def __init__(self):
        self.config = Config()
        self.data_fetcher = MarketDataFetcher()
        self.ml_predictor = MLPredictor(model_type='ensemble')
        self.strategies = TradingStrategies()
        self.risk_manager = RiskManager()
        
        self.is_running = False
        self.capital = self.config.DEFAULT_TRADE_AMOUNT * 100  # Initial capital
        
        logger.info("="*60)
        logger.info("AI CRYPTO TRADING BOT INITIALIZED")
        logger.info("="*60)
        logger.info(f"Trading Mode: {self.config.TRADING_MODE.upper()}")
        logger.info(f"Trading Pairs: {', '.join(self.config.TRADING_PAIRS)}")
        logger.info(f"Initial Capital: ${self.capital:,.2f}")
        logger.info("="*60)
    
    def initialize(self, quick: bool = False):
        """Initialize the bot by training ML models"""
        logger.info("Initializing bot - Training ML models...")
        
        # Use first symbol only for quick initialization
        symbols_to_train = [self.config.TRADING_PAIRS[0]] if quick else self.config.TRADING_PAIRS
        
        for symbol in symbols_to_train:
            try:
                logger.info(f"Fetching training data for {symbol}...")
                # Use less data for faster training
                limit = 300 if quick else 1000
                df = self.data_fetcher.get_ohlcv(symbol, '1h', limit=limit)
                
                if df.empty:
                    logger.warning(f"No data available for {symbol}")
                    continue
                
                # Add indicators
                df = TechnicalIndicators.add_all_indicators(df)
                
                # Train models
                logger.info(f"Training models for {symbol}...")
                results = self.ml_predictor.train(df)
                
                if results['status'] == 'success':
                    logger.info(f"[OK] Models trained successfully for {symbol}")
                    for model_name, metrics in results['models'].items():
                        if 'accuracy' in metrics:
                            logger.info(f"  {model_name}: {metrics['accuracy']:.2%} accuracy")
                
            except Exception as e:
                logger.error(f"Error initializing {symbol}: {e}")
        
        # Save models
        self.ml_predictor.save_models()
        logger.info("[OK] Initialization complete!")
    
    def analyze_symbol(self, symbol: str) -> Dict:
        """Analyze a single trading pair"""
        try:
            logger.info(f"Fetching data for {symbol}...")
            # Fetch latest data
            df = self.data_fetcher.get_ohlcv(symbol, self.config.PRIMARY_TIMEFRAME, limit=500)
            
            if df.empty:
                logger.warning(f"No data received for {symbol}")
                return {'symbol': symbol, 'status': 'error', 'message': 'No data'}
            
            logger.info(f"Adding indicators to {len(df)} candles...")
            # Add technical indicators
            df = TechnicalIndicators.add_all_indicators(df)
            
            # Get current price
            current_price = df['close'].iloc[-1]
            
            # Get ML prediction
            ml_prediction = self.ml_predictor.predict(df)
            
            # Get strategy signals
            trend_signal = self.strategies.trend_following_strategy(df)
            mean_rev_signal = self.strategies.mean_reversion_strategy(df)
            breakout_signal = self.strategies.breakout_strategy(df)
            
            # Get ML-enhanced signal
            enhanced_signal = self.strategies.ml_enhanced_strategy(df, ml_prediction)
            
            # Get market sentiment
            sentiment = self.data_fetcher.get_market_sentiment(symbol)
            
            # Get technical signal summary
            tech_summary = TechnicalIndicators.get_signal_summary(df)
            
            return {
                'symbol': symbol,
                'status': 'success',
                'current_price': current_price,
                'ml_prediction': ml_prediction,
                'enhanced_signal': enhanced_signal,
                'trend_signal': trend_signal,
                'mean_reversion_signal': mean_rev_signal,
                'breakout_signal': breakout_signal,
                'sentiment': sentiment,
                'technical_summary': tech_summary,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {'symbol': symbol, 'status': 'error', 'message': str(e)}
    
    def execute_trade(self, symbol: str, signal: str, confidence: float, current_price: float):
        """Execute a trade (paper or live)"""
        
        # Check if we should enter the trade
        risk_check = self.risk_manager.should_enter_trade(signal, confidence, current_price)
        
        if not risk_check['can_trade']:
            logger.warning(f"Trade blocked for {symbol}: {', '.join(risk_check['reasons'])}")
            return None
        
        # Calculate position size
        position_info = self.risk_manager.calculate_position_size(
            self.capital, current_price, self.config.STOP_LOSS_PERCENTAGE, confidence
        )
        
        if position_info['position_size'] == 0:
            logger.warning(f"Position size is 0 for {symbol}")
            return None
        
        # Determine side
        side = 'BUY' if signal in ['BUY', 'STRONG_BUY'] else 'SELL'
        
        logger.info("="*60)
        logger.info(f"EXECUTING {side} ORDER FOR {symbol}")
        logger.info(f"Price: ${current_price:.2f}")
        logger.info(f"Quantity: {position_info['position_size']:.6f}")
        logger.info(f"Value: ${position_info['position_value']:.2f}")
        logger.info(f"Confidence: {confidence:.2%}")
        logger.info(f"Stop Loss: ${position_info['recommended_stop_loss']:.2f}")
        logger.info(f"Take Profit: ${position_info['recommended_take_profit']:.2f}")
        logger.info("="*60)
        
        if self.config.TRADING_MODE == 'paper':
            # Paper trading
            position_id = self.risk_manager.add_position(
                symbol=symbol,
                side=side,
                entry_price=current_price,
                quantity=position_info['position_size'],
                stop_loss=position_info['recommended_stop_loss'],
                take_profit=position_info['recommended_take_profit']
            )
            
            logger.info(f"[OK] Paper trade executed - Position ID: {position_id}")
            return position_id
        
        else:
            # Live trading - execute real order on exchange
            logger.warning("="*60)
            logger.warning("[LIVE] LIVE TRADING MODE - PLACING REAL ORDER")
            logger.warning("="*60)
            
            # Place market order on exchange
            order_result = self.data_fetcher.place_market_order(
                symbol=symbol,
                side=side.lower(),
                amount=position_info['position_size']
            )
            
            if order_result and order_result.get('success'):
                # Track position in risk manager
                actual_price = order_result.get('average') or order_result.get('price') or current_price
                actual_amount = order_result.get('filled') or order_result.get('amount')
                
                position_id = self.risk_manager.add_position(
                    symbol=symbol,
                    side=side,
                    entry_price=actual_price,
                    quantity=actual_amount,
                    stop_loss=position_info['recommended_stop_loss'],
                    take_profit=position_info['recommended_take_profit']
                )
                
                logger.info(f"[OK] LIVE TRADE EXECUTED!")
                logger.info(f"  Order ID: {order_result.get('order_id')}")
                logger.info(f"  Actual Price: ${actual_price:.2f}")
                logger.info(f"  Actual Amount: {actual_amount:.6f}")
                logger.info(f"  Total Cost: ${order_result.get('cost', 0):.2f}")
                logger.info(f"  Position ID: {position_id}")
                
                return position_id
            else:
                error_msg = order_result.get('message', 'Unknown error') if order_result else 'No response'
                logger.error(f"[FAIL] Live order failed: {error_msg}")
                return None
    
    def monitor_positions(self):
        """Monitor and manage open positions"""
        if not self.risk_manager.open_positions:
            return
        
        logger.info(f"Monitoring {len(self.risk_manager.open_positions)} open positions...")
        
        for position_id, position in list(self.risk_manager.open_positions.items()):
            symbol = position['symbol']
            
            # Get current price
            ticker = self.data_fetcher.get_ticker(symbol)
            if not ticker:
                continue
            
            current_price = ticker['last']
            
            # Update P&L
            self.risk_manager.update_position_pnl(position_id, current_price)
            
            # Check exit conditions
            exit_check = self.risk_manager.check_exit_conditions(position_id, current_price)
            
            if exit_check['should_exit']:
                trade_result = self.risk_manager.close_position(
                    position_id, current_price, exit_check['reason']
                )
                
                if trade_result:
                    pnl = trade_result['pnl']
                    logger.info(f"Position closed: {symbol} - P&L: ${pnl:.2f} ({exit_check['reason']})")
            else:
                pnl = position['pnl']
                logger.debug(f"{symbol}: ${current_price:.2f} - P&L: ${pnl:.2f}")
    
    def trading_cycle(self):
        """Main trading cycle"""
        logger.info("\n" + "="*60)
        logger.info(f"TRADING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)
        
        # Check if models are trained, if not train them now
        if not self.ml_predictor.models:
            logger.info("Models not loaded - training now (one-time setup)...")
            try:
                self.initialize(quick=True)
            except Exception as e:
                logger.error(f"Error training models: {e}")
        
        # Monitor existing positions
        self.monitor_positions()
        
        # Analyze each trading pair
        for symbol in self.config.TRADING_PAIRS:
            logger.info(f"\n{'='*60}")
            logger.info(f"Analyzing {symbol}...")
            logger.info(f"{'='*60}")
            
            try:
                analysis = self.analyze_symbol(symbol)
                
                if analysis['status'] != 'success':
                    logger.error(f"Failed to analyze {symbol}: {analysis.get('message')}")
                    continue
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)
                continue
            
            # Get the enhanced signal (combines all strategies + ML)
            signal_data = analysis['enhanced_signal']
            signal = signal_data['signal']
            confidence = signal_data['confidence']
            
            logger.info(f"Signal: {signal} (Confidence: {confidence:.2%})")
            logger.info(f"ML Prediction: {analysis['ml_prediction']['signal']} "
                       f"({analysis['ml_prediction']['prediction']:.2%})")
            logger.info(f"Market Sentiment: {analysis['sentiment']['interpretation']} "
                       f"(Score: {analysis['sentiment']['sentiment_score']:.0f})")
            
            # Check if we should trade
            if signal in ['BUY', 'STRONG_BUY', 'SELL', 'STRONG_SELL']:
                if confidence >= self.config.PREDICTION_CONFIDENCE_THRESHOLD:
                    self.execute_trade(symbol, signal, confidence, analysis['current_price'])
                else:
                    logger.info(f"Signal confidence too low: {confidence:.2%}")
            else:
                logger.info("Holding - no strong signal")
        
        # Print portfolio summary
        self.print_portfolio_summary()
        
        logger.info("="*60 + "\n")
    
    def print_portfolio_summary(self):
        """Print current portfolio status"""
        current_prices = {}
        for symbol in self.config.TRADING_PAIRS:
            ticker = self.data_fetcher.get_ticker(symbol)
            if ticker:
                current_prices[symbol] = ticker['last']
        
        portfolio = self.risk_manager.get_portfolio_summary(current_prices)
        stats = self.risk_manager.get_performance_stats()
        
        logger.info("\n" + "-"*60)
        logger.info("PORTFOLIO SUMMARY")
        logger.info("-"*60)
        logger.info(f"Open Positions: {portfolio['open_positions']}")
        logger.info(f"Total Position Value: ${portfolio['total_position_value']:.2f}")
        logger.info(f"Unrealized P&L: ${portfolio['unrealized_pnl']:.2f}")
        logger.info(f"Daily P&L: ${portfolio['daily_pnl']:.2f}")
        logger.info(f"Risk Score: {portfolio['risk_score']:.0f}/100")
        
        if stats['total_trades'] > 0:
            logger.info(f"\nTotal Trades: {stats['total_trades']}")
            logger.info(f"Win Rate: {stats['win_rate']:.2%}")
            logger.info(f"Profit Factor: {stats['profit_factor']:.2f}")
            logger.info(f"Total P&L: ${stats['total_pnl']:.2f}")
        
        logger.info("-"*60)
    
    def start(self, interval_minutes: int = 30):
        """Start the trading bot"""
        logger.info(f"\nStarting trading bot (checking every {interval_minutes} minutes)...")
        logger.info("Press Ctrl+C to stop\n")
        
        self.is_running = True
        
        # Run first cycle immediately
        try:
            self.trading_cycle()
        except Exception as e:
            logger.error(f"Error in first trading cycle: {e}")
        
        # Schedule periodic cycles
        schedule.every(interval_minutes).minutes.do(self.trading_cycle)
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nStopping bot...")
            self.stop()
        except Exception as e:
            logger.error(f"Error in bot main loop: {e}")
            self.stop()
    
    def stop(self):
        """Stop the trading bot"""
        self.is_running = False
        
        # Close all positions
        logger.info("Closing all positions...")
        for position_id in list(self.risk_manager.open_positions.keys()):
            position = self.risk_manager.open_positions[position_id]
            ticker = self.data_fetcher.get_ticker(position['symbol'])
            if ticker:
                self.risk_manager.close_position(position_id, ticker['last'], 'Bot Stopped')
        
        # Print final stats
        logger.info("\n" + "="*60)
        logger.info("FINAL PERFORMANCE STATISTICS")
        logger.info("="*60)
        stats = self.risk_manager.get_performance_stats()
        
        for key, value in stats.items():
            if isinstance(value, float):
                logger.info(f"{key.replace('_', ' ').title()}: {value:.2f}")
            else:
                logger.info(f"{key.replace('_', ' ').title()}: {value}")
        
        logger.info("="*60)
        logger.info("Bot stopped successfully")


if __name__ == "__main__":
    bot = CryptoTradingBot()
    
    # Initialize and train models
    bot.initialize()
    
    # Start trading (30-60 min cycle recommended)
    bot.start(interval_minutes=30)

