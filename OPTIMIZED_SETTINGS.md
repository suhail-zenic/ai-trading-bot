# Optimized Trading Bot Settings

## Applied Configuration (Updated)

The bot has been configured with the following optimized parameters for better risk management and performance:

### Risk Management
| Parameter | Previous | Optimized | Description |
|-----------|----------|-----------|-------------|
| **Stop Loss (SL)** | 4-5% | **1.5%** | Tighter stop loss to minimize losses |
| **Take Profit (TP)** | 10-15% | **4%** | More realistic profit target |
| **Risk per Trade** | 2% | **1.5%** | Conservative risk per position |
| **Max Open Trades** | 5 | **1-2** | Focus on quality over quantity |

### Trading Timing
| Parameter | Previous | Optimized | Description |
|-----------|----------|-----------|-------------|
| **Trading Cycle** | 5-15 min | **30 min** | Better signal quality (30-60 min range) |
| **Chart Timeframe** | 15m | **15m** | Optimal for intraday trading (15-30m range) |

### Trading Pairs
| Parameter | Previous | Optimized | Description |
|-----------|----------|-----------|-------------|
| **Coins** | BTC, ETH, SOL, BNB | **BTC/USDT, ETH/USDT** | High liquidity pairs only |

## Files Updated

1. **config.py** - Core configuration updated with optimized parameters
2. **src/trading_bot.py** - Default trading cycle changed to 30 minutes

## Key Benefits of These Settings

### 1. Reduced Risk
- **1.5% Stop Loss**: Limits potential losses on any single trade
- **1.5% Risk per Trade**: Conservative position sizing
- **Max 1-2 Positions**: Prevents over-exposure

### 2. Better Trade Quality
- **30-minute cycle**: Reduces noise and false signals
- **4% Take Profit**: More achievable profit targets
- **BTC/ETH only**: High liquidity = better execution

### 3. Improved Risk/Reward
- Risk/Reward Ratio: 1:2.67 (1.5% risk for 4% profit)
- Lower false signals with 30-min intervals
- Focused trading on most liquid pairs

## How to Run the Bot

### Option 1: Use Default Settings (Now Optimized)
```bash
python src/trading_bot.py
```

### Option 2: Override with Environment Variables
Create a `.env` file or export variables:
```bash
# Trading Configuration
TRADING_MODE=paper
INITIAL_CAPITAL=10000

# Risk Management
STOP_LOSS_PCT=0.015       # 1.5%
TAKE_PROFIT_PCT=0.04      # 4%
MAX_POSITIONS=2           # 1-2 trades

# Trading Cycle
TRADING_CYCLE_MINUTES=30  # 30-60 min

# Trading Pairs
TRADING_PAIRS=BTC/USDT,ETH/USDT
```

### Option 3: Adjust in Code
The settings are now optimized by default. You can fine-tune:
- Increase cycle to 60 min for even fewer false signals
- Use 30m timeframe instead of 15m for longer trends
- Adjust confidence threshold in config.py

## Position Sizing Example

With these settings and $10,000 capital:
- **Risk per trade**: $150 (1.5% of $10,000)
- **Position size** (at 1.5% SL): $10,000
- **Stop Loss**: -$150 if hit
- **Take Profit**: +$400 if hit
- **Risk/Reward**: 1:2.67

## Recommended Usage

### For Paper Trading (Testing)
- Start with current settings
- Monitor for 1-2 weeks
- Analyze win rate and profit factor
- Adjust confidence threshold if needed

### For Live Trading (Real Money)
- Use these conservative settings
- Start with small capital (e.g., $500-$1000)
- Monitor closely for first week
- Scale up only after consistent profits

## Important Notes

⚠️ **Always test in paper mode first!**

✅ **These settings prioritize**:
- Capital preservation
- Consistent small wins
- Risk management over profit maximization

📊 **Monitor these metrics**:
- Win rate (target: >50%)
- Profit factor (target: >1.5)
- Max drawdown (target: <10%)

## Next Steps

1. **Test the bot**: Run in paper mode with new settings
2. **Monitor performance**: Track for at least 50 trades
3. **Analyze results**: Review win rate and risk/reward
4. **Fine-tune**: Adjust if needed based on results
5. **Go live**: Only after consistent paper trading profits

---

**Configuration Last Updated**: October 24, 2025
**Status**: Optimized for conservative, sustainable trading

