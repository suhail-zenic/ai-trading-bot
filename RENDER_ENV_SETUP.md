# Render Environment Variables Setup

## Required Environment Variables for Live Trading

Click **"Add"** button under "Environment Variables" and add each of these:

### 1. Trading Mode
```
Key: TRADING_MODE
Value: live
```

### 2. Binance API Keys (REQUIRED)
```
Key: BINANCE_API_KEY
Value: [paste your actual API key from Binance]
```

```
Key: BINANCE_API_SECRET
Value: [paste your actual API secret from Binance]
```

### 3. Trading Configuration
```
Key: INITIAL_CAPITAL
Value: 22.50
```

```
Key: TRADING_PAIRS
Value: BTC/USDT
```

```
Key: POSITION_SIZE_PCT
Value: 0.95
```

```
Key: MAX_POSITIONS
Value: 1
```

```
Key: STOP_LOSS_PCT
Value: 0.015
```

```
Key: TAKE_PROFIT_PCT
Value: 0.04
```

```
Key: TRADING_CYCLE_MINUTES
Value: 15
```

```
Key: MAX_DAILY_LOSS
Value: 5
```

```
Key: PREDICTION_CONFIDENCE_THRESHOLD
Value: 0.55
```

## After Adding All Variables

1. **Click "Save Changes"** at the bottom of the page
2. Render will automatically redeploy (takes 2-3 minutes)
3. Check the **"Logs"** tab after deployment
4. Look for: `STARTING CRYPTO TRADING BOT - LIVE MODE (REAL MONEY!)`

## Verification

Once deployed, your bot should:
- ✅ Start in LIVE mode
- ✅ Connect to Binance with real API keys
- ✅ Place real orders with real money
- ✅ Show "LIVE" status in the dashboard

## Important Notes

- **DO NOT** share these API keys with anyone
- Make sure your Binance API keys have **Spot Trading** enabled
- Start with small capital (₹2000 = ~22.50 USDT)
- Monitor the bot closely for the first few trades

## Troubleshooting

If bot still runs in paper mode after deployment:
1. Check if all environment variables are saved
2. Look at logs for any errors
3. Try manually redeploying: Click "Manual Deploy" → "Clear build cache & deploy"

