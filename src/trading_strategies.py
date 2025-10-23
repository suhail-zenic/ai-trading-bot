import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging
from config import Config

logger = logging.getLogger(__name__)

class TradingStrategies:
    """Collection of trading strategies"""
    
    def __init__(self):
        self.config = Config()
    
    def trend_following_strategy(self, df: pd.DataFrame) -> Dict:
        """
        Trend Following Strategy using EMAs and MACD
        """
        try:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            signals = []
            
            # EMA Crossover
            if latest['ema_9'] > latest['ema_21'] and prev['ema_9'] <= prev['ema_21']:
                signals.append({'type': 'BUY', 'strength': 0.8, 'reason': 'EMA 9/21 Golden Cross'})
            elif latest['ema_9'] < latest['ema_21'] and prev['ema_9'] >= prev['ema_21']:
                signals.append({'type': 'SELL', 'strength': 0.8, 'reason': 'EMA 9/21 Death Cross'})
            
            # MACD Crossover
            if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
                signals.append({'type': 'BUY', 'strength': 0.7, 'reason': 'MACD Bullish Crossover'})
            elif latest['macd'] < latest['macd_signal'] and prev['macd'] >= prev['macd_signal']:
                signals.append({'type': 'SELL', 'strength': 0.7, 'reason': 'MACD Bearish Crossover'})
            
            # Trend Confirmation with ADX
            if latest['adx'] > 25:  # Strong trend
                if latest['adx_pos'] > latest['adx_neg']:
                    signals.append({'type': 'BUY', 'strength': 0.6, 'reason': 'Strong Uptrend (ADX)'})
                else:
                    signals.append({'type': 'SELL', 'strength': 0.6, 'reason': 'Strong Downtrend (ADX)'})
            
            return self._aggregate_signals(signals, 'Trend Following')
            
        except Exception as e:
            logger.error(f"Error in trend following strategy: {e}")
            return {'signal': 'HOLD', 'confidence': 0, 'strategy': 'Trend Following'}
    
    def mean_reversion_strategy(self, df: pd.DataFrame) -> Dict:
        """
        Mean Reversion Strategy using Bollinger Bands and RSI
        """
        try:
            latest = df.iloc[-1]
            
            signals = []
            
            # Bollinger Bands
            if latest['close'] < latest['bb_lower']:
                oversold_strength = (latest['bb_lower'] - latest['close']) / latest['bb_lower']
                signals.append({'type': 'BUY', 'strength': min(0.9, 0.5 + oversold_strength), 
                              'reason': 'Price below lower BB'})
            elif latest['close'] > latest['bb_upper']:
                overbought_strength = (latest['close'] - latest['bb_upper']) / latest['bb_upper']
                signals.append({'type': 'SELL', 'strength': min(0.9, 0.5 + overbought_strength),
                              'reason': 'Price above upper BB'})
            
            # RSI
            if latest['rsi'] < 30:
                signals.append({'type': 'BUY', 'strength': 0.8, 'reason': 'RSI Oversold'})
            elif latest['rsi'] > 70:
                signals.append({'type': 'SELL', 'strength': 0.8, 'reason': 'RSI Overbought'})
            
            # Stochastic
            if latest['stoch_k'] < 20 and latest['stoch_d'] < 20:
                signals.append({'type': 'BUY', 'strength': 0.7, 'reason': 'Stochastic Oversold'})
            elif latest['stoch_k'] > 80 and latest['stoch_d'] > 80:
                signals.append({'type': 'SELL', 'strength': 0.7, 'reason': 'Stochastic Overbought'})
            
            # Williams %R
            if latest['williams_r'] < -80:
                signals.append({'type': 'BUY', 'strength': 0.6, 'reason': 'Williams %R Oversold'})
            elif latest['williams_r'] > -20:
                signals.append({'type': 'SELL', 'strength': 0.6, 'reason': 'Williams %R Overbought'})
            
            return self._aggregate_signals(signals, 'Mean Reversion')
            
        except Exception as e:
            logger.error(f"Error in mean reversion strategy: {e}")
            return {'signal': 'HOLD', 'confidence': 0, 'strategy': 'Mean Reversion'}
    
    def breakout_strategy(self, df: pd.DataFrame) -> Dict:
        """
        Breakout Strategy using Support/Resistance and Volume
        """
        try:
            latest = df.iloc[-1]
            
            signals = []
            
            # Support/Resistance Breakout
            resistance = df['high'].rolling(window=20).max().iloc[-1]
            support = df['low'].rolling(window=20).min().iloc[-1]
            
            # Volume confirmation
            avg_volume = df['volume'].rolling(window=20).mean().iloc[-1]
            volume_spike = latest['volume'] > avg_volume * 1.5
            
            if latest['close'] > resistance and volume_spike:
                signals.append({'type': 'BUY', 'strength': 0.9, 'reason': 'Resistance Breakout with Volume'})
            elif latest['close'] < support and volume_spike:
                signals.append({'type': 'SELL', 'strength': 0.9, 'reason': 'Support Breakdown with Volume'})
            
            # Price momentum
            if latest['price_momentum_5'] > 0.03 and volume_spike:
                signals.append({'type': 'BUY', 'strength': 0.7, 'reason': 'Strong Upward Momentum'})
            elif latest['price_momentum_5'] < -0.03 and volume_spike:
                signals.append({'type': 'SELL', 'strength': 0.7, 'reason': 'Strong Downward Momentum'})
            
            return self._aggregate_signals(signals, 'Breakout')
            
        except Exception as e:
            logger.error(f"Error in breakout strategy: {e}")
            return {'signal': 'HOLD', 'confidence': 0, 'strategy': 'Breakout'}
    
    def volume_analysis_strategy(self, df: pd.DataFrame) -> Dict:
        """
        Volume-based Strategy using OBV and Volume trends
        """
        try:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            signals = []
            
            # OBV trend
            obv_slope = (latest['obv'] - df['obv'].iloc[-20]) / 20
            if obv_slope > 0 and latest['close'] > prev['close']:
                signals.append({'type': 'BUY', 'strength': 0.7, 'reason': 'Rising OBV with Price'})
            elif obv_slope < 0 and latest['close'] < prev['close']:
                signals.append({'type': 'SELL', 'strength': 0.7, 'reason': 'Falling OBV with Price'})
            
            # VWAP
            if latest['close'] > latest['vwap'] and prev['close'] <= prev['vwap']:
                signals.append({'type': 'BUY', 'strength': 0.6, 'reason': 'Price crossed above VWAP'})
            elif latest['close'] < latest['vwap'] and prev['close'] >= prev['vwap']:
                signals.append({'type': 'SELL', 'strength': 0.6, 'reason': 'Price crossed below VWAP'})
            
            return self._aggregate_signals(signals, 'Volume Analysis')
            
        except Exception as e:
            logger.error(f"Error in volume analysis strategy: {e}")
            return {'signal': 'HOLD', 'confidence': 0, 'strategy': 'Volume Analysis'}
    
    def ml_enhanced_strategy(self, df: pd.DataFrame, ml_prediction: Dict) -> Dict:
        """
        ML-Enhanced Strategy combining traditional signals with ML predictions
        """
        try:
            # Get traditional strategy signals
            trend = self.trend_following_strategy(df)
            mean_rev = self.mean_reversion_strategy(df)
            breakout = self.breakout_strategy(df)
            volume = self.volume_analysis_strategy(df)
            
            # Weight each strategy
            strategies = [
                (trend, 0.3),
                (mean_rev, 0.25),
                (breakout, 0.25),
                (volume, 0.2)
            ]
            
            # Calculate weighted average
            buy_score = 0
            sell_score = 0
            
            for strategy, weight in strategies:
                if strategy['signal'] == 'BUY':
                    buy_score += strategy['confidence'] * weight
                elif strategy['signal'] == 'SELL':
                    sell_score += strategy['confidence'] * weight
            
            # Add ML prediction with high weight
            ml_weight = 0.4
            ml_pred = ml_prediction.get('prediction', 0.5)
            ml_conf = ml_prediction.get('confidence', 0)
            
            if ml_pred > 0.5:
                buy_score += (ml_pred - 0.5) * 2 * ml_conf * ml_weight
            else:
                sell_score += (0.5 - ml_pred) * 2 * ml_conf * ml_weight
            
            # Determine final signal
            if buy_score > sell_score + 0.2:
                signal = 'BUY'
                confidence = buy_score
            elif sell_score > buy_score + 0.2:
                signal = 'SELL'
                confidence = sell_score
            else:
                signal = 'HOLD'
                confidence = 1 - abs(buy_score - sell_score)
            
            return {
                'signal': signal,
                'confidence': min(1.0, confidence),
                'strategy': 'ML Enhanced',
                'components': {
                    'trend': trend,
                    'mean_reversion': mean_rev,
                    'breakout': breakout,
                    'volume': volume,
                    'ml_prediction': ml_prediction
                },
                'buy_score': buy_score,
                'sell_score': sell_score
            }
            
        except Exception as e:
            logger.error(f"Error in ML enhanced strategy: {e}")
            return {'signal': 'HOLD', 'confidence': 0, 'strategy': 'ML Enhanced'}
    
    def _aggregate_signals(self, signals: list, strategy_name: str) -> Dict:
        """Aggregate multiple signals into a single decision"""
        if not signals:
            return {'signal': 'HOLD', 'confidence': 0, 'strategy': strategy_name, 'reasons': []}
        
        buy_signals = [s for s in signals if s['type'] == 'BUY']
        sell_signals = [s for s in signals if s['type'] == 'SELL']
        
        buy_strength = sum(s['strength'] for s in buy_signals) / len(signals)
        sell_strength = sum(s['strength'] for s in sell_signals) / len(signals)
        
        if buy_strength > sell_strength + 0.2:
            signal = 'BUY'
            confidence = buy_strength
            reasons = [s['reason'] for s in buy_signals]
        elif sell_strength > buy_strength + 0.2:
            signal = 'SELL'
            confidence = sell_strength
            reasons = [s['reason'] for s in sell_signals]
        else:
            signal = 'HOLD'
            confidence = 1 - abs(buy_strength - sell_strength)
            reasons = ['Conflicting signals']
        
        return {
            'signal': signal,
            'confidence': confidence,
            'strategy': strategy_name,
            'reasons': reasons,
            'buy_strength': buy_strength,
            'sell_strength': sell_strength
        }

