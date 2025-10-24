# Accessing Binance from Restricted Regions

## Problem
You're seeing this error:
```
[FAIL] Binance connection test failed: binance GET https://api.binance.com/api/v3/exchangeInfo 451
```

**Error 451 = "Service Unavailable for Legal Reasons"** - Binance is blocked in your region by IP address.

## Solutions

### **Solution 1: VPN (Recommended for Local Development)**

Use a VPN to connect from a Binance-friendly country.

#### **Step 1: Get a VPN**

**Free Options:**
- **ProtonVPN** - https://protonvpn.com (Free tier, no credit card)
- **Windscribe** - https://windscribe.com (10GB/month free)

**Paid Options (Better for Trading):**
- **NordVPN** - ~$3-12/month
- **ExpressVPN** - ~$8-12/month
- **Surfshark** - ~$2-12/month

#### **Step 2: Connect to Binance-Friendly Location**
Choose one of these VPN servers:
- 🇸🇬 **Singapore** (Best - closest to Binance servers, low latency)
- 🇯🇵 **Japan** (Good)
- 🇩🇪 **Germany** (Good)
- 🇬🇧 **UK** (Good)
- 🇳🇱 **Netherlands** (Good)

#### **Step 3: Test Connection**
```bash
# Run the bot locally with VPN connected
python app.py
```

You should see:
```
[OK] Successfully connected to Binance!
```

---

### **Solution 2: HTTP Proxy (For Render Deployment)**

For cloud deployment on Render, use a proxy service.

#### **Step 1: Get a Proxy Service**

**Recommended Proxy Providers:**

1. **Webshare.io** (Best for trading)
   - https://www.webshare.io
   - 10 free proxies (rotating)
   - $2.99/month for premium
   - Locations: Multiple countries

2. **ProxyRack**
   - https://www.proxyrack.com
   - $49/month for residential proxies
   - Good for Binance API

3. **Bright Data (formerly Luminati)**
   - https://brightdata.com
   - Premium service, more expensive
   - Very reliable

#### **Step 2: Get Proxy URL**

After signing up, you'll get a proxy URL like:
```
http://username:password@proxy-server.com:12345
```

Or for SOCKS5:
```
socks5://username:password@proxy-server.com:1080
```

#### **Step 3: Add to Render Environment Variables**

In Render Dashboard → Environment:

```
Key: HTTPS_PROXY
Value: http://username:password@your-proxy-server.com:12345
```

```
Key: HTTP_PROXY
Value: http://username:password@your-proxy-server.com:12345
```

**Important:** Choose a proxy server in a Binance-friendly country (Singapore, Japan, Germany, etc.)

#### **Step 4: Deploy**

Save changes → Render will redeploy with proxy → Bot will connect through proxy

---

### **Solution 3: Use Binance US (If in USA)**

If you're in the USA:
- Use **Binance.US** instead: https://www.binance.us
- Create account and get API keys
- Same bot works with Binance.US

---

### **Solution 4: VPN on Render (Advanced)**

You can run a VPN client on Render, but it's more complex:

1. Use WireGuard or OpenVPN
2. Configure through Render's buildpacks
3. Not officially supported, may violate Render's TOS

**Not recommended** - use proxy instead.

---

## Testing Your Connection

### **Test 1: Check if Binance is accessible**

```bash
curl -I https://api.binance.com/api/v3/ping
```

If you see `HTTP/2 451`, Binance is blocked.

### **Test 2: Check with VPN/Proxy**

With VPN connected or proxy configured:
```bash
python test_api_permissions.py
```

Should show:
```
[OK] Successfully connected to Binance!
```

---

## Costs Comparison

| Solution | Cost | Ease | Reliability |
|----------|------|------|-------------|
| **VPN (Local)** | Free-$12/mo | ⭐⭐⭐⭐⭐ Easy | ⭐⭐⭐⭐ Good |
| **Proxy (Render)** | $3-50/mo | ⭐⭐⭐ Medium | ⭐⭐⭐⭐⭐ Excellent |
| **Binance.US** | Free | ⭐⭐⭐⭐⭐ Easy | ⭐⭐⭐⭐⭐ Excellent |

---

## My Recommendation

### **For Local Development:**
✅ Use **ProtonVPN** (free) → Connect to Singapore → Run bot

### **For Render Deployment:**
✅ Use **Webshare.io** proxy ($2.99/month) → Add to Render env vars → Deploy

### **If in USA:**
✅ Just use **Binance.US** instead

---

## Troubleshooting

### Still getting 451 error?
- Make sure VPN is actually connected (check IP: https://whatismyipaddress.com)
- Try a different VPN server location
- Check if proxy is working: `curl -x your-proxy-url https://api.binance.com/api/v3/ping`

### Slow connection?
- Use Singapore VPN server (closest to Binance)
- Upgrade to paid VPN for better speeds
- Use dedicated proxy instead of shared

### Proxy not working on Render?
- Check proxy format: `http://user:pass@host:port`
- Make sure proxy supports HTTPS
- Test proxy locally first

---

## Summary

**You MUST use either:**
1. ✅ **VPN** (for local bot)
2. ✅ **Proxy** (for Render deployment)
3. ✅ **Binance.US** (if in USA)

**Without one of these, the bot CANNOT access Binance API from your region.**

Choose the solution that fits your needs and budget! 🚀

