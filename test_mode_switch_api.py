"""
Test Mode Switching API
Quick test to verify mode switching works via web API
"""
import requests
import json
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:5000"

print("\n" + "="*60)
print(f"{Fore.CYAN}{Style.BRIGHT}Mode Switching API Test")
print("="*60 + "\n")

print(f"{Fore.YELLOW}Prerequisites:")
print("  1. Web dashboard must be running (python app.py)")
print("  2. Bot must be stopped")
print("\n")

# Test 1: Get current mode
print(f"{Fore.YELLOW}[1/2] Getting current mode...")
try:
    response = requests.get(f"{BASE_URL}/api/mode", timeout=5)
    if response.status_code == 200:
        data = response.json()
        mode = data.get('mode', 'unknown')
        is_live = data.get('is_live', False)
        api_configured = data.get('api_configured', False)
        
        print(f"{Fore.GREEN}✅ Current mode retrieved")
        print(f"    Mode: {Fore.RED if is_live else Fore.GREEN}{mode.upper()}")
        print(f"    API Keys: {Fore.GREEN if api_configured else Fore.YELLOW}{'✓ Configured' if api_configured else '✗ Not configured'}")
        
        current_mode = mode
    else:
        print(f"{Fore.RED}✗ Failed: {response.status_code}")
        exit(1)
except requests.exceptions.ConnectionError:
    print(f"{Fore.RED}✗ Cannot connect to dashboard")
    print(f"{Fore.YELLOW}   Please start the dashboard: python app.py")
    exit(1)
except Exception as e:
    print(f"{Fore.RED}✗ Error: {e}")
    exit(1)

# Test 2: Switch mode (to opposite)
new_mode = 'paper' if current_mode == 'live' else 'live'
print(f"\n{Fore.YELLOW}[2/2] Testing mode switch to {new_mode.upper()}...")

try:
    response = requests.post(
        f"{BASE_URL}/api/mode/switch",
        json={'mode': new_mode},
        headers={'Content-Type': 'application/json'},
        timeout=5
    )
    
    data = response.json()
    
    if response.status_code == 200 and data.get('success'):
        print(f"{Fore.GREEN}✅ Mode switched successfully!")
        print(f"    New mode: {Fore.CYAN}{data.get('new_mode', '').upper()}")
        print(f"    Message: {Fore.CYAN}{data.get('message', '')}")
        if data.get('note'):
            print(f"    Note: {Fore.YELLOW}{data.get('note', '')}")
    else:
        print(f"{Fore.YELLOW}⚠ Switch failed (expected if bot is running)")
        print(f"    Message: {Fore.YELLOW}{data.get('message', '')}")
        
except Exception as e:
    print(f"{Fore.RED}✗ Error: {e}")

# Test 3: Verify new mode
print(f"\n{Fore.YELLOW}[3/3] Verifying current mode...")
try:
    response = requests.get(f"{BASE_URL}/api/mode", timeout=5)
    if response.status_code == 200:
        data = response.json()
        mode = data.get('mode', 'unknown')
        is_live = data.get('is_live', False)
        
        print(f"{Fore.GREEN}✅ Current mode verified")
        print(f"    Mode: {Fore.RED if is_live else Fore.GREEN}{mode.upper()}")
except Exception as e:
    print(f"{Fore.YELLOW}⚠ Could not verify: {e}")

# Summary
print("\n" + "="*60)
print(f"{Fore.GREEN}{Style.BRIGHT}Test Complete!")
print("="*60)

print(f"\n{Fore.CYAN}Available API Endpoints:")
print(f"  • GET  /api/mode - Get current mode")
print(f"  • POST /api/mode/switch - Switch mode")
print(f"  • POST /api/start - Start bot")
print(f"  • POST /api/stop - Stop bot")
print(f"  • GET  /api/status - Get bot status")

print(f"\n{Fore.CYAN}Browser Console Commands:")
print(f"  • Check mode:")
print(f"    {Fore.WHITE}fetch('/api/mode').then(r=>r.json()).then(console.log)")
print(f"\n  • Switch to paper:")
print(f"    {Fore.WHITE}fetch('/api/mode/switch',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{mode:'paper'}})}}).then(r=>r.json()).then(alert)")
print(f"\n  • Switch to live:")
print(f"    {Fore.WHITE}fetch('/api/mode/switch',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{mode:'live'}})}}).then(r=>r.json()).then(alert)")

print("\n" + "="*60 + "\n")

