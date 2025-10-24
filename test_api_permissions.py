"""
Test API permissions and balance fetch
"""
import ccxt
from config import Config

config = Config()

print("="*60)
print("TESTING API KEY PERMISSIONS")
print("="*60)
print()

# Initialize exchange
exchange = ccxt.binance({
    'apiKey': config.BINANCE_API_KEY,
    'secret': config.BINANCE_API_SECRET,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

print(f"API Key (first 20 chars): {config.BINANCE_API_KEY[:20]}...")
print(f"Exchange: {exchange.name}")
print()

# Test 1: Public data (should work)
print("Test 1: Fetching public ticker (no auth needed)")
try:
    ticker = exchange.fetch_ticker('BTC/USDT')
    print(f"✅ SUCCESS: BTC price = ${ticker['last']:,.2f}")
except Exception as e:
    print(f"❌ FAILED: {e}")

print()

# Test 2: Account balance (needs auth)
print("Test 2: Fetching account balance (needs auth)")
try:
    balance = exchange.fetch_balance()
    print("✅ SUCCESS: Balance fetched!")
    print()
    
    # Show USDT balance
    if 'USDT' in balance:
        usdt = balance['USDT']
        print(f"USDT Balance:")
        print(f"  Total: {usdt.get('total', 0):.2f} USDT")
        print(f"  Free:  {usdt.get('free', 0):.2f} USDT")
        print(f"  Used:  {usdt.get('used', 0):.2f} USDT")
    else:
        print("No USDT found in balance")
        
    print()
    print("🎉 Your API key has proper permissions!")
    
except ccxt.AuthenticationError as e:
    print(f"❌ AUTHENTICATION ERROR: {e}")
    print()
    print("Possible reasons:")
    print("  1. API key/secret incorrect")
    print("  2. IP not whitelisted (if IP restriction enabled)")
    print("  3. Permissions not enabled properly")
    print()
    print("Solutions:")
    print("  - Wait 5-10 minutes for changes to propagate")
    print("  - Check IP whitelist settings")
    print("  - Try creating a NEW API key")
    
except ccxt.PermissionDenied as e:
    print(f"❌ PERMISSION DENIED: {e}")
    print()
    print("Your API key doesn't have the required permissions.")
    print()
    print("Make sure you enabled:")
    print("  ✅ Enable Reading")
    print("  ✅ Enable Spot & Margin Trading")
    
except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {e}")

print()
print("="*60)

