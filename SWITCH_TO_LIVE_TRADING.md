# Switch to Live Trading Guide 🚀

## ⚠️ CRITICAL: Read This First!

You have **~22-24 USDT** (₹2,000). This is a **small amount** for testing.

**Expectations:**
- Good for learning and testing
- Expect 2-5 trades max at a time
- Profit/loss will be small (₹50-200 per trade)
- Perfect for gaining experience

## 🔑 Step 1: Enable Trading on API Key

### **If You Have KYC Verified:**

1. **Go to API Management:**
   ```
   Binance.com → Profile → API Management
   ```

2. **Click "Edit" on your API key**

3. **Enable these permissions:**
   ```
   ✅ Enable Reading
   ✅ Enable Spot & Margin Trading ← ENABLE THIS!
   ❌ Enable Futures (leave OFF)
   ❌ Enable Withdrawals (NEVER enable!)
   ```

4. **Save changes**

5. **Complete security verification** (2FA code)

### **If You DON'T Have KYC:**

**You must complete KYC first to enable trading:**

1. Go to: https://www.binance.com/en/my/settings/profile
2. Click "Verify" under Identification
3. Upload Aadhaar/PAN card
4. Complete face verification
5. Wait for approval (10 mins - 24 hours)
6. Then enable trading on API key

**Without KYC, you cannot use API for live trading!**

## 💰 Step 2: Transfer USDT to Spot Wallet

Your USDT is probably in **P2P Wallet** - needs to be in **Spot Wallet** for trading!

### **How to Transfer:**

1. **Go to Wallet:**
   ```
   Binance → Wallet → Fiat and Spot
   ```

2. **Click "Transfer"**

3. **Set transfer:**
   ```
   From: P2P Wallet
   To: Spot Wallet
   Coin: USDT
   Amount: [Your amount, e.g., 23 USDT]
   ```

4. **Click "Confirm Transfer"**

5. **Verify:** Check Spot Wallet has USDT

## ⚙️ Step 3: Configure Bot for Small Capital

With only ~23 USDT, you need to adjust settings for smaller trades.

### **Edit Your Bot Configuration:**

Open `.env` file:
```bash
notepad .env
```

**Add/modify these lines:**

```bash
# Switch to LIVE mode
TRADING_MODE=live

# Smaller position sizes for low capital
# With 23 USDT, use 30-40% per position = ~7-9 USDT per trade
```

**Save and close.**

### **Edit config.py for Small Capital:**

We need to reduce position sizes since you have limited capital.

Open `config.py` and change line 56-60 to:

```python
# Small capital settings (for ~20-50 USDT)
POSITION_SIZE_PCT = 0.30  # 30% per position instead of 15%
STOP_LOSS_PCT = 0.03      # 3% stop loss (tighter)
TAKE_PROFIT_PCT = 0.08    # 8% take profit (quicker)
MAX_POSITIONS = 2         # Max 2 positions (instead of 5)
TRADING_CYCLE_MINUTES = 10 # Every 10 minutes (more conservative)
```

**Why these changes?**
- **30% per position** = ~7 USDT per trade (minimum needed)
- **Max 2 positions** = Can open 2 trades max
- **Tighter stops** = Protect small capital
- **10-min cycles** = Less frequent, more careful

## 🎯 Step 4: Start Live Trading

### **Option A: Via Dashboard (Recommended)**

```bash
python app.py
```

1. Open: http://localhost:5000
2. Click **"Start Bot"**
3. Monitor the dashboard
4. Watch for real trades!

### **Option B: Via Command Line**

```bash
python run_bot.py
```

Watch the logs for trade execution.

## 📊 What to Expect with 23 USDT

### **Trading Capacity:**
- **Per trade:** ~7 USDT (₹600)
- **Max positions:** 2 trades at once
- **Total deployed:** ~14 USDT when fully invested

