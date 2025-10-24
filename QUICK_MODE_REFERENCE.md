# Quick Mode Reference Card

## 🎯 One-Minute Guide

### Current Mode Status
```bash
python switch_mode.py
# Select option 3 to see current mode
```

---

## 📄 Paper Trading (Safe - No Real Money)

### Enable Paper Mode
```bash
python switch_mode.py
# Select option 1
```

### Run Paper Trading
```bash
python run_bot.py
```

**✅ Safe for:** Testing, learning, experimenting  
**❌ No real money, no real profit**

---

## 🔴 Live Trading (Real Money - High Risk)

### Enable Live Mode
```bash
python switch_mode.py
# Select option 2
# Complete 3 safety confirmations
```

### Run Live Trading
```bash
python run_bot.py
# Type: START LIVE TRADING
```

**⚠️ Uses REAL money from Binance**  
**⚠️ Requires API keys configured**

---

## ⚡ Quick Commands

| Action | Command |
|--------|---------|
| Switch mode | `python switch_mode.py` |
| Run bot | `python run_bot.py` |
| Check status | `python switch_mode.py` → option 3 |
| Test API | `python test_api_permissions.py` |
| Check balance | `python test_balance.py` |
| View logs | `tail -f trading_bot.log` |
| Stop bot | Press `Ctrl+C` |

---

## 📊 Optimized Settings (Current)

```
Stop Loss: 1.5%
Take Profit: 4%
Max Positions: 1-2
Cycle Time: 30 minutes
Pairs: BTC/USDT, ETH/USDT
```

---

## 🚦 Safety Checklist

### Before Live Trading:
- [ ] Tested in paper mode for 2+ weeks
- [ ] Win rate >50% in paper trading
- [ ] API keys configured in `.env`
- [ ] Started with small capital ($100-500)
- [ ] Ready to monitor closely
- [ ] Understand the risks

---

## 🆘 Emergency

**Stop the bot immediately:**
```bash
Ctrl+C
```

**Switch back to paper mode:**
```bash
python switch_mode.py
# Select option 1
```

---

## 📁 Configuration Files

**Main config:** `.env`  
**Current mode:** Check with `switch_mode.py`  
**Bot logs:** `trading_bot.log`

---

## 💡 Pro Tips

1. **Always start with paper mode**
2. **Test for 50+ trades before going live**
3. **Use small amounts initially ($100-500)**
4. **Monitor first 10 live trades closely**
5. **Stop if losing >5% in a day**
6. **Withdraw profits regularly**

---

## 📞 Full Documentation

- **Complete Guide:** `TRADING_MODE_GUIDE.md`
- **Optimized Settings:** `OPTIMIZED_SETTINGS.md`
- **API Setup:** `SETUP_API_KEYS.md`

---

**Current Version:** v2.0 - Switchable Paper/Live Trading  
**Last Updated:** October 2025

