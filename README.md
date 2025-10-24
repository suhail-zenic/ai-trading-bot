# AI Crypto Trading Bot

A sophisticated AI-powered cryptocurrency trading bot with machine learning predictions, technical analysis, and comprehensive risk management.

## ✨ Key Features

- 🤖 **Machine Learning** - Ensemble models (Random Forest + Gradient Boosting)
- 📊 **Technical Analysis** - 20+ indicators (RSI, MACD, Bollinger Bands, etc.)
- 🎯 **Multi-Strategy** - Trend following, mean reversion, breakout strategies
- 🛡️ **Risk Management** - Stop loss, take profit, position sizing, daily limits
- 📄 **Paper Trading** - Safe simulation mode for testing
- 💰 **Live Trading** - Real order execution on Binance
- 🔄 **Easy Mode Switching** - Interactive switcher with safety confirmations
- 📈 **Web Dashboard** - Real-time monitoring and control
- 🌐 **Multiple Exchanges** - Binance, KuCoin, OKX, Bybit, Kraken

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-trading-tool

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file (or copy from `ENV_TEMPLATE.txt`):

```bash
# Trading Mode
TRADING_MODE=paper  # Start with paper mode!

# Capital
INITIAL_CAPITAL=10000

# API Keys (for live trading only)
BINANCE_API_KEY=
BINANCE_API_SECRET=

# Risk Management (Optimized Settings)
STOP_LOSS_PCT=0.015      # 1.5%
TAKE_PROFIT_PCT=0.04     # 4%
MAX_POSITIONS=2          # Max 2 trades

# Trading Config
TRADING_PAIRS=BTC/USDT,ETH/USDT
TRADING_CYCLE_MINUTES=30
```

### 3. Run the Bot

**Option A: Command Line (Recommended)**
```bash
python run_bot.py
```

**Option B: Web Dashboard**
```bash
python app.py
# Open http://localhost:5000 in browser
```

**Option C: Switch Trading Mode**
```bash
python switch_mode.py
```

---

## 📖 Documentation

### Essential Guides

| Document | Description |
|----------|-------------|
| **[QUICK_MODE_REFERENCE.md](QUICK_MODE_REFERENCE.md)** | ⚡ Quick reference card - start here! |
| **[TRADING_MODE_GUIDE.md](TRADING_MODE_GUIDE.md)** | 📘 Complete guide for paper/live trading |
| **[OPTIMIZED_SETTINGS.md](OPTIMIZED_SETTINGS.md)** | ⚙️ Configuration explained & recommendations |
| **[MODE_SWITCHING_COMPLETE.md](MODE_SWITCHING_COMPLETE.md)** | 📋 Feature summary & implementation details |

### Setup & Deployment

| Document | Description |
|----------|-------------|
| **[SETUP_API_KEYS.md](SETUP_API_KEYS.md)** | 🔑 How to set up Binance API keys |
| **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** | 🌐 Deploy to Render, Heroku, or VPS |
| **[ENV_TEMPLATE.txt](ENV_TEMPLATE.txt)** | 🔧 Configuration template |

---

## 🎯 Trading Modes

### 📄 Paper Trading (Safe - Recommended First)

- **No real money** - All trades simulated
- **Real market data** - Live prices and indicators
- **Perfect for testing** - Try strategies risk-free
- **Learn the system** - Understand how it works

```bash
python switch_mode.py  # Select option 1
python run_bot.py
```

### 💰 Live Trading (Real Money - Advanced)

- **Real orders** - Actual trades on Binance
- **Real profit/loss** - Your money at risk
- **Requires API keys** - Binance account needed
- **Use carefully** - Start with small amounts

```bash
python switch_mode.py  # Select option 2 (requires confirmations)
python run_bot.py      # Type: START LIVE TRADING
```

---

## ⚙️ Optimized Settings (Current)

The bot comes pre-configured with conservative, battle-tested settings:

| Setting | Value | Reason |
|---------|-------|--------|
| **Stop Loss** | 1.5% | Tight risk control |
| **Take Profit** | 4% | Realistic targets |
| **Risk per Trade** | 1.5% | Capital preservation |
| **Max Positions** | 1-2 | Limited exposure |
| **Trading Cycle** | 30 min | Quality signals |
| **Chart Timeframe** | 15 min | Intraday trading |
| **Pairs** | BTC/USDT, ETH/USDT | High liquidity |

**Risk/Reward Ratio:** 1:2.67 (excellent!)

---

## 📁 Project Structure

```
ai-trading-tool/
├── src/
│   ├── trading_bot.py          # Main AI trading bot
│   ├── simple_trading_bot.py   # Simplified bot for web dashboard
│   ├── data_fetcher.py          # Market data & order execution
│   ├── ml_predictor.py          # Machine learning models
│   ├── trading_strategies.py    # Trading strategies
│   ├── technical_indicators.py  # Technical analysis
│   ├── risk_manager.py          # Risk & position management
│   └── backtester.py            # Backtesting engine
├── templates/
│   ├── dashboard_premium.html   # Premium web dashboard
│   └── dashboard.html           # Classic web dashboard
├── models/                      # Trained ML models (auto-generated)
├── config.py                    # Configuration class
├── run_bot.py                   # CLI runner
├── app.py                       # Web dashboard app
├── switch_mode.py               # Interactive mode switcher
├── test_*.py                    # Testing utilities
└── *.md                         # Documentation
```

