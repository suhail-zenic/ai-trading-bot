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

from src.simple_trading_bot import SimpleTradingBot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)

# Global bot instance
bot = None

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get bot status"""
    if bot is None:
        return jsonify({
            'status': 'stopped',
            'is_running': False,
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
    
    return jsonify({
        'status': 'running' if status['running'] else 'stopped',
        'is_running': status['running'],
        'capital': status['capital'],
        'portfolio': {
            'open_positions': status['num_positions'],
            'unrealized_pnl': status['profit'],
            'daily_pnl': status['profit']
        },
        'stats': {
            'total_trades': status['num_trades'],
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_pnl': status['profit']
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

