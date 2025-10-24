"""
Web Dashboard for AI Crypto Trading Bot
Run with: python app.py
Access at: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
import logging
from collections import deque
import threading

from src.simple_trading_bot import SimpleTradingBot

# Setup logging with custom handler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)

# Global bot instance and logs
bot = None
web_logs = deque(maxlen=100)  # Store last 100 log messages

# Custom log handler to capture logs for web interface
class WebLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': record.levelname.lower(),
            'message': record.getMessage()
        }
        web_logs.append(log_entry)

# Add web log handler
web_handler = WebLogHandler()
logging.getLogger().addHandler(web_handler)

@app.route('/')
def index():
    """Main dashboard page - Premium Version"""
    return render_template('dashboard_premium.html')

@app.route('/classic')
def classic_dashboard():
    """Classic dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get bot status"""
    if bot is None:
        return jsonify({
            'status': 'stopped',
            'is_running': False,
            'is_healthy': False,
            'capital': 0,
            'portfolio': {
                'open_positions': 0,
                'unrealized_pnl': 0,
                'daily_pnl': 0
            },
            'stats': {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_pnl': 0
            },
            'health': {
                'last_heartbeat': None,
                'seconds_since_heartbeat': 0,
                'status_message': 'Bot not started'
            }
        })
    
    status = bot.get_status()
    
    # Calculate win rate
    win_rate = 0
    if status['num_trades'] > 0:
        winning_trades = sum(1 for trade in bot.trades if trade.get('profit', 0) > 0)
        win_rate = winning_trades / status['num_trades']
    
    # Calculate profit factor
    profit_factor = 0
    total_wins = sum(trade.get('profit', 0) for trade in bot.trades if trade.get('profit', 0) > 0)
    total_losses = abs(sum(trade.get('profit', 0) for trade in bot.trades if trade.get('profit', 0) < 0))
    if total_losses > 0:
        profit_factor = total_wins / total_losses
    
    # Health status message
    health_message = 'Healthy and active'
    if not status.get('is_healthy', False):
        health_message = 'Warning: No heartbeat for 10+ minutes'
    elif not status['running']:
        health_message = 'Bot stopped'
    
    # Calculate unrealized P&L from open positions only
    unrealized_pnl = 0
    for symbol, pos in bot.positions.items():
        try:
            ticker = bot.data_fetcher.get_ticker(symbol)
            if ticker:
                current_price = ticker['last']
                entry_price = pos.get('entry_price', current_price)
                amount = pos.get('amount', 0)
                position_pnl = (current_price - entry_price) * amount
                unrealized_pnl += position_pnl
        except:
            pass
    
    # Calculate daily P&L (from closed trades today)
    daily_pnl = 0
    today = datetime.now().date()
    for trade in bot.trades:
        try:
            trade_date = datetime.fromisoformat(trade.get('timestamp', '')).date()
            if trade_date == today:
                daily_pnl += trade.get('profit', 0)
        except:
            pass
    
    return jsonify({
        'status': 'running' if status['running'] else 'stopped',
        'is_running': status['running'],
        'is_healthy': status.get('is_healthy', False),
        'capital': status.get('total_value', status['capital']),  # Total account value
        'free_capital': status['capital'],  # Available cash
        'portfolio': {
            'open_positions': status['num_positions'],
            'unrealized_pnl': unrealized_pnl,  # Only from open positions
            'daily_pnl': daily_pnl  # Only today's closed trades
        },
        'stats': {
            'total_trades': status['num_trades'],
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_pnl': status['profit']  # Cumulative all-time P&L
        },
        'health': {
            'last_heartbeat': status.get('last_heartbeat'),
            'seconds_since_heartbeat': status.get('seconds_since_heartbeat', 0),
            'status_message': health_message
        }
    })

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    global bot
    
    if bot is not None and bot.running:
        return jsonify({'success': False, 'message': 'Bot is already running'})
    
    try:
        bot = SimpleTradingBot()
        bot.start()
        
        return jsonify({'success': True, 'message': 'Bot started successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    global bot
    
    if bot is None or not bot.running:
        return jsonify({'success': False, 'message': 'Bot is not running'})
    
    try:
        bot.stop()
        return jsonify({'success': True, 'message': 'Bot stopped successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/mode')
def get_mode():
    """Get current trading mode"""
    from config import Config
    config = Config()
    return jsonify({
        'mode': config.TRADING_MODE,
        'is_live': config.TRADING_MODE == 'live',
        'api_configured': bool(config.BINANCE_API_KEY and config.BINANCE_API_SECRET)
    })

@app.route('/api/mode/switch', methods=['POST'])
def switch_mode():
    """Switch trading mode (requires bot to be stopped)"""
    global bot
    
    # Check if bot is running
    if bot is not None and bot.running:
        return jsonify({
            'success': False, 
            'message': 'Please stop the bot before switching modes'
        })
    
    try:
        import os
        from pathlib import Path
        
        # Read current .env
        env_path = Path('.env')
        env_vars = {}
        
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        
        # Get requested mode from request
        data = request.get_json() or {}
        new_mode = data.get('mode', '').lower()
        
        if new_mode not in ['paper', 'live']:
            return jsonify({
                'success': False,
                'message': 'Invalid mode. Must be "paper" or "live"'
            })
        
        # Update mode
        env_vars['TRADING_MODE'] = new_mode
        
        # Write back to .env
        with open(env_path, 'w') as f:
            f.write("# AI Trading Bot Configuration\n")
            f.write(f"# Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        # Reload environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv(override=True)
        os.environ['TRADING_MODE'] = new_mode
        
        return jsonify({
            'success': True,
            'message': f'Switched to {new_mode.upper()} mode!',
            'new_mode': new_mode,
            'note': 'Mode updated - you can now start the bot'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/api/positions')
def get_positions():
    """Get open positions"""
    if bot is None:
        return jsonify({'positions': []})
    
    return jsonify({'positions': bot.get_positions()})

@app.route('/api/trades')
def get_trades():
    """Get trade history"""
    if bot is None:
        return jsonify({'trades': []})
    
    return jsonify({'trades': bot.get_trades()})

@app.route('/api/logs')
def get_logs():
    """Get recent log entries"""
    return jsonify({'logs': list(web_logs)})

@app.route('/api/market-data')
def get_market_data():
    """Get real-time market data"""
    try:
        from src.data_fetcher import MarketDataFetcher
        fetcher = MarketDataFetcher()
        
        market_data = []
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        
        for symbol in symbols:
            try:
                ticker = fetcher.get_ticker(symbol)
                if ticker:
                    market_data.append({
                        'symbol': symbol,
                        'price': ticker.get('last', 0),
                        'change_24h': ticker.get('percentage', 0),
                        'volume': ticker.get('baseVolume', 0)
                    })
            except Exception as e:
                logging.error(f"Error fetching {symbol}: {e}")
        
        return jsonify({'market_data': market_data})
    except Exception as e:
        logging.error(f"Error in market data endpoint: {e}")
        return jsonify({'market_data': []})

if __name__ == '__main__':
    import os
    
    # Get port from environment variable (for deployment platforms) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*60)
    print("AI CRYPTO TRADING BOT - WEB DASHBOARD")
    print("="*60)
    print(f"Dashboard URL: http://localhost:{port}")
    print("="*60 + "\n")
    
    # Use debug=False for production
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port, use_reloader=False)

