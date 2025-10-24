import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime
import logging
from config import Config

logger = logging.getLogger(__name__)

class RiskManager:
    """Manages trading risk and position sizing"""
    
    def __init__(self):
        self.config = Config()
        self.daily_pnl = 0
        self.open_positions = {}
        self.trade_history = []
        self.daily_reset_time = datetime.now().date()
        
    def reset_daily_metrics(self):
        """Reset daily metrics if it's a new day"""
        current_date = datetime.now().date()
        if current_date > self.daily_reset_time:
            self.daily_pnl = 0
            self.daily_reset_time = current_date
            logger.info("Daily metrics reset")
    
    def calculate_position_size(self, capital: float, current_price: float, 
                               stop_loss_pct: float, confidence: float = 0.5) -> Dict:
        """
        Calculate optimal position size using Kelly Criterion and risk management
        
        Args:
            capital: Available capital
            current_price: Current asset price
            stop_loss_pct: Stop loss percentage (e.g., 0.05 for 5%)
            confidence: Confidence in the trade (0-1)
        
        Returns:
            Dict with position size information
        """
        try:
            # Maximum risk per trade
            max_risk_amount = capital * self.config.MAX_PORTFOLIO_RISK
            
            # Kelly Criterion adjustment
            # Kelly = (Win_Prob * Win_Amount - Loss_Prob * Loss_Amount) / Win_Amount
            win_prob = 0.5 + (confidence - 0.5) * 0.8  # Scale confidence to win probability
            loss_prob = 1 - win_prob
            
            # Assume risk/reward ratio of 3:1
            win_amount = stop_loss_pct * 3
            loss_amount = stop_loss_pct
            
            kelly_fraction = (win_prob * win_amount - loss_prob * loss_amount) / win_amount
            kelly_fraction = max(0, min(0.25, kelly_fraction))  # Cap at 25% (half Kelly)
            
            # Calculate position size
            kelly_position_size = (capital * kelly_fraction) / current_price
            risk_based_position_size = max_risk_amount / (current_price * stop_loss_pct)
            
            # Use the more conservative approach
            position_size = min(kelly_position_size, risk_based_position_size)
            
            # Adjust based on confidence
            position_size *= confidence
            
            position_value = position_size * current_price
            
            return {
                'position_size': position_size,
                'position_value': position_value,
                'risk_amount': position_value * stop_loss_pct,
                'kelly_fraction': kelly_fraction,
                'win_probability': win_prob,
                'recommended_stop_loss': current_price * (1 - stop_loss_pct),
                'recommended_take_profit': current_price * (1 + stop_loss_pct * 3)
            }
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return {'position_size': 0, 'position_value': 0, 'risk_amount': 0}
    
    def should_enter_trade(self, signal: str, confidence: float, current_price: float) -> Dict:
        """
        Determine if we should enter a trade based on risk parameters
        
        Returns:
            Dict with decision and reasoning
        """
        self.reset_daily_metrics()
        
        reasons = []
        can_trade = True
        
        # Check daily loss limit
        if abs(self.daily_pnl) >= self.config.MAX_DAILY_LOSS:
            can_trade = False
            reasons.append(f"Daily loss limit reached: ${self.daily_pnl:.2f}")
        
        # Check max open positions
        if len(self.open_positions) >= self.config.MAX_OPEN_POSITIONS:
            can_trade = False
            reasons.append(f"Max open positions reached: {len(self.open_positions)}")
        
        # Check signal strength
        if signal == 'HOLD':
            can_trade = False
            reasons.append("Signal is HOLD")
        
        # Check confidence threshold
        if confidence < self.config.PREDICTION_CONFIDENCE_THRESHOLD:
            can_trade = False
            reasons.append(f"Confidence too low: {confidence:.2%} < {self.config.PREDICTION_CONFIDENCE_THRESHOLD:.2%}")
        
        # Check volatility (if we have historical data)
        # High volatility = reduce position size or skip
        
        if can_trade:
            reasons.append("All risk checks passed")
        
        return {
            'can_trade': can_trade,
            'reasons': reasons,
            'daily_pnl': self.daily_pnl,
            'open_positions': len(self.open_positions),
            'risk_score': self._calculate_risk_score()
        }
    
    def add_position(self, symbol: str, side: str, entry_price: float, 
                     quantity: float, stop_loss: float, take_profit: float):
        """Add a new position"""
        position_id = f"{symbol}_{datetime.now().timestamp()}"
        
        self.open_positions[position_id] = {
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'quantity': quantity,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_time': datetime.now(),
            'pnl': 0
        }
        
        logger.info(f"Position opened: {position_id} - {side} {quantity} {symbol} @ {entry_price}")
        return position_id
    
    def update_position_pnl(self, position_id: str, current_price: float):
        """Update position P&L"""
        if position_id not in self.open_positions:
            return
        
        position = self.open_positions[position_id]
        
        if position['side'] == 'BUY':
            pnl = (current_price - position['entry_price']) * position['quantity']
        else:  # SELL/SHORT
            pnl = (position['entry_price'] - current_price) * position['quantity']
        
        position['pnl'] = pnl
        position['current_price'] = current_price
    
    def check_exit_conditions(self, position_id: str, current_price: float) -> Dict:
        """Check if position should be closed"""
        if position_id not in self.open_positions:
            return {'should_exit': False, 'reason': 'Position not found'}
        
        position = self.open_positions[position_id]
        
        # Check stop loss
        if position['side'] == 'BUY' and current_price <= position['stop_loss']:
            return {'should_exit': True, 'reason': 'Stop loss hit', 'type': 'STOP_LOSS'}
        elif position['side'] == 'SELL' and current_price >= position['stop_loss']:
            return {'should_exit': True, 'reason': 'Stop loss hit', 'type': 'STOP_LOSS'}
        
        # Check take profit
        if position['side'] == 'BUY' and current_price >= position['take_profit']:
            return {'should_exit': True, 'reason': 'Take profit hit', 'type': 'TAKE_PROFIT'}
        elif position['side'] == 'SELL' and current_price <= position['take_profit']:
            return {'should_exit': True, 'reason': 'Take profit hit', 'type': 'TAKE_PROFIT'}
        
        # Check time-based exit (optional: close after X hours)
        time_open = (datetime.now() - position['entry_time']).total_seconds() / 3600
        if time_open > 24:  # Close after 24 hours
            return {'should_exit': True, 'reason': 'Time limit reached', 'type': 'TIME_EXIT'}
        
        return {'should_exit': False, 'reason': 'No exit condition met'}
    
    def close_position(self, position_id: str, exit_price: float, reason: str = 'Manual'):
        """Close a position"""
        if position_id not in self.open_positions:
            return None
        
        position = self.open_positions[position_id]
        self.update_position_pnl(position_id, exit_price)
        
        trade_result = {
            'position_id': position_id,
            'symbol': position['symbol'],
            'side': position['side'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'quantity': position['quantity'],
            'pnl': position['pnl'],
            'entry_time': position['entry_time'],
            'exit_time': datetime.now(),
            'duration': (datetime.now() - position['entry_time']).total_seconds() / 3600,
            'exit_reason': reason
        }
        
        # Update daily P&L
        self.daily_pnl += position['pnl']
        
        # Add to history
        self.trade_history.append(trade_result)
        
        # Remove from open positions
        del self.open_positions[position_id]
        
        logger.info(f"Position closed: {position_id} - P&L: ${position['pnl']:.2f} - Reason: {reason}")
        
        return trade_result
    
    def _calculate_risk_score(self) -> float:
        """Calculate overall risk score (0-100, higher is riskier)"""
        risk_score = 0
        
        # Daily loss component
        if self.config.MAX_DAILY_LOSS > 0:
            loss_ratio = abs(self.daily_pnl) / self.config.MAX_DAILY_LOSS
            risk_score += min(50, loss_ratio * 50)
        
        # Position count component
        position_ratio = len(self.open_positions) / self.config.MAX_OPEN_POSITIONS
        risk_score += position_ratio * 30
        
        # Add more risk factors here
        
        return min(100, risk_score)
    
    def get_portfolio_summary(self, current_prices: Dict[str, float]) -> Dict:
        """Get portfolio summary"""
        total_value = 0
        total_pnl = 0
        
        for pos_id, position in self.open_positions.items():
            symbol = position['symbol']
            if symbol in current_prices:
                self.update_position_pnl(pos_id, current_prices[symbol])
                total_value += position['quantity'] * current_prices[symbol]
                total_pnl += position['pnl']
        
        return {
            'open_positions': len(self.open_positions),
            'total_position_value': total_value,
            'unrealized_pnl': total_pnl,
            'daily_pnl': self.daily_pnl,
            'total_trades': len(self.trade_history),
            'risk_score': self._calculate_risk_score(),
            'positions': self.open_positions
        }
    
    def get_performance_stats(self) -> Dict:
        """Calculate performance statistics"""
        if not self.trade_history:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'total_pnl': 0
            }
        
        df = pd.DataFrame(self.trade_history)
        
        winning_trades = df[df['pnl'] > 0]
        losing_trades = df[df['pnl'] < 0]
        
        total_wins = len(winning_trades)
        total_losses = len(losing_trades)
        total_trades = len(df)
        
        win_rate = total_wins / total_trades if total_trades > 0 else 0
        avg_win = winning_trades['pnl'].mean() if not winning_trades.empty else 0
        avg_loss = abs(losing_trades['pnl'].mean()) if not losing_trades.empty else 0
        
        total_profit = winning_trades['pnl'].sum() if not winning_trades.empty else 0
        total_loss = abs(losing_trades['pnl'].sum()) if not losing_trades.empty else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        return {
            'total_trades': total_trades,
            'winning_trades': total_wins,
            'losing_trades': total_losses,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_pnl': df['pnl'].sum(),
            'best_trade': df['pnl'].max(),
            'worst_trade': df['pnl'].min(),
            'avg_trade_duration': df['duration'].mean()
        }

