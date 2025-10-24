# Trading Mode Guide - Paper vs Live Trading

## Overview

Your AI trading bot now supports **two modes**:

1. **📄 Paper Trading** - Safe simulation mode (NO real money)
2. **🔴 Live Trading** - Real trading mode (REAL money, REAL risk)

---

## Quick Start

### Switch Trading Mode

Use the interactive mode switcher:

```bash
python switch_mode.py
```

This will show you:
- Current mode status
- Configuration settings
- Options to switch between modes
- Safety confirmations for live trading

---

## Paper Trading Mode (Default & Recommended)

### What is Paper Trading?

Paper trading simulates real trading **without using real money**. Perfect for:

✅ Testing strategies safely  
✅ Learning how the bot works  
✅ Verifying configurations  
✅ Building confidence before going live  
✅ No financial risk  

### How to Enable Paper Mode

```bash
python switch_mode.py
# Select option 1
```

Or manually edit `.env`:
```bash
TRADING_MODE=paper
INITIAL_CAPITAL=10000  # Simulated starting balance
```

### Running in Paper Mode

```bash
python run_bot.py
```

The bot will:
- ✅ Fetch real market data
- ✅ Analyze markets with real indicators
- ✅ Generate real trading signals
- ✅ Simulate order execution
- ✅ Track simulated profit/loss
- ❌ **NOT place any real orders**
- ❌ **NOT use real money**

---

## Live Trading Mode (Advanced Users Only)

### ⚠️ Important Warnings

🚨 **READ THIS BEFORE ENABLING LIVE MODE:**

- ❌ This uses **REAL MONEY** from your Binance account
- ❌ Losses are **REAL and PERMANENT**
- ❌ Cryptocurrency trading is **HIGH RISK**
- ❌ You can **LOSE your entire investment**
- ❌ No guarantees of profit
- ✅ Only use money you can **afford to lose**

### Prerequisites

Before enabling live trading:

1. **Successful Paper Trading**
   - Run in paper mode for at least 1-2 weeks
   - Verify positive results
   - Understand the bot's behavior

2. **Binance Account Setup**
   - Verified Binance account
   - API keys created (with Spot Trading enabled)
   - Small starting balance (recommend $100-500 for testing)

3. **API Key Configuration**
   - See `SETUP_API_KEYS.md` for instructions
   - Keys saved in `.env` file
   - Permissions: Enable Reading + Enable Spot & Margin Trading

### How to Enable Live Mode

**Method 1: Interactive Switcher (Recommended)**

```bash
python switch_mode.py
# Select option 2
# Read ALL warnings carefully
# Complete ALL 3 safety confirmations
```

**Method 2: Manual Configuration**

Edit `.env` file:
```bash
TRADING_MODE=live

# Your real Binance API credentials
BINANCE_API_KEY=your_actual_api_key_here
BINANCE_API_SECRET=your_actual_api_secret_here

# Recommended conservative settings
STOP_LOSS_PCT=0.015        # 1.5% stop loss
TAKE_PROFIT_PCT=0.04       # 4% take profit
MAX_POSITIONS=2            # Max 2 simultaneous trades
TRADING_PAIRS=BTC/USDT,ETH/USDT
```

### Running in Live Mode

```bash
python run_bot.py
```

You'll see:
1. **Live trading warning** - Must confirm to proceed
2. Bot will fetch your **real Binance balance**
3. Trades will be **actual market orders**
4. **Real money** will be used

### Safety Confirmations

The bot has **multiple safety layers**:

1. **Mode Switcher** - 3 confirmations required
2. **Run Bot** - Must type exact phrase to confirm
3. **API Check** - Verifies credentials before starting
4. **Balance Check** - Shows real balance before trading

---

## Comparison Table

| Feature | Paper Mode | Live Mode |
|---------|------------|-----------|
| **Real Money** | ❌ No | ✅ Yes |
| **Real Orders** | ❌ Simulated | ✅ Real |
| **Market Data** | ✅ Real | ✅ Real |
| **ML Predictions** | ✅ Real | ✅ Real |
| **Risk** | 🟢 Zero | 🔴 High |
| **Good For** | Testing, Learning | Profit (with risk) |
| **API Keys Required** | ❌ Optional | ✅ Required |
| **Recommended For** | Beginners | Experienced only |

---

## Step-by-Step: Your First Live Trade

### Phase 1: Paper Trading (2-4 weeks)

1. **Start in paper mode**
   ```bash
   python switch_mode.py  # Select Paper
   python run_bot.py
   ```

2. **Monitor for at least 50 trades**
   - Track win rate (target: >50%)
   - Monitor profit factor (target: >1.5)
   - Understand why trades win/lose

3. **Evaluate performance**
   - Check total P&L
   - Review max drawdown
   - Analyze strategy effectiveness

### Phase 2: Preparation for Live

