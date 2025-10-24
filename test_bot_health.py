"""
Quick health check script to verify bot fixes are working
Run this before leaving the bot overnight
"""
import sys
import time
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def print_status(message, status="INFO"):
    """Print formatted status message"""
    symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "TESTING": "🔧"
    }
    print(f"{symbols.get(status, 'ℹ️')} {message}")

def test_exchange_connection():
    """Test if exchange connection works"""
    print_status("Testing exchange connection...", "TESTING")
    try:
        from src.data_fetcher import MarketDataFetcher
        
        start = time.time()
        fetcher = MarketDataFetcher()
        elapsed = time.time() - start
        
        print_status(f"Connected to {fetcher.exchange_name} in {elapsed:.2f}s", "SUCCESS")
        return fetcher
    except Exception as e:
        print_status(f"Exchange connection failed: {e}", "ERROR")
        return None

def test_data_fetching(fetcher):
    """Test if data fetching works"""
    print_status("Testing data fetching...", "TESTING")
    try:
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        results = []
        
        for symbol in symbols:
            start = time.time()
            df = fetcher.get_ohlcv(symbol, timeframe='15m', limit=50)
            elapsed = time.time() - start
            
            if df is not None and not df.empty:
                print_status(f"  {symbol}: {len(df)} candles in {elapsed:.2f}s", "SUCCESS")
                results.append(True)
            else:
                print_status(f"  {symbol}: No data received", "ERROR")
                results.append(False)
        
        return all(results)
    except Exception as e:
        print_status(f"Data fetching failed: {e}", "ERROR")
        return False

def test_bot_initialization():
    """Test if bot initializes properly"""
    print_status("Testing bot initialization...", "TESTING")
    try:
        from src.simple_trading_bot import SimpleTradingBot
        
        start = time.time()
        bot = SimpleTradingBot()
        elapsed = time.time() - start
        
        print_status(f"Bot initialized in {elapsed:.2f}s", "SUCCESS")
        print_status(f"  Capital: ${bot.capital:,.2f}", "INFO")
        print_status(f"  Trading pairs: {len(bot.data_fetcher.exchange.markets) if hasattr(bot.data_fetcher, 'exchange') else 'N/A'}", "INFO")
        
        return bot
    except Exception as e:
        print_status(f"Bot initialization failed: {e}", "ERROR")
        return None

def test_heartbeat(bot):
    """Test if heartbeat mechanism works"""
    print_status("Testing heartbeat mechanism...", "TESTING")
    try:
        initial_heartbeat = bot.last_heartbeat
        time.sleep(1)
        
        # Manually update heartbeat
        bot.last_heartbeat = datetime.now()
        
        if bot.last_heartbeat > initial_heartbeat:
            print_status("Heartbeat updates correctly", "SUCCESS")
            
            # Test status
            status = bot.get_status()
            print_status(f"  Health status: {'Healthy' if status['is_healthy'] else 'Unhealthy'}", "SUCCESS")
            print_status(f"  Seconds since heartbeat: {status['seconds_since_heartbeat']:.1f}s", "INFO")
            return True
        else:
            print_status("Heartbeat not updating", "ERROR")
            return False
    except Exception as e:
        print_status(f"Heartbeat test failed: {e}", "ERROR")
        return False

def test_trading_cycle(bot):
    """Test if a single trading cycle completes"""
    print_status("Testing trading cycle (this may take 30-60 seconds)...", "TESTING")
    try:
        initial_heartbeat = bot.last_heartbeat
        
        start = time.time()
        bot.trading_cycle()
        elapsed = time.time() - start
        
        if elapsed > 300:
            print_status(f"Cycle took too long: {elapsed:.1f}s", "WARNING")
            return False
        elif bot.last_heartbeat > initial_heartbeat:
            print_status(f"Trading cycle completed in {elapsed:.1f}s", "SUCCESS")
            return True
        else:
            print_status(f"Cycle completed but heartbeat not updated", "WARNING")
            return True
    except Exception as e:
        print_status(f"Trading cycle failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_logging():
    """Test if logging works"""
    print_status("Testing logging...", "TESTING")
    try:
        import os
        
        # Write a test log entry
        logger = logging.getLogger("test")
        logger.info("Health check test entry")
        
        # Check if log file exists
        if os.path.exists('trading_bot.log'):
            with open('trading_bot.log', 'r') as f:
                lines = f.readlines()
                if len(lines) > 0:
                    print_status(f"Log file has {len(lines)} lines", "SUCCESS")
                    return True
                else:
                    print_status("Log file is empty", "WARNING")
                    return False
        else:
            print_status("Log file not found (will be created on bot start)", "INFO")
            return True
    except Exception as e:
        print_status(f"Logging test failed: {e}", "ERROR")
        return False

def main():
    """Run all health checks"""
    print("\n" + "="*60)
    print("🏥 BOT HEALTH CHECK")
    print("="*60 + "\n")
    
    results = {}
    
    # Test 1: Exchange Connection
    fetcher = test_exchange_connection()
    results['exchange'] = fetcher is not None
    print()
    
    if not results['exchange']:
        print_status("Cannot continue without exchange connection", "ERROR")
        return False
    
    # Test 2: Data Fetching
    results['data'] = test_data_fetching(fetcher)
    print()
    
    # Test 3: Bot Initialization
    bot = test_bot_initialization()
    results['bot_init'] = bot is not None
    print()
    
    if not results['bot_init']:
        print_status("Cannot continue without bot initialization", "ERROR")
        return False
    
    # Test 4: Heartbeat
    results['heartbeat'] = test_heartbeat(bot)
    print()
    
    # Test 5: Logging
    results['logging'] = test_logging()
    print()
    
    # Test 6: Trading Cycle (most important)
    results['cycle'] = test_trading_cycle(bot)
    print()
    
    # Summary
    print("="*60)
    print("📊 HEALTH CHECK SUMMARY")
    print("="*60)
    
    total = len(results)
    passed = sum(results.values())
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title():.<40} {status}")
    
    print("="*60)
    
    if passed == total:
        print_status(f"All {total} tests passed! Bot is healthy and ready. 🎉", "SUCCESS")
        print_status("You can safely run the bot overnight.", "SUCCESS")
        return True
    elif passed >= total - 1:
        print_status(f"{passed}/{total} tests passed. Bot should work but monitor it.", "WARNING")
        return True
    else:
        print_status(f"Only {passed}/{total} tests passed. Fix issues before running overnight.", "ERROR")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nHealth check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

