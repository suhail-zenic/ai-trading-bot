# How to Restart Your Bot Safely

## ✅ The Fixes Are Applied

Your bot has been fixed with these improvements:
- ✅ Timeout protection on all API calls
- ✅ Automatic retry for network errors
- ✅ Rate limit handling
- ✅ Heartbeat monitoring
- ✅ Immediate log flushing
- ✅ Better error recovery
- ✅ Health status tracking

## 🚀 Quick Start (Recommended)

### Option 1: Dashboard (Best for monitoring)

```bash
# Start the dashboard
python app.py

# Open your browser to:
http://localhost:5000

# Click "Start Bot" button
# Monitor the dashboard (shows health status, positions, trades, logs)
```

### Option 2: Command Line (Best for detailed logs)

```bash
# Run the bot directly
python run_bot.py

# Or with live log monitoring in another window:
# Window 1:
python run_bot.py

# Window 2:
Get-Content trading_bot.log -Wait -Tail 50
```

## 📊 Before Running Overnight

### 1. Run Health Check (Takes ~1 minute)
```bash
python test_bot_health.py
```

**Expected Result:** 5-6 tests should pass
- If all pass: ✅ Safe to run overnight
- If 5 pass: ✅ Should be fine, monitor for 30 minutes first
- If <5 pass: ❌ Fix issues before running overnight

### 2. Test for 30 Minutes First
1. Start the bot
2. Watch for at least 2-3 trading cycles (every 5 minutes)
3. Check that logs are being written
4. Verify positions are being tracked correctly
5. Ensure no repeated errors

### 3. Monitor Logs
```bash
# PowerShell - Live log monitoring
Get-Content trading_bot.log -Wait -Tail 50
```

**Good Signs:**
```
=== TRADING CYCLE - 2025-10-24 10:30:00 ===
Checking existing positions for SL/TP...
Analyzing 3 trading pairs...
BTC/USDT: Signal=HOLD, Price=$67234.50, RSI=52.3
=== CYCLE COMPLETE ===
```

**Bad Signs (Need attention):**
```
Network error fetching BTC/USDT, retrying...
Rate limit exceeded for ETH/USDT, waiting...
Trading cycle timeout - exceeded 5 minutes
```

## 🎯 Recommended Settings for Overnight

Edit `config.py` to make trading less aggressive:

```python
# Less frequent trading = fewer API calls = more stable
TRADING_CYCLE_MINUTES = 10  # Instead of 5

# Smaller positions = lower risk
POSITION_SIZE_PCT = 0.10    # Instead of 0.15

# Fewer positions = easier to manage
MAX_POSITIONS = 3           # Instead of 5
```

## 🔍 Dashboard Health Indicators

When you open http://localhost:5000, you'll now see:

### Health Status (NEW!)
- **Green "Healthy and active"** ✅ = Bot is working perfectly
- **Yellow "Warning: No heartbeat for 10+ minutes"** ⚠️ = Bot might be stuck
- **Red "Bot stopped"** ❌ = Bot is not running

### Other Indicators
- **Last Heartbeat**: Shows when the last cycle completed
- **Seconds Since Heartbeat**: How long since last activity
- **Is Healthy**: true/false health status

## 🚨 What to Do If Bot Gets Stuck

### 1. Check Dashboard
- Open http://localhost:5000
- Look at Health Status
- Check "Seconds Since Heartbeat"
- If >600 seconds: Bot is stuck

### 2. Check Logs
```bash
Get-Content trading_bot.log -Tail 100
```
- Last entry shows where it stuck
- Look for repeated errors

### 3. Restart the Bot
```bash
# If running in terminal: Press Ctrl+C
# If running as dashboard: Click "Stop Bot" then "Start Bot"

# Or restart completely:
python app.py
```

### 4. Report Issue
If it gets stuck again, save:
- Last 100 log lines
- Time it got stuck
- Your internet status
- Any error messages

## 🔧 Troubleshooting

### "Exchange connection failed"
```bash
# Check internet
ping binance.com

# Try different exchange
# Edit src/data_fetcher.py line 14:
exchange_name = 'kucoin'  # or 'kraken', 'okx'
```

### "Rate limit exceeded"
- Increase TRADING_CYCLE_MINUTES in config.py
- Reduce number of TRADING_PAIRS
- Wait 5 minutes and restart

### "Not enough data"
- Normal for new/low-volume coins
- Bot will skip them automatically
- Not an error, just informational

### Log file not updating
```bash
# Check if bot is actually running
# Dashboard: Look for "Running" status
# Or check Task Manager for python.exe

# Force log flush by restarting
```

## 📈 Performance Expectations

With current settings (5-minute cycles):
- **API calls**: ~15-20 per cycle
- **Cycle duration**: 3-5 seconds normally
- **Trades**: 0-5 per hour (depends on market)
- **Log entries**: ~50-100 per hour

## ✨ New Features After Fixes

1. **Timeout Protection**: No more infinite hangs
2. **Auto-Retry**: Recovers from temporary network issues
3. **Health Monitoring**: Dashboard shows if bot is alive
4. **Better Logging**: All actions logged immediately
5. **Graceful Degradation**: Continues even if some pairs fail

## 🌙 Overnight Checklist

Before going to bed:

- [ ] Run `python test_bot_health.py` (5/6 or 6/6 pass)
- [ ] Start bot and monitor for 30 minutes
- [ ] Check at least 3 cycles completed successfully
- [ ] Verify logs are being written
- [ ] Dashboard shows "Healthy and active"
- [ ] No repeated error messages
- [ ] Internet connection is stable

If all checked: **Your bot is ready to run overnight!** 🎉

## 📞 Need Help?

If issues persist:
1. Save the last 100 lines of trading_bot.log
2. Note what time the bot got stuck
3. Run the health check and share results
4. Check if your internet was stable

---

**Remember**: The bot is now much more resilient. Even if individual API calls fail, it will:
- Retry automatically
- Skip problematic symbols
- Continue to the next cycle
- Log everything for debugging

You should have a smooth overnight run! 🚀

