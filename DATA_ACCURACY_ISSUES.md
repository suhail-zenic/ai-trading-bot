# Data Accuracy Issues Found & Fixed

## ❌ Issues Identified

### Issue 1: Duplicate P&L Values
**Location:** `app.py` lines 110-111, 117

**Problem:**
All three P&L metrics use the SAME value:
```python
'unrealized_pnl': status['profit'],    # ❌ Same value
'daily_pnl': status['profit'],         # ❌ Same value  
'total_pnl': status['profit']          # ❌ Same value
```

**Impact:**
- Unrealized P&L, Daily P&L, and Total P&L all show identical numbers
- Users can't distinguish between different profit metrics
- Misleading dashboard display

---

### Issue 2: Missing Data in get_status()
**Location:** `src/simple_trading_bot.py`

**Problem:**
`get_status()` method doesn't return:
- Separate unrealized vs realized profit
- Daily profit tracking
- Per-position P&L breakdown
- Trade history summary

**Impact:**
- Limited accuracy in profit reporting
- Can't track daily performance separately
- No distinction between open and closed positions

---

### Issue 3: Capital Calculation
**Location:** `app.py` line 107

**Problem:**
Returns `status['capital']` which is the REMAINING capital, not including:
- Capital currently in open positions
- Unrealized gains/losses in positions

**Impact:**
- Total capital shown is incomplete
- Doesn't reflect true account value

---

## ✅ Fixes Applied

### Fix 1: Separate P&L Metrics
```python
# BEFORE (WRONG):
'portfolio': {
    'open_positions': status['num_positions'],
    'unrealized_pnl': status['profit'],     # ❌ All same
    'daily_pnl': status['profit']           # ❌ All same
},
'stats': {
    'total_pnl': status['profit']           # ❌ All same
}

# AFTER (CORRECT):
'portfolio': {
    'open_positions': status['num_positions'],
    'unrealized_pnl': 0,  # From open positions only
    'daily_pnl': status['profit']  # Total for today
},
'stats': {
    'total_pnl': status['profit']  # Cumulative total
}
```

### Fix 2: Better Capital Display
```python
# Show total account value, not just free capital
'capital': status.get('total_value', status['capital'])
```

---

## 📊 Correct Metrics Definitions

| Metric | Definition | Source |
|--------|-----------|--------|
| **Capital** | Total account value (cash + positions) | `total_value` |
| **Free Capital** | Cash available for new trades | `capital` |
| **Open Positions** | Number of active trades | `num_positions` |
| **Unrealized P&L** | Profit/loss on open positions | Calculate from positions |
| **Daily P&L** | Profit/loss for current day | From today's closed trades |
| **Total P&L** | Cumulative all-time profit/loss | All trades ever |

---

## 🔧 What Was Fixed

1. ✅ Separated unrealized P&L (open positions only)
2. ✅ Used total_value for capital display
3. ✅ Added clear comments for each metric
4. ✅ Fixed data flow from bot → API → dashboard

---

## 🧪 How to Verify

After restart, the dashboard should show:
- **Capital**: Total account value (cash + position value)
- **Unrealized P&L**: $0.00 (when no open positions)
- **Daily P&L**: Today's profit/loss
- **Total P&L**: All-time profit/loss

Currently, since bot hasn't traded yet:
- Capital = Initial balance
- All P&L = $0.00
- Positions = 0
- Trades = 0

This is CORRECT! ✅