### **Example Trades:**
```
Trade 1: BUY 0.0001 BTC @ $67,000 = ~7 USDT
Trade 2: BUY 0.003 ETH @ $2,600 = ~7 USDT
Remaining: ~9 USDT in reserve
```

### **Expected Profits (Per Trade):**
- **8% gain:** ₹48 profit (₹600 × 8%)
- **3% loss:** -₹18 loss (₹600 × 3%)
- **Daily target:** ₹50-150 (realistic)

## ⚠️ Risk Management for Small Capital

### **Do's:**
- ✅ Start with 1-2 trades only
- ✅ Monitor closely first day
- ✅ Use tight stop losses (3%)
- ✅ Take profits quickly (8%)
- ✅ Don't overtrade

### **Don't's:**
- ❌ Don't expect huge profits
- ❌ Don't panic on first loss
- ❌ Don't add more money immediately
- ❌ Don't run unattended first week

## 🔍 Step 5: Verify Live Trading is Working

### **Check 1: Bot Status**
Dashboard should show:
```
Status: Running
Mode: LIVE ← Important!
Capital: ~23 USDT
Positions: 0-2
```

### **Check 2: Binance Wallet**
Check your Spot Wallet:
- USDT decreases when buying
- BTC/ETH/SOL increases
- Real orders in "Spot Orders"

### **Check 3: Bot Logs**
You should see:
```
LIVE TRADING MODE ENABLED
BUY BTC/USDT - Amount: 0.0001 @ $67,234.50
Order executed on Binance
```

## 📈 Growing Your Capital

### **First Week Goals:**
- Learn how the bot works
- Understand trade execution
- Get comfortable with losses
- Target: Break even or +5%

### **After Testing:**
- If profitable: Add more capital (₹5,000-10,000)
- If issues: Switch back to paper mode, analyze

## 🚨 Emergency Stop

**To stop trading immediately:**

### **Dashboard:**
Click **"Stop Bot"** button

### **Command Line:**
Press `Ctrl + C`

### **Close All Positions:**
1. Go to Binance → Trade → Spot
2. Manually sell your positions
3. Convert back to USDT

## 💡 Pro Tips for Small Capital

1. **Be Patient:** Don't expect daily profits
2. **Learn First:** Focus on learning, not earning
3. **Track Everything:** Keep a log of trades
4. **Stay Realistic:** ₹2,000 won't make you rich overnight
5. **Compound:** Reinvest profits to grow capital

## 📞 Troubleshooting

### **"Insufficient balance" error:**
- Position size too large
- Reduce `POSITION_SIZE_PCT` to 0.25 (25%)

### **"Invalid API key" error:**
- Trading permission not enabled
- Complete KYC first
- Re-enable "Spot Trading" on API

### **No trades executing:**
- Check USDT is in Spot Wallet (not P2P)
- Verify bot is in LIVE mode
- Check trading signals are generating

### **Trades too small:**
- Binance minimums: ~10 USDT per trade
- You need at least 20-30 USDT total
- Consider adding more capital

## ✅ Pre-Flight Checklist

Before starting live trading:

- [ ] KYC completed on Binance ✅
- [ ] API key has "Enable Spot Trading" ✅
- [ ] USDT in Spot Wallet (not P2P) ✅
- [ ] `.env` has `TRADING_MODE=live` ✅
- [ ] `config.py` adjusted for small capital ✅
- [ ] Tested bot in paper mode ✅
- [ ] Understand you might lose money ✅
- [ ] Ready to monitor actively ✅

## 🎯 Your Action Plan

**Right Now:**
1. Enable "Spot Trading" on API key (need KYC)
2. Transfer USDT to Spot Wallet
3. Edit settings for small capital
4. Start bot and monitor

**First Day:**
- Watch every trade
- Understand bot behavior
- Be ready to stop if issues

**First Week:**
- Evaluate performance
- Decide to continue or adjust
- Add capital if successful

---

**Remember: ₹2,000 is for LEARNING, not earning. Focus on understanding how it works!** 🎓

Good luck! 🚀

