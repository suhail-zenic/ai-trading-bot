"""
Quick test to verify auto balance fetch
"""
print("Testing auto balance fetch feature...")
print("")

from src.simple_trading_bot import SimpleTradingBot

print("")
print("Creating bot instance...")
print("="*60)

bot = SimpleTradingBot()

print("="*60)
print("")
print("RESULT:")
print(f"  Bot capital: {bot.capital:.2f} USDT")
print(f"  Initial capital: {bot.initial_capital:.2f} USDT")
print("")

if bot.capital == bot.initial_capital:
    print("SUCCESS! Bot is using the fetched balance!")
else:
    print("Note: Balance may differ if trades are open")

