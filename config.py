import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
    
    # Trading Configuration
    TRADING_MODE = os.getenv('TRADING_MODE', 'paper')
    DEFAULT_TRADE_AMOUNT = float(os.getenv('DEFAULT_TRADE_AMOUNT', 100))
    MAX_PORTFOLIO_RISK = float(os.getenv('MAX_PORTFOLIO_RISK', 0.02))
    STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', 0.05))
    TAKE_PROFIT_PERCENTAGE = float(os.getenv('TAKE_PROFIT_PERCENTAGE', 0.15))
    
    # Trading Pairs
    TRADING_PAIRS = os.getenv('TRADING_PAIRS', 'BTC/USDT,ETH/USDT,SOL/USDT,BNB/USDT').split(',')
    
    # Risk Management
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 500))
    MAX_OPEN_POSITIONS = int(os.getenv('MAX_OPEN_POSITIONS', 5))
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///trading.db')
    
    # Timeframes for analysis
    TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d']
    PRIMARY_TIMEFRAME = '15m'
    
    # ML Model Configuration
    MODEL_RETRAIN_INTERVAL = 24  # hours
    PREDICTION_CONFIDENCE_THRESHOLD = 0.55  # Lowered to allow more trades in paper mode
    
    # Technical Indicators Configuration
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    BB_PERIOD = 20
    BB_STD = 2
    
    # Backtesting
    BACKTEST_START_DATE = '2023-01-01'
    BACKTEST_INITIAL_CAPITAL = 10000

# Module-level constants for simple bot
INITIAL_CAPITAL = 10000
TRADING_MODE = os.getenv('TRADING_MODE', 'paper')
TRADING_PAIRS = os.getenv('TRADING_PAIRS', 'BTC/USDT,ETH/USDT,SOL/USDT').split(',')
POSITION_SIZE_PCT = 0.15  # 15% of capital per position (MORE aggressive)
STOP_LOSS_PCT = 0.04  # 4% stop loss (tighter)
TAKE_PROFIT_PCT = 0.10  # 10% take profit (quicker exits for faster turnover)
MAX_POSITIONS = 5  # Max 5 positions at once (MORE trades)
TRADING_CYCLE_MINUTES = 5  # Run cycle every 5 minutes (FASTER trading)

