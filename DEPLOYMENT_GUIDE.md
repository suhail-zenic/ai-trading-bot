# 🚀 Free Deployment Guide for AI Crypto Trading Bot

This guide will help you deploy your AI trading bot for **FREE** on various platforms.

---

## 🎯 Best Free Deployment Options

### Option 1: **Render.com** (Recommended ⭐)
- ✅ Free tier with 750 hours/month
- ✅ Automatic deployments from GitHub
- ✅ Easy setup
- ✅ Persistent storage

### Option 2: **Railway.app**
- ✅ $5 free credit monthly
- ✅ Great for continuous running apps
- ✅ Simple deployment

### Option 3: **Fly.io**
- ✅ Free tier available
- ✅ Good performance
- ✅ Global deployment

---

## 📋 Option 1: Deploy to Render.com (EASIEST)

### Step 1: Prepare Your Code
1. Create a GitHub account if you don't have one: https://github.com
2. Create a new repository (e.g., "ai-trading-bot")
3. Push your code to GitHub:

```bash
git init
git add .
git commit -m "Initial commit - AI Trading Bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-trading-bot.git
git push -u origin main
```

### Step 2: Deploy to Render
1. Go to https://render.com and sign up (use your GitHub account)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `ai-trading-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Select **"Free"**

5. Click **"Create Web Service"**

### Step 3: Configure Environment Variables (Optional)
In Render dashboard, go to **Environment** and add:
- `TRADING_MODE` = `paper`
- `TRADING_PAIRS` = `BTC/USDT,ETH/USDT,SOL/USDT`

### Step 4: Access Your Bot
Once deployed, Render will give you a URL like:
```
https://ai-trading-bot-xxxx.onrender.com
```

Your bot is now live! 🎉

---

## 📋 Option 2: Deploy to Railway.app

### Step 1: Push to GitHub (same as above)

### Step 2: Deploy to Railway
1. Go to https://railway.app and sign up
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will auto-detect Python and deploy
5. Add environment variables in the **Variables** tab

### Step 3: Access Your App
Railway will provide a URL for your deployed app.

---

## 📋 Option 3: Deploy to Fly.io

### Step 1: Install Fly CLI
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Mac/Linux
curl -L https://fly.io/install.sh | sh
```

### Step 2: Login and Launch
```bash
fly auth login
fly launch
```

Follow the prompts and your app will be deployed!

---

## 🔧 Important Notes for Free Deployment

### ⚠️ Limitations of Free Tiers:
1. **Render Free**: App sleeps after 15 min of inactivity (wakes up on request)
2. **Railway**: Limited to $5/month credit
3. **Fly.io**: Limited resources on free tier

### 💡 To Keep Bot Running 24/7 (Free):
Use **UptimeRobot** (free) to ping your app every 5 minutes:
1. Go to https://uptimerobot.com (free account)
2. Add your Render URL as a monitor
3. Set interval to 5 minutes
4. Your bot will never sleep! 🎯

---

## 🎨 Alternative: Deploy to Replit (Simplest!)

### Quick Deploy on Replit:
1. Go to https://replit.com
2. Click **"Create Repl"** → **"Import from GitHub"**
3. Paste your GitHub repo URL
4. Click **"Import from GitHub"**
5. Click **"Run"** button
6. Your bot is live instantly! ✨

**Note**: Keep the Replit tab open or use Replit's "Always On" feature (paid).

---

## 🔐 Environment Variables Setup

For production deployment, set these environment variables:

```
TRADING_MODE=paper
TRADING_PAIRS=BTC/USDT,ETH/USDT,SOL/USDT
DEFAULT_TRADE_AMOUNT=100
MAX_PORTFOLIO_RISK=0.02
STOP_LOSS_PERCENTAGE=0.05
TAKE_PROFIT_PERCENTAGE=0.15
MAX_DAILY_LOSS=500
MAX_OPEN_POSITIONS=5
PREDICTION_CONFIDENCE_THRESHOLD=0.55
```

**For live trading** (add your exchange API keys):
```
TRADING_MODE=live
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

---

## 📊 Post-Deployment Checklist

✅ Bot is accessible via the provided URL  
✅ Dashboard loads correctly  
✅ Can start/stop bot from web interface  
✅ Trading in paper mode (for testing)  
✅ Environment variables are set  
✅ UptimeRobot monitor added (optional)  

---

## 🆘 Troubleshooting

### App won't start?
- Check logs in your deployment platform
- Verify all dependencies in `requirements.txt` are installed
- Ensure `gunicorn` is in requirements.txt

### Bot keeps sleeping?
- Use UptimeRobot to ping your app every 5 minutes
- Or upgrade to a paid plan for always-on service

### Need live trading?
- Add your exchange API keys as environment variables
- Set `TRADING_MODE=live`
- **Test thoroughly in paper mode first!**

---

## 🎉 Success!

Your AI Crypto Trading Bot is now deployed and accessible worldwide!

**Dashboard URL**: Your deployment platform will provide this  
**Start Trading**: Click "Start Bot" in the dashboard  
**Monitor**: Watch real-time performance and P&L  

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Fly.io Documentation](https://fly.io/docs)
- [UptimeRobot Guide](https://uptimerobot.com/help)

---

**Need help?** Check the logs in your deployment platform's dashboard!

Happy Trading! 🚀📈