---

## 🔧 Configuration Files

### `.env` - Main Configuration
- Trading mode (paper/live)
- API credentials
- Risk parameters
- Trading pairs
- Cycle timing

### `config.py` - Python Configuration
- Default values
- Class-based config
- Module-level constants

---

## 🛠️ Utilities

| Script | Purpose |
|--------|---------|
| `switch_mode.py` | Switch between paper/live trading |
| `run_bot.py` | Run the bot (CLI mode) |
| `app.py` | Web dashboard server |
| `test_api_permissions.py` | Test Binance API setup |
| `test_balance.py` | Check account balance |
| `test_bot_health.py` | Bot health check |

---

## 📊 Performance Monitoring

### Command Line

```bash
# Real-time logs
tail -f trading_bot.log

# View in console
python run_bot.py
```

### Web Dashboard

```bash
python app.py
# Visit: http://localhost:5000
```

Monitor:
- Active positions
- P&L (Profit & Loss)
- Win rate
- Trade history
- Real-time signals

---

## 🔒 Safety Features

### Multiple Safety Layers

1. **Mode Switcher Confirmations**
   - 3 separate confirmations for live mode
   - Must type exact phrases
   - Clear risk warnings

2. **Runtime Checks**
   - Mode validation on startup
   - API key verification
   - Balance confirmation

3. **Risk Management**
   - Automatic stop loss (1.5%)
   - Position limits (max 2)
   - Daily loss limits
   - Confidence thresholds

4. **Logging & Monitoring**
   - All trades logged
   - Performance tracking
   - Error handling

---

## ⚠️ Important Warnings

### Before Going Live

- ✅ Test in **paper mode** for 2+ weeks
- ✅ Verify **win rate > 50%**
- ✅ Understand **all settings**
- ✅ Set up **API keys properly**
- ✅ Start with **small capital** ($100-500)
- ✅ **Monitor closely** (first 10 trades)
- ✅ Know the **risks** of crypto trading

### Risk Disclaimer

⚠️ **Cryptocurrency trading is high risk!**

- You can lose your entire investment
- Past performance ≠ future results
- No guarantees of profit
- Only trade with money you can afford to lose
- This bot is for educational purposes
- Use at your own risk

---

## 🎓 Learning Path

### Phase 1: Paper Trading (2-4 weeks)
1. Start in paper mode
2. Run for 50+ trades
3. Monitor performance
4. Learn the strategies
5. Adjust settings if needed

### Phase 2: Preparation (1 week)
1. Verify paper success
2. Set up Binance API
3. Test API connection
4. Deposit small amount
5. Read all documentation

### Phase 3: Live Trading (Ongoing)
1. Switch to live mode
2. Monitor first 10 trades
3. Track real performance
4. Scale up slowly
5. Continuous learning

---

## 🆘 Troubleshooting

### Bot won't start
```bash
python test_bot_health.py
```

### API errors
```bash
python test_api_permissions.py
```

### Balance issues
```bash
python test_balance.py
```

### Stop the bot immediately
```bash
Ctrl+C
```

### Switch back to safe mode
```bash
python switch_mode.py  # Select option 1 (Paper)
```

---

## 🧪 Testing

Before live trading, always test:

```bash
# 1. Test bot health
python test_bot_health.py

# 2. Test API connection
python test_api_permissions.py

# 3. Check balance
python test_balance.py

# 4. Run in paper mode
python switch_mode.py  # Select Paper
python run_bot.py
```

---

## 📈 Performance Metrics

Track these metrics:

- **Win Rate** - Target: >50%
- **Profit Factor** - Target: >1.5
- **Sharpe Ratio** - Higher is better
- **Max Drawdown** - Target: <20%
- **Total P&L** - Cumulative profit/loss
- **Risk/Reward** - 1:2.67 (current settings)

---

## 🔄 Updates & Maintenance

### Check for Updates
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Retrain Models
```bash
python -c "from src.trading_bot import CryptoTradingBot; bot = CryptoTradingBot(); bot.initialize()"
```

### Clean Logs
Logs auto-rotate at 10 MB (keeps 5 backups = 50 MB total)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

---

## 📞 Support

- **Documentation**: Read all `.md` files in root directory
- **Quick Reference**: `QUICK_MODE_REFERENCE.md`
- **Complete Guide**: `TRADING_MODE_GUIDE.md`
- **Issues**: Check troubleshooting section above

---

## 📄 License

[Your License Here]

---

## 🎉 Quick Command Reference

```bash
# Switch trading mode
python switch_mode.py

# Run the bot (CLI)
python run_bot.py

# Run web dashboard
python app.py

# Test everything
python test_bot_health.py

# View real-time logs
tail -f trading_bot.log
```

---

## ✨ Features Summary

✅ Machine Learning Predictions  
✅ 20+ Technical Indicators  
✅ Multi-Strategy Trading  
✅ Risk Management  
✅ Paper & Live Trading  
✅ Interactive Mode Switcher  
✅ Web Dashboard  
✅ Multiple Exchange Support  
✅ Comprehensive Documentation  
✅ Safety Confirmations  
✅ Performance Tracking  

---

**Happy Trading! 🚀**

*Remember: Start with paper mode, test thoroughly, use small amounts, and trade responsibly.*

---

*Version: 2.0 - Switchable Paper/Live Trading*  
*Last Updated: October 24, 2025*

