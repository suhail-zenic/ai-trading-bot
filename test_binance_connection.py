"""
Quick test to check if Binance API is accessible
Run this to verify your VPN/Proxy is working
"""
import ccxt
import sys

print("\n" + "="*60)
print("BINANCE CONNECTION TEST")
print("="*60)

# Test 1: Direct connection
print("\n[Test 1] Testing direct connection to Binance...")
try:
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'timeout': 10000
    })
    ticker = exchange.fetch_ticker('BTC/USDT')
    price = ticker['last']
    print(f"✅ SUCCESS! Binance is accessible")
    print(f"   BTC/USDT Price: ${price:,.2f}")
    print(f"   No VPN/Proxy needed in your region!")
    sys.exit(0)
except Exception as e:
    error_msg = str(e)
    if '451' in error_msg:
        print(f"❌ BLOCKED: Binance returns HTTP 451 (Service Unavailable)")
        print(f"   Binance is blocked in your region")
    else:
        print(f"❌ ERROR: {error_msg[:200]}")

# Test 2: Check if VPN/Proxy is configured
print("\n[Test 2] Checking for VPN/Proxy configuration...")
import os
from dotenv import load_dotenv
load_dotenv()

http_proxy = os.getenv('HTTP_PROXY')
https_proxy = os.getenv('HTTPS_PROXY')

if http_proxy or https_proxy:
    print(f"✅ Proxy configured:")
    if http_proxy:
        print(f"   HTTP: {http_proxy[:30]}...")
    if https_proxy:
        print(f"   HTTPS: {https_proxy[:30]}...")
    
    print("\n[Test 3] Testing connection through proxy...")
    try:
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'timeout': 10000,
            'proxies': {
                'http': http_proxy,
                'https': https_proxy
            }
        })
        ticker = exchange.fetch_ticker('BTC/USDT')
        price = ticker['last']
        print(f"✅ SUCCESS! Binance accessible through proxy")
        print(f"   BTC/USDT Price: ${price:,.2f}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Proxy failed: {str(e)[:200]}")
        print(f"   Check your proxy configuration")
else:
    print(f"⚠️  No proxy configured")

# Summary
print("\n" + "="*60)
print("SOLUTION REQUIRED")
print("="*60)
print("\nBinance is blocked in your region. You need to:")
print("\n📝 Option 1: Use VPN (For Local Bot)")
print("   1. Download ProtonVPN: https://protonvpn.com")
print("   2. Connect to Singapore or Japan")
print("   3. Run this test again")
print("\n📝 Option 2: Use Proxy (For Render Deployment)")
print("   1. Get proxy from Webshare.io: https://www.webshare.io")
print("   2. Add to Render environment variables:")
print("      HTTPS_PROXY=http://user:pass@proxy-server:port")
print("   3. Redeploy on Render")
print("\n📖 Full Guide: See BINANCE_REGION_FIX.md")
print("\n" + "="*60)

sys.exit(1)

