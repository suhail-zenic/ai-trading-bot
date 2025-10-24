"""
Simple CLI runner for the crypto trading bot
Run this directly to see detailed logs
"""
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from src.trading_bot import CryptoTradingBot
from config import Config

# Setup detailed logging with rotation
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

logger = logging.getLogger(__name__)

def check_live_trading_safety():
    """Safety check for live trading mode"""
    config = Config()
    
    if config.TRADING_MODE != 'live':
        return True
    
    # Live trading safety checks
    print("\n" + "="*80)
    print("⚠️  LIVE TRADING MODE DETECTED ⚠️")
    print("="*80)
    print("\n⚠️  WARNING: This bot will place REAL orders using REAL money!")
    print("⚠️  Losses are REAL and PERMANENT!")
    print("\nCurrent Configuration:")
    print(f"  • Stop Loss: {config.STOP_LOSS_PERCENTAGE*100:.1f}%")
    print(f"  • Take Profit: {config.TAKE_PROFIT_PERCENTAGE*100:.1f}%")
    print(f"  • Max Positions: {config.MAX_OPEN_POSITIONS}")
    print(f"  • Trading Pairs: {', '.join(config.TRADING_PAIRS)}")
    
    # Check API keys
    if not config.BINANCE_API_KEY or not config.BINANCE_API_SECRET:
        print("\n❌ ERROR: API keys not configured!")
        print("Please set BINANCE_API_KEY and BINANCE_API_SECRET in .env")
        return False
    
    print("\n" + "="*80)
    print("Type 'START LIVE TRADING' to continue (or Ctrl+C to cancel):")
    print("="*80)
    
    try:
        confirmation = input("> ").strip()
        if confirmation != 'START LIVE TRADING':
            print("\n✓ Cancelled for safety")
            return False
        
        print("\n" + "="*80)
        print("🔴 LIVE TRADING MODE CONFIRMED - Using REAL money!")
        print("="*80 + "\n")
        return True
        
    except KeyboardInterrupt:
        print("\n\n✓ Cancelled by user")
        return False

if __name__ == "__main__":
    config = Config()
    
    logger.info("="*80)
    if config.TRADING_MODE == 'live':
        logger.warning("STARTING CRYPTO TRADING BOT - LIVE MODE (REAL MONEY!)")
    else:
        logger.info("STARTING CRYPTO TRADING BOT - PAPER MODE (Safe Simulation)")
    logger.info("="*80)
    
    # Safety check for live trading
    if not check_live_trading_safety():
        logger.info("Bot start cancelled")
        sys.exit(0)
    
    try:
        # Create and initialize bot
        bot = CryptoTradingBot()
        
        # Train models if not exist
        logger.info("Initializing ML models...")
        bot.initialize(quick=True)
        
        # Start trading (blocks until stopped)
        # Use config value for cycle time (30 min default from optimized settings)
        from config import TRADING_CYCLE_MINUTES
        logger.info("Starting trading loop...")
        bot.start(interval_minutes=TRADING_CYCLE_MINUTES)
        
    except KeyboardInterrupt:
        logger.info("\n\nBot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

