# Bot Log Storage Explained 📝

## Overview

Your bot now has **automatic log rotation** to prevent files from growing too large!

## 📊 Log Storage Configuration

### **File Logs (Persistent)**

**Location:** `trading_bot.log` in your project folder

**Rotation Settings:**
- ✅ **Max file size**: 10 MB per file
- ✅ **Backup files**: 5 old files kept
- ✅ **Total storage**: ~50-60 MB maximum
- ✅ **Auto-cleanup**: Old logs deleted automatically

**How It Works:**
```
trading_bot.log          ← Current log file (active)
trading_bot.log.1        ← Previous rotation (10 MB)
trading_bot.log.2        ← 2 rotations ago (10 MB)
trading_bot.log.3        ← 3 rotations ago (10 MB)
trading_bot.log.4        ← 4 rotations ago (10 MB)
trading_bot.log.5        ← 5 rotations ago (10 MB)
```

When `trading_bot.log` reaches 10 MB:
1. Renames `trading_bot.log.4` → `trading_bot.log.5` (deletes old .5)
2. Renames `trading_bot.log.3` → `trading_bot.log.4`
3. Renames `trading_bot.log.2` → `trading_bot.log.3`
4. Renames `trading_bot.log.1` → `trading_bot.log.2`
5. Renames `trading_bot.log` → `trading_bot.log.1`
6. Creates new empty `trading_bot.log`

### **Dashboard Logs (In-Memory)**

