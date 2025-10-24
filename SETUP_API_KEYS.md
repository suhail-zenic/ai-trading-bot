# How to Set Up Your Binance API Keys 🔑

## ⚠️ IMPORTANT: Your API Keys Need Specific Permissions

Your bot is currently running in **PAPER TRADING MODE** (simulated), so API keys are **OPTIONAL**. However, if you want to use real market data or prepare for live trading, follow these steps:

## 📋 Step 1: Get Your API Keys from Binance

1. **Log in to Binance:** https://www.binance.com
2. **Go to API Management:**
   - Click your profile (top right)
   - Select "API Management"
   - Or go directly to: https://www.binance.com/en/my/settings/api-management

3. **Create New API Key:**
   - Click "Create API"
   - Label: "Trading Bot" (or any name you prefer)
   - Complete security verification (2FA, email, etc.)

4. **Set Permissions (CRITICAL!):**
   - ✅ **Enable Reading** (check "Enable Reading")
   - ❌ **DISABLE Trading** (for now, keep unchecked for safety)
   - ❌ **DISABLE Withdrawals** (NEVER enable this!)
   - ❌ **DISABLE Futures** (unless you trade futures)
   
   **For Paper Trading (Current Mode):**
   - Only "Enable Reading" is needed
   
   **For Live Trading (When Ready):**
   - Enable "Enable Reading" + "Enable Spot & Margin Trading"
   - NEVER enable "Enable Withdrawals"

5. **Copy Your Keys:**
   - **API Key**: Long string (public, like username)
   - **Secret Key**: Another long string (PRIVATE, like password)
   - ⚠️ Secret Key shown ONLY ONCE - save it immediately!

## 📝 Step 2: Add Keys to Your Bot

### Option A: Edit the .env File (RECOMMENDED)

I've created a `.env` file for you. Open it and replace the placeholder values:

```bash
# Open in Notepad
notepad .env

# Or use any text editor
```

Replace these lines:
```bash
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

With your actual keys:
```bash
BINANCE_API_KEY=abcdef123456789...your_actual_api_key
BINANCE_API_SECRET=xyz789456123...your_actual_secret_key
```

**Save the file and close.**

### Option B: Set Windows Environment Variables (Advanced)

If you prefer system-wide environment variables:

1. **Open System Properties:**
   - Press `Win + R`
   - Type: `sysdm.cpl`
   - Press Enter

2. **Go to Environment Variables:**
   - Click "Advanced" tab
   - Click "Environment Variables" button

3. **Add New Variables:**
   - Click "New" under "User variables"
   - Variable name: `BINANCE_API_KEY`
   - Variable value: [Your API key]
   - Click OK
   
   - Repeat for `BINANCE_API_SECRET`

4. **Restart PowerShell/Terminal** for changes to take effect

## 🔐 Step 3: Verify Your Setup

Run this command to test your API connection:

```bash
python -c "from config import Config; c = Config(); print('API Key:', c.BINANCE_API_KEY[:10] + '...' if c.BINANCE_API_KEY else 'NOT SET'); print('Secret:', c.BINANCE_API_SECRET[:10] + '...' if c.BINANCE_API_SECRET else 'NOT SET')"
```

**Expected output:**
```
API Key: abcdef1234...
Secret: xyz9876543...
```

If you see `NOT SET`, your keys aren't loaded properly.

## 📊 Current Configuration

```
📁 .env                  ← Your API keys (NEVER share!)
📁 .env.example          ← Template (safe to share)
📁 .gitignore            ← Prevents .env from being uploaded
```

## 🚨 Security Best Practices

### ✅ DO:
- ✅ Keep API keys in `.env` file
- ✅ NEVER share your `.env` file
- ✅ Enable IP whitelist on Binance (recommended)
- ✅ Use "Reading" only permission for paper trading
- ✅ Test with small amounts first (when going live)
- ✅ Regenerate keys if compromised

### ❌ DON'T:
- ❌ NEVER enable "Enable Withdrawals" permission
- ❌ NEVER commit `.env` to git
- ❌ NEVER share your Secret Key
- ❌ Don't use same keys for multiple bots
- ❌ Don't screenshot keys
- ❌ Don't paste keys in Discord/Slack

## 🎯 API Key Permissions by Mode

### Paper Trading (Current - Simulated):
```
✅ Enable Reading          (get market data)
❌ Enable Spot Trading     (not needed for simulation)
❌ Enable Withdrawals      (NEVER enable)
```

### Live Trading (Real Money - Future):
```
✅ Enable Reading          (get market data)
✅ Enable Spot Trading     (execute real trades)
❌ Enable Withdrawals      (NEVER enable for security)
```

## 🔄 Switching Between Paper and Live Trading

In your `.env` file, change:

```bash
# Paper Trading (Simulated - Safe)
TRADING_MODE=paper

# Live Trading (Real Money - Use with caution!)
TRADING_MODE=live
```

**⚠️ WARNING:** Always test extensively in paper mode before switching to live!

## 🛡️ IP Whitelist (Highly Recommended)

1. Go to Binance API Management
2. Click "Edit" on your API key
3. Enable "Restrict access to trusted IPs only"
4. Add your current IP address:
   ```bash
   # Find your public IP
   curl https://api.ipify.org
   ```
5. Save changes

This prevents anyone else from using your API keys, even if they're stolen.

## 🔧 Troubleshooting

### "API key not set" error:
```bash
# Check if .env file exists
Get-Item .env

# Check if keys are in .env
Get-Content .env | Select-String "BINANCE"
```

### "Invalid API key" error:
- Double-check you copied the full key (no spaces)
- Ensure key hasn't been deleted from Binance
- Check permissions are enabled
- Verify IP whitelist (if enabled) includes your IP

### "Signature verification failed":
- Make sure Secret Key is correct
- Check system time is synchronized
- Restart the bot after changing keys

## 📞 Need Help?

If you encounter issues:
1. Check the `.env` file is in the project root
2. Verify no extra spaces in keys
3. Restart the bot after changes
4. Check Binance API Management for key status

## ✨ Example .env File

```bash
# Your .env file should look like this:
BINANCE_API_KEY=K6j8mP3vT9xZ2nR5wQ1yB4cD7fG0hL8sA6eF3gH1jK9mN2pQ5rS8tU1vW4xY7zA0
BINANCE_API_SECRET=N2pQ5rS8tU1vW4xY7zA0B3cD6eF9gH2jK5mN8pQ1rS4tU7vW0xY3zA6bC9dE2fG5

TRADING_MODE=paper
TRADING_PAIRS=BTC/USDT,ETH/USDT,SOL/USDT
```

(These are fake keys for example only - use your real keys!)

---

**🎉 Once set up, your bot will automatically use these keys when it starts!**

**Remember:** 
- Keys in `.env` are loaded automatically
- No need to edit Python code
- Keep `.env` file secure and private
- Test with paper trading first!

