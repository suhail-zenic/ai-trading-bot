"""
Simple CLI runner for the crypto trading bot
Run this directly to see detailed logs
"""
import sys
import logging
from logging.handlers import RotatingFileHandler
from src.trading_bot import CryptoTradingBot

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

if __name__ == "__main__":
    logger.info("="*80)
    logger.info("STARTING CRYPTO TRADING BOT - CLI MODE")
    logger.info("="*80)
    
    try:
        # Create and initialize bot
        bot = CryptoTradingBot()
        
        # Train models if not exist
        logger.info("Initializing ML models...")
        bot.initialize(quick=True)
        
        # Start trading (blocks until stopped)
        logger.info("Starting trading loop...")
        bot.start(interval_minutes=1)  # Run every 1 minute for testing
        
    except KeyboardInterrupt:
        logger.info("\n\nBot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