**Location:** Web browser (http://localhost:5000)

**Storage:**
- ✅ **Last 100 messages** only
- ✅ **Lost on restart**: Not persistent
- ✅ **Purpose**: Quick monitoring

## 📈 Expected Log Growth

### **With Current Settings (5-minute cycles):**

| Time Period | Log Lines | File Size | Files |
|-------------|-----------|-----------|-------|
| 1 hour      | 240-600   | ~10 KB    | 1     |
| 1 day       | 5,760-14,400 | ~240 KB | 1     |
| 1 week      | 40,320-100,800 | ~1.7 MB | 1     |
| 1 month     | ~173,000-432,000 | ~7 MB | 1     |
| 2 months    | ~346,000-864,000 | 10 MB+ | 2 (rotates!) |

### **Storage Time (Before Deletion):**

With 10 MB per file × 6 files (current + 5 backups):
- **~60 MB total**
- **~8-10 months** of logs before oldest is deleted
- **Completely automatic** - no manual cleanup needed!

## 🔍 How to View Logs

### **Option 1: Real-Time Monitoring (Recommended)**
```bash
# PowerShell - Watch logs as they're written
Get-Content trading_bot.log -Wait -Tail 50
```

### **Option 2: View in Dashboard**
```bash
python app.py
# Open: http://localhost:5000
# Logs section shows last 100 messages
```

### **Option 3: Open Full Log File**
```bash
# PowerShell - View entire current log
Get-Content trading_bot.log

# View with line numbers
Get-Content trading_bot.log | Select-Object -First 100 | ForEach-Object { "$($_.ReadCount): $_" }

# View last 100 lines
Get-Content trading_bot.log -Tail 100

# Search for errors
Get-Content trading_bot.log | Select-String "ERROR"

# Search for specific symbol
Get-Content trading_bot.log | Select-String "BTC/USDT"
```

### **Option 4: View Old Rotated Logs**
```bash
# View first backup
Get-Content trading_bot.log.1

# View all rotated logs
Get-Content trading_bot.log.*
```

## 📂 Log File Locations

All log files are stored in your project root:
```
C:\Users\suhai\ai-trading-tool\
├── trading_bot.log       ← Current active log
├── trading_bot.log.1     ← Most recent rotation (if exists)
├── trading_bot.log.2     ← 2nd rotation (if exists)
├── trading_bot.log.3     ← 3rd rotation (if exists)
├── trading_bot.log.4     ← 4th rotation (if exists)
└── trading_bot.log.5     ← Oldest rotation (if exists)
```

## 🗑️ Cleaning Up Logs

### **Automatic Cleanup (Already Configured)** ✅
- Files older than the 5th backup are **automatically deleted**
- No manual intervention needed
- Maximum ~60 MB used

### **Manual Cleanup (If Needed)**
```bash
# Delete all log files (fresh start)
Remove-Item trading_bot.log*

# Delete only rotated logs (keep current)
Remove-Item trading_bot.log.[1-5]

# Delete logs older than 30 days
Get-ChildItem trading_bot.log* | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
```

## 📝 What Gets Logged?

### **Every Trading Cycle (~50 lines per cycle):**
```
=== TRADING CYCLE - 2025-10-24 10:30:00 ===
Checking existing positions for SL/TP...
No open positions to check
Analyzing 3 trading pairs...
BTC/USDT: Signal=HOLD, Price=$67234.50, RSI=52.3
ETH/USDT: Signal=BUY, Price=$2634.21, RSI=38.7
BUY ETH/USDT - Amount: 0.5000 @ $2634.21 | SL: $2529.24 | TP: $2897.63
SOL/USDT: Signal=HOLD, Price=$165.32, RSI=55.1
Portfolio: $10500.00 | Profit: $500.00 (5.00%) | Positions: 1
=== CYCLE COMPLETE ===
```

### **Error Messages:**
```
ERROR - Network error fetching BTC/USDT, retrying (1/2)...
WARNING - Rate limit exceeded for ETH/USDT, waiting...
ERROR - Error in trading cycle: Connection timeout
```

### **Bot Lifecycle:**
```
INFO - SimpleTradingBot module loaded
INFO - Initializing SimpleTradingBot...
INFO - Successfully connected to Binance!
INFO - STREAMLINED TRADING BOT STARTED
INFO - Bot stopping...
INFO - Bot has been stopped gracefully
```

## ⚙️ Customizing Log Storage

Want to change the settings? Edit `src/simple_trading_bot.py` line 13-17:

```python
# CURRENT (Recommended):
rotating_handler = RotatingFileHandler(
    'trading_bot.log',
    maxBytes=10*1024*1024,  # 10 MB per file
    backupCount=5,           # Keep 5 backups
    mode='a'
)

# CONSERVATIVE (Less storage):
rotating_handler = RotatingFileHandler(
    'trading_bot.log',
    maxBytes=5*1024*1024,   # 5 MB per file
    backupCount=3,          # Keep 3 backups
    mode='a'
)

# AGGRESSIVE (More history):
rotating_handler = RotatingFileHandler(
    'trading_bot.log',
    maxBytes=20*1024*1024,  # 20 MB per file
    backupCount=10,         # Keep 10 backups
    mode='a'
)
```

## 📊 Storage Impact by Settings

| Setting | File Size | Backups | Total Storage | History Duration |
|---------|-----------|---------|---------------|------------------|
| Conservative | 5 MB | 3 | ~20 MB | 3-4 months |
| **Current** | **10 MB** | **5** | **~60 MB** | **8-10 months** |
| Aggressive | 20 MB | 10 | ~220 MB | 24-30 months |

## 🎯 Recommendations

### **For Most Users (Current Setup):**
- ✅ 10 MB per file, 5 backups
- ✅ ~60 MB total storage
- ✅ 8-10 months of history
- ✅ Perfect balance of storage vs history

### **For Long-Term Analysis:**
```python
maxBytes=20*1024*1024   # 20 MB
backupCount=10          # 10 backups
# = 2+ years of logs
```

### **For Limited Storage:**
```python
maxBytes=5*1024*1024    # 5 MB
backupCount=2           # 2 backups
# = ~15 MB total
```

## 🔐 Log Security

**What's in the logs:**
- ✅ Timestamps
- ✅ Trading signals
- ✅ Position sizes and prices
- ✅ Profit/loss calculations
- ✅ Error messages

**What's NOT in the logs:**
- ❌ API keys
- ❌ API secrets
- ❌ Personal information
- ❌ Passwords

**Safe to share:** Yes, but redact:
- Capital amounts (if private)
- Exact profit amounts
- Any custom configurations

## 📈 Monitoring Log Growth

Check current log file size:
```bash
# PowerShell
(Get-Item trading_bot.log).Length / 1MB
# Output: 2.3 (means 2.3 MB)

# Check all log files
Get-ChildItem trading_bot.log* | Select-Object Name, @{Name="SizeMB";Expression={$_.Length / 1MB}}
```

## 🎉 Summary

**Your bot now has smart log management!**

✅ **Automatic rotation** at 10 MB
✅ **Keeps 5 backups** (~60 MB total)
✅ **8-10 months** of history
✅ **Auto-cleanup** of old files
✅ **No manual maintenance** needed

**You can safely run your bot for months without worrying about log files filling up your disk!** 🚀

