import pandas as pd
import numpy as np
from typing import Dict, List, Callable
from datetime import datetime
import logging
from config import Config
from src.risk_manager import RiskManager

logger = logging.getLogger(__name__)

class Backtester:
    """Backtest trading strategies on historical data"""
    
    def __init__(self, initial_capital: float = 10000):
        self.config = Config()
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []
        
    def run_backtest(self, df: pd.DataFrame, strategy_func: Callable, 
                     symbol: str = 'BTC/USDT') -> Dict:
        """
        Run backtest on historical data
        
        Args:
            df: DataFrame with OHLCV and indicators
            strategy_func: Function that returns trading signals
            symbol: Trading pair symbol
        
        Returns:
            Dict with backtest results
        """
        logger.info(f"Running backtest on {len(df)} candles")
        
        self.capital = self.initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []
        
        risk_manager = RiskManager()
        
        for i in range(100, len(df)):  # Start after 100 candles for indicator warmup
            current_data = df.iloc[:i+1]
            current_price = df.iloc[i]['close']
            timestamp = df.index[i]
            
            # Get strategy signal
            signal_result = strategy_func(current_data)
            signal = signal_result.get('signal', 'HOLD')
            confidence = signal_result.get('confidence', 0)
            
            # Update existing positions
            for position in self.positions:
                position['current_price'] = current_price
                
                # Calculate P&L
                if position['side'] == 'LONG':
                    position['pnl'] = (current_price - position['entry_price']) * position['size']
                    pnl_pct = (current_price - position['entry_price']) / position['entry_price']
                else:
                    position['pnl'] = (position['entry_price'] - current_price) * position['size']
                    pnl_pct = (position['entry_price'] - current_price) / position['entry_price']
                
                # Check exit conditions
                should_exit = False
                exit_reason = ''
                
                if position['side'] == 'LONG':
                    if current_price <= position['stop_loss']:
                        should_exit = True
                        exit_reason = 'Stop Loss'
                    elif current_price >= position['take_profit']:
                        should_exit = True
                        exit_reason = 'Take Profit'
                elif position['side'] == 'SHORT':
                    if current_price >= position['stop_loss']:
                        should_exit = True
                        exit_reason = 'Stop Loss'
                    elif current_price <= position['take_profit']:
                        should_exit = True
                        exit_reason = 'Take Profit'
                
                if should_exit:
                    self._close_position(position, current_price, timestamp, exit_reason)
            
            # Remove closed positions
            self.positions = [p for p in self.positions if p.get('status') != 'CLOSED']
            
            # Check for new entry signals
            if len(self.positions) < self.config.MAX_OPEN_POSITIONS:
                if signal == 'BUY' and confidence >= self.config.PREDICTION_CONFIDENCE_THRESHOLD:
                    self._open_position('LONG', current_price, timestamp, confidence, symbol)
                elif signal == 'SELL' and confidence >= self.config.PREDICTION_CONFIDENCE_THRESHOLD:
                    self._open_position('SHORT', current_price, timestamp, confidence, symbol)
            
            # Record equity
            total_equity = self.capital
            for position in self.positions:
                total_equity += position.get('pnl', 0)
            
            self.equity_curve.append({
                'timestamp': timestamp,
                'equity': total_equity,
                'cash': self.capital,
                'positions': len(self.positions)
            })
        
        # Close all remaining positions at the end
        final_price = df.iloc[-1]['close']
        final_timestamp = df.index[-1]
        for position in self.positions:
            self._close_position(position, final_price, final_timestamp, 'Backtest End')
        
        return self._calculate_results()
    
    def _open_position(self, side: str, price: float, timestamp, 
                      confidence: float, symbol: str):
        """Open a new position"""
        # Calculate position size
        risk_amount = self.capital * self.config.MAX_PORTFOLIO_RISK
        stop_loss_pct = self.config.STOP_LOSS_PERCENTAGE
        
        position_size = (risk_amount / (price * stop_loss_pct)) * confidence
        position_value = position_size * price
        
        # Check if we have enough capital
        if position_value > self.capital * 0.95:  # Use max 95% of capital
            position_value = self.capital * 0.95
            position_size = position_value / price
        
        if position_value < self.capital * 0.01:  # Minimum 1% of capital
            return
        
        # Set stop loss and take profit
        if side == 'LONG':
            stop_loss = price * (1 - stop_loss_pct)
            take_profit = price * (1 + self.config.TAKE_PROFIT_PERCENTAGE)
        else:  # SHORT
            stop_loss = price * (1 + stop_loss_pct)
            take_profit = price * (1 - self.config.TAKE_PROFIT_PERCENTAGE)
        
        position = {
            'symbol': symbol,
            'side': side,
            'entry_price': price,
            'entry_time': timestamp,
            'size': position_size,
            'value': position_value,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'confidence': confidence,
            'status': 'OPEN',
            'pnl': 0
        }
        
        self.positions.append(position)
        self.capital -= position_value  # Deduct from available capital
        
        logger.debug(f"Opened {side} position at {price:.2f} with size {position_size:.4f}")
    
    def _close_position(self, position: Dict, exit_price: float, 
                       timestamp, reason: str):
        """Close a position"""
        if position['side'] == 'LONG':
            pnl = (exit_price - position['entry_price']) * position['size']
        else:
            pnl = (position['entry_price'] - exit_price) * position['size']
        
        position['exit_price'] = exit_price
        position['exit_time'] = timestamp
        position['pnl'] = pnl
        position['status'] = 'CLOSED'
        position['exit_reason'] = reason
        position['return_pct'] = pnl / position['value'] if position['value'] > 0 else 0
        
        self.capital += position['value'] + pnl  # Return capital plus P&L
        self.trades.append(position.copy())
        
        logger.debug(f"Closed {position['side']} position at {exit_price:.2f} - P&L: ${pnl:.2f}")
    
    def _calculate_results(self) -> Dict:
        """Calculate backtest results and performance metrics"""
        if not self.trades:
            return {
                'total_return': 0,
                'total_return_pct': 0,
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'message': 'No trades executed'
            }
        
        df_trades = pd.DataFrame(self.trades)
        df_equity = pd.DataFrame(self.equity_curve)
        
        # Overall performance
        final_equity = df_equity['equity'].iloc[-1]
        total_return = final_equity - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # Trade statistics
        winning_trades = df_trades[df_trades['pnl'] > 0]
        losing_trades = df_trades[df_trades['pnl'] < 0]
        
        total_trades = len(df_trades)
        winning_count = len(winning_trades)
        losing_count = len(losing_trades)
        win_rate = (winning_count / total_trades) * 100 if total_trades > 0 else 0
        
        avg_win = winning_trades['pnl'].mean() if not winning_trades.empty else 0
        avg_loss = abs(losing_trades['pnl'].mean()) if not losing_trades.empty else 0
        
        total_profit = winning_trades['pnl'].sum() if not winning_trades.empty else 0
        total_loss = abs(losing_trades['pnl'].sum()) if not losing_trades.empty else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        # Risk metrics
        returns = df_equity['equity'].pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        # Maximum drawdown
        cumulative = df_equity['equity'].cummax()
        drawdown = (df_equity['equity'] - cumulative) / cumulative
        max_drawdown = abs(drawdown.min()) * 100
        
        # Average trade duration
        df_trades['duration'] = (df_trades['exit_time'] - df_trades['entry_time']).dt.total_seconds() / 3600
        avg_duration = df_trades['duration'].mean()
        
        return {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'total_trades': total_trades,
            'winning_trades': winning_count,
            'losing_trades': losing_count,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'avg_trade_duration_hours': avg_duration,
            'best_trade': df_trades['pnl'].max(),
            'worst_trade': df_trades['pnl'].min(),
            'equity_curve': df_equity.to_dict('records'),
            'trades': df_trades.to_dict('records')
        }
    
    def print_results(self, results: Dict):
        """Print formatted backtest results"""
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"Initial Capital: ${results['initial_capital']:,.2f}")
        print(f"Final Equity: ${results['final_equity']:,.2f}")
        print(f"Total Return: ${results['total_return']:,.2f} ({results['total_return_pct']:.2f}%)")
        print(f"\nTotal Trades: {results['total_trades']}")
        print(f"Winning Trades: {results['winning_trades']}")
        print(f"Losing Trades: {results['losing_trades']}")
        print(f"Win Rate: {results['win_rate']:.2f}%")
        print(f"\nAverage Win: ${results['avg_win']:.2f}")
        print(f"Average Loss: ${results['avg_loss']:.2f}")
        print(f"Profit Factor: {results['profit_factor']:.2f}")
        print(f"\nSharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
        print(f"Avg Trade Duration: {results.get('avg_trade_duration_hours', 0):.2f} hours")
        print("="*60 + "\n")