1. **Create Binance account** (if you don't have one)

2. **Deposit small amount** ($100-500 for testing)

3. **Create API keys** (see SETUP_API_KEYS.md)
   - Enable Reading
   - Enable Spot & Margin Trading
   - Save keys securely in `.env`

4. **Test API connection**
   ```bash
   python test_api_permissions.py
   ```

### Phase 3: Go Live (Carefully!)

1. **Switch to live mode**
   ```bash
   python switch_mode.py  # Select Live
   ```

2. **Review configuration**
   - Conservative stop loss (1.5%)
   - Realistic take profit (4%)
   - Limited positions (1-2 max)

3. **Start bot with supervision**
   ```bash
   python run_bot.py
   # Type: START LIVE TRADING
   ```

4. **Monitor CLOSELY**
   - Watch first 5-10 trades carefully
   - Check Binance app for order confirmations
   - Monitor P&L in real-time
   - Be ready to stop if needed (Ctrl+C)

---

## Configuration for Each Mode

### Recommended Paper Trading Config

```bash
# .env file
TRADING_MODE=paper
INITIAL_CAPITAL=10000          # Large enough for testing
STOP_LOSS_PCT=0.015           # 1.5%
TAKE_PROFIT_PCT=0.04          # 4%
MAX_POSITIONS=2               # Conservative
TRADING_CYCLE_MINUTES=30      # 30-60 min recommended
TRADING_PAIRS=BTC/USDT,ETH/USDT
```

### Recommended Live Trading Config (Conservative)

```bash
# .env file
TRADING_MODE=live

# API keys (REQUIRED)
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret

# Conservative risk settings
STOP_LOSS_PCT=0.015           # 1.5% - tight stop loss
TAKE_PROFIT_PCT=0.04          # 4% - realistic target
MAX_POSITIONS=1               # Only 1 trade at a time (safest)
TRADING_CYCLE_MINUTES=60      # 60 min - fewer false signals
TRADING_PAIRS=BTC/USDT        # Only BTC for lowest risk

# Optional: Set max daily loss
MAX_DAILY_LOSS=50             # Stop trading if lose $50/day
```

### Aggressive Live Trading Config (Higher Risk)

```bash
# Only use if experienced!
TRADING_MODE=live
STOP_LOSS_PCT=0.015           # 1.5%
TAKE_PROFIT_PCT=0.06          # 6% - higher targets
MAX_POSITIONS=2               # Up to 2 positions
TRADING_CYCLE_MINUTES=30      # More frequent checks
TRADING_PAIRS=BTC/USDT,ETH/USDT  # Both major pairs
```

---

## Monitoring Your Bot

### Paper Mode Monitoring

Check these metrics:
- Total trades executed
- Win rate percentage
- Profit factor
- Max drawdown
- Sharpe ratio (if available)

### Live Mode Monitoring

⚠️ **Monitor MORE carefully in live mode:**

1. **Binance App**
   - Check open orders
   - Verify filled orders
   - Monitor account balance

2. **Bot Logs**
   ```bash
   tail -f trading_bot.log
   ```

3. **Performance Metrics**
   - Daily P&L
   - Win/loss ratio
   - Current positions

4. **Set Alerts**
   - Phone notifications for large losses
   - Email alerts for errors
   - Daily balance checks

---

## Switching Between Modes

### Paper → Live

✅ Safe to switch after successful paper trading  
⚠️ Requires API keys  
⚠️ Use small capital initially  

```bash
python switch_mode.py  # Select Live mode
```

### Live → Paper

✅ Can switch anytime  
✅ Recommended if experiencing losses  
✅ Good for testing new strategies  

```bash
python switch_mode.py  # Select Paper mode
```

**Note:** Open positions will be closed when switching modes!

---

## Troubleshooting

### "API credentials not configured" Error

**Solution:**
1. Create API keys on Binance
2. Add to `.env` file:
   ```
   BINANCE_API_KEY=your_key
   BINANCE_API_SECRET=your_secret
   ```
3. Run `python test_api_permissions.py`

### Live Orders Not Executing

**Possible causes:**
1. Insufficient balance
2. API permissions not enabled
3. Invalid order size (too small)
4. Exchange connectivity issues

**Solution:**
```bash
python test_balance.py  # Check account balance
python test_api_permissions.py  # Verify API setup
```

### Want to Test Live Orders Safely

**Solution:** Use Binance Testnet
1. Get testnet API keys from testnet.binance.vision
2. Use test orders (bot supports this)
3. No real money risk

---

## Safety Best Practices

### For Live Trading

1. ✅ **Start Small** - Use $100-500 initially
2. ✅ **Tight Stop Loss** - 1.5% maximum
3. ✅ **Limit Positions** - 1-2 trades max
4. ✅ **Monitor Daily** - Check results every day
5. ✅ **Set Max Loss** - Stop if daily loss > $X
6. ✅ **Withdraw Profits** - Take profits regularly
7. ❌ **Never Risk More** Than you can afford to lose

### For Paper Trading

1. ✅ Use realistic capital ($1,000-10,000)
2. ✅ Run for 50+ trades minimum
3. ✅ Test different timeframes
4. ✅ Experiment with settings
5. ✅ Learn from mistakes (they're free!)

---

## Support & Resources

- **Mode Switcher**: `python switch_mode.py`
- **Test API**: `python test_api_permissions.py`
- **Check Balance**: `python test_balance.py`
- **Bot Health**: `python test_bot_health.py`
- **View Logs**: `tail -f trading_bot.log`

---

## Summary

| Task | Command |
|------|---------|
| Check current mode | `python switch_mode.py` (option 3) |
| Switch to paper | `python switch_mode.py` (option 1) |
| Switch to live | `python switch_mode.py` (option 2) |
| Run bot | `python run_bot.py` |
| View status | `python switch_mode.py` |

---

**Remember:** 
- 📄 Start with PAPER mode
- 📊 Test thoroughly (50+ trades)
- 💰 Use small amounts in LIVE mode
- 📱 Monitor closely
- 🛑 Stop if losing consistently

**Good luck and trade safely! 🚀**

