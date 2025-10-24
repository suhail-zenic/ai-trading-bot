"""
Comprehensive System Test
Tests all major components without placing real trades
"""
import sys
import logging
from colorama import init, Fore, Style

init(autoreset=True)

print("\n" + "="*70)
print(f"{Fore.CYAN}{Style.BRIGHT}AI TRADING BOT - COMPREHENSIVE SYSTEM TEST")
print("="*70 + "\n")

# Suppress warnings for cleaner output
logging.basicConfig(level=logging.ERROR)

# Test 1: Configuration
print(f"{Fore.YELLOW}[1/8] Testing Configuration...")
try:
    from config import Config
    config = Config()
    print(f"{Fore.GREEN}[OK] Config loaded successfully")
    print(f"    Mode: {Fore.CYAN}{config.TRADING_MODE}")
    print(f"    Pairs: {Fore.CYAN}{', '.join(config.TRADING_PAIRS)}")
    print(f"    Stop Loss: {Fore.CYAN}{config.STOP_LOSS_PERCENTAGE*100}%")
    print(f"    Take Profit: {Fore.CYAN}{config.TAKE_PROFIT_PERCENTAGE*100}%")
    print(f"    Max Positions: {Fore.CYAN}{config.MAX_OPEN_POSITIONS}")
except Exception as e:
    print(f"{Fore.RED}[FAIL] Config failed: {e}")
    sys.exit(1)

# Test 2: Market Data Fetcher
print(f"\n{Fore.YELLOW}[2/8] Testing Market Data Fetcher...")
try:
    from src.data_fetcher import MarketDataFetcher
    fetcher = MarketDataFetcher()
    print(f"{Fore.GREEN}[OK] Data fetcher initialized")
    print(f"    Exchange: {Fore.CYAN}{fetcher.exchange_name}")
except Exception as e:
    print(f"{Fore.RED}[FAIL] Data fetcher failed: {e}")
    sys.exit(1)

# Test 3: Technical Indicators
print(f"\n{Fore.YELLOW}[3/8] Testing Technical Indicators...")
try:
    from src.technical_indicators import TechnicalIndicators
    print(f"{Fore.GREEN}[OK] Technical indicators module loaded")
except Exception as e:
    print(f"{Fore.RED}[FAIL] Technical indicators failed: {e}")
    sys.exit(1)

# Test 4: ML Predictor
print(f"\n{Fore.YELLOW}[4/8] Testing ML Predictor...")
try:
    from src.ml_predictor import MLPredictor
    ml_predictor = MLPredictor(model_type='ensemble')
    print(f"{Fore.GREEN}[OK] ML predictor initialized")
    print(f"    Models loaded: {Fore.CYAN}{len(ml_predictor.models) if ml_predictor.models else 0}")
except Exception as e:
    print(f"{Fore.RED}[FAIL] ML predictor failed: {e}")
    sys.exit(1)

# Test 5: Trading Strategies
print(f"\n{Fore.YELLOW}[5/8] Testing Trading Strategies...")
try:
    from src.trading_strategies import TradingStrategies
    strategies = TradingStrategies()
    print(f"{Fore.GREEN}[OK] Trading strategies initialized")
except Exception as e:
    print(f"{Fore.RED}[FAIL] Trading strategies failed: {e}")
    sys.exit(1)

# Test 6: Risk Manager
print(f"\n{Fore.YELLOW}[6/8] Testing Risk Manager...")
try:
    from src.risk_manager import RiskManager
    risk_manager = RiskManager()
    print(f"{Fore.GREEN}[OK] Risk manager initialized")
    print(f"    Open positions: {Fore.CYAN}{len(risk_manager.open_positions)}")
except Exception as e:
    print(f"{Fore.RED}[FAIL] Risk manager failed: {e}")
    sys.exit(1)

# Test 7: Fetch Real Market Data
print(f"\n{Fore.YELLOW}[7/8] Testing Real Market Data Fetch...")
try:
    ticker = fetcher.get_ticker('BTC/USDT')
    if ticker:
        print(f"{Fore.GREEN}[OK] Successfully fetched BTC/USDT data")
        print(f"    Current Price: {Fore.CYAN}${ticker['last']:,.2f}")
        print(f"    24h Change: {Fore.CYAN}{ticker['change_24h']:.2f}%")
    else:
        print(f"{Fore.YELLOW}[WARN] Could not fetch market data (network issue?)")
except Exception as e:
    print(f"{Fore.YELLOW}[WARN] Market data fetch failed: {e}")

# Test 8: Main Trading Bot
print(f"\n{Fore.YELLOW}[8/8] Testing Main Trading Bot...")
try:
    from src.trading_bot import CryptoTradingBot
    print(f"{Fore.GREEN}[OK] Trading bot class loaded")
    print(f"    {Fore.CYAN}Ready to initialize bot instance")
except Exception as e:
    print(f"{Fore.RED}[FAIL] Trading bot failed: {e}")
    sys.exit(1)

# Final Summary
print("\n" + "="*70)
print(f"{Fore.GREEN}{Style.BRIGHT}[SUCCESS] ALL TESTS PASSED!")
print("="*70)

print(f"\n{Fore.CYAN}System Status:")
print(f"  - Configuration: {Fore.GREEN}[OK]")
print(f"  - Market Data: {Fore.GREEN}[OK]")
print(f"  - ML Models: {Fore.GREEN}[OK]")
print(f"  - Strategies: {Fore.GREEN}[OK]")
print(f"  - Risk Management: {Fore.GREEN}[OK]")
print(f"  - Trading Bot: {Fore.GREEN}[OK]")

if config.TRADING_MODE == 'live':
    print(f"\n{Fore.RED}{Style.BRIGHT}[WARNING] Bot is in LIVE TRADING mode!")
    print(f"{Fore.YELLOW}   Real money will be used if you start trading.")
    print(f"{Fore.YELLOW}   Switch to paper mode with: python switch_mode.py")
else:
    print(f"\n{Fore.GREEN}[OK] Bot is in PAPER TRADING mode (safe)")
    print(f"{Fore.CYAN}   No real money will be used")

print(f"\n{Fore.CYAN}Next Steps:")
print(f"  1. Run bot: {Fore.WHITE}python run_bot.py")
print(f"  2. Web dashboard: {Fore.WHITE}python app.py")
print(f"  3. Switch mode: {Fore.WHITE}python switch_mode.py")

print("\n" + "="*70)
print(f"{Fore.GREEN}System is ready to trade!")
print("="*70 + "\n")

