# Dynamic Balance System

## Overview

The bot now **automatically fetches your real-time balance from Binance** instead of using a static value from `.env`.

## How It Works

### Paper Mode (Simulation)
- Uses `INITIAL_CAPITAL` from `.env` file
- Simulated balance only
- No real money

### Live Mode (Real Trading)
- ✅ **Automatically fetches balance from Binance**
- ✅ **Updates every trading cycle (15 minutes)**
- ✅ **Refreshes immediately after each trade**
- ✅ **Always uses your actual USDT balance**

## Balance Updates

The bot refreshes your balance:

1. **On startup** - Gets initial balance
2. **Every trading cycle** - Before checking signals (every 15 min)
3. **After BUY orders** - Immediately after order fills
4. **After SELL orders** - Immediately after order fills

## What You'll See in Logs

```
[LIVE] Binance Balance Updated:
   Total: 25.50 USDT
   Free:  22.50 USDT (available for trading)
   Used:  3.00 USDT (in open orders)
```

- **Total**: Your complete USDT balance
- **Free**: Available for new trades
- **Used**: Currently in open orders

## Balance Changes

### If You Add USDT to Binance:
- Bot automatically detects it in the next cycle (max 15 min)
- Starts trading with the new balance

### If You Withdraw USDT:
- Bot automatically adjusts
- Won't try to trade with money that's not there

### If Balance Changes from Trading:
- Updates immediately after each order
- Dashboard shows real-time balance

## Configuration

### `.env` File (Local/Paper Mode)
```bash
INITIAL_CAPITAL=10000  # Only for paper mode
TRADING_MODE=paper     # or 'live'
```

### Render Environment Variables (Live Mode)
```bash
TRADING_MODE=live
INITIAL_CAPITAL=10000  # Ignored in live mode, fetched from Binance
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
```

## Important Notes

1. **API Permissions Required:**
   - ✅ Enable Reading (to fetch balance)
   - ✅ Enable Spot & Margin Trading (to place orders)

2. **Balance Synchronization:**
   - The bot always uses your **FREE balance** (available for trading)
   - Locked funds in orders are not used for new trades

3. **Initial Capital Tracking:**
   - On first start, bot records your total balance as "initial capital"
   - Used to calculate profit/loss percentage
   - Resets when you restart the bot

## Benefits

✅ **No manual updates needed** - Balance stays in sync automatically
✅ **Accurate profit tracking** - Based on real account value
✅ **Safe position sizing** - Never trades more than you have
✅ **Flexible capital management** - Add/withdraw USDT anytime

## Troubleshooting

### Balance Not Updating?
1. Check API key has "Enable Reading" permission
2. Check Render logs for errors
3. Visit `/api/diagnostics` endpoint to verify connection

### Shows Wrong Balance?
1. Check for open orders (shown as "Used")
2. Wait for next trading cycle (max 15 min)
3. Restart the bot to force refresh

## Summary

**You don't need to worry about the `INITIAL_CAPITAL` value in `.env` anymore!** 

In live mode, the bot will:
- Read your actual balance from Binance
- Update it automatically
- Track it in real-time

Just make sure your API keys have the right permissions! 🚀

