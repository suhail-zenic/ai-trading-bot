import pandas as pd
import numpy as np
from ta.trend import MACD, EMAIndicator, SMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, ROCIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Calculate various technical indicators for trading analysis"""
    
    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicators to the dataframe"""
        df = TechnicalIndicators.add_trend_indicators(df)
        df = TechnicalIndicators.add_momentum_indicators(df)
        df = TechnicalIndicators.add_volatility_indicators(df)
        df = TechnicalIndicators.add_volume_indicators(df)
        df = TechnicalIndicators.add_custom_indicators(df)
        return df
    
    @staticmethod
    def add_trend_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add trend-based indicators"""
        try:
            # Moving Averages
            df['sma_20'] = SMAIndicator(close=df['close'], window=20).sma_indicator()
            df['sma_50'] = SMAIndicator(close=df['close'], window=50).sma_indicator()
            df['sma_200'] = SMAIndicator(close=df['close'], window=200).sma_indicator()
            
            df['ema_9'] = EMAIndicator(close=df['close'], window=9).ema_indicator()
            df['ema_21'] = EMAIndicator(close=df['close'], window=21).ema_indicator()
            df['ema_55'] = EMAIndicator(close=df['close'], window=55).ema_indicator()
            
            # MACD
            macd = MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_diff'] = macd.macd_diff()
            
            # ADX (Average Directional Index)
            adx = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
            df['adx'] = adx.adx()
            df['adx_pos'] = adx.adx_pos()
            df['adx_neg'] = adx.adx_neg()
            
            logger.debug("Trend indicators added successfully")
        except Exception as e:
            logger.error(f"Error adding trend indicators: {e}")
        
        return df
    
    @staticmethod
    def add_momentum_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum-based indicators"""
        try:
            # RSI
            df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
            
            # Stochastic Oscillator
            stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'], 
                                         window=14, smooth_window=3)
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            
            # Rate of Change
            df['roc'] = ROCIndicator(close=df['close'], window=12).roc()
            
            # Williams %R
            df['williams_r'] = ((df['high'].rolling(window=14).max() - df['close']) / 
                               (df['high'].rolling(window=14).max() - df['low'].rolling(window=14).min()) * -100)
            
            logger.debug("Momentum indicators added successfully")
        except Exception as e:
            logger.error(f"Error adding momentum indicators: {e}")
        
        return df
    
    @staticmethod
    def add_volatility_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility-based indicators"""
        try:
            # Bollinger Bands
            bb = BollingerBands(close=df['close'], window=20, window_dev=2)
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_width'] = bb.bollinger_wband()
            df['bb_percent'] = bb.bollinger_pband()
            
            # ATR (Average True Range)
            df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], 
                                         window=14).average_true_range()
            
            logger.debug("Volatility indicators added successfully")
        except Exception as e:
            logger.error(f"Error adding volatility indicators: {e}")
        
        return df
    
    @staticmethod
    def add_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based indicators"""
        try:
            # OBV (On-Balance Volume)
            df['obv'] = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()
            
            # VWAP (Volume Weighted Average Price)
            df['vwap'] = VolumeWeightedAveragePrice(high=df['high'], low=df['low'], 
                                                    close=df['close'], volume=df['volume']).volume_weighted_average_price()
            
            # Volume MA
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            
            logger.debug("Volume indicators added successfully")
        except Exception as e:
            logger.error(f"Error adding volume indicators: {e}")
        
        return df
    
    @staticmethod
    def add_custom_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add custom indicators and features"""
        try:
            # Price momentum
            df['price_momentum_5'] = df['close'].pct_change(5)
            df['price_momentum_10'] = df['close'].pct_change(10)
            df['price_momentum_20'] = df['close'].pct_change(20)
            
            # Volatility
            df['volatility_20'] = df['close'].pct_change().rolling(window=20).std()
            
            # Higher highs and lower lows
            df['higher_high'] = (df['high'] > df['high'].shift(1)).astype(int)
            df['lower_low'] = (df['low'] < df['low'].shift(1)).astype(int)
            
            # Support and Resistance levels
            df['support'] = df['low'].rolling(window=20).min()
            df['resistance'] = df['high'].rolling(window=20).max()
            
            # Trend strength
            df['trend_strength'] = abs(df['close'] - df['sma_20']) / df['sma_20'] * 100
            
            logger.debug("Custom indicators added successfully")
        except Exception as e:
            logger.error(f"Error adding custom indicators: {e}")
        
        return df
    
    @staticmethod
    def get_signal_summary(df: pd.DataFrame) -> Dict:
        """Get a summary of trading signals from indicators"""
        try:
            latest = df.iloc[-1]
            signals = {
                'bullish': 0,
                'bearish': 0,
                'neutral': 0
            }
            
            # RSI signals
            if latest['rsi'] < 30:
                signals['bullish'] += 1
            elif latest['rsi'] > 70:
                signals['bearish'] += 1
            else:
                signals['neutral'] += 1
            
            # MACD signals
            if latest['macd'] > latest['macd_signal']:
                signals['bullish'] += 1
            else:
                signals['bearish'] += 1
            
            # Bollinger Bands signals
            if latest['close'] < latest['bb_lower']:
                signals['bullish'] += 1
            elif latest['close'] > latest['bb_upper']:
                signals['bearish'] += 1
            else:
                signals['neutral'] += 1
            
            # Moving Average signals
            if latest['ema_9'] > latest['ema_21']:
                signals['bullish'] += 1
            else:
                signals['bearish'] += 1
            
            # Stochastic signals
            if latest['stoch_k'] < 20:
                signals['bullish'] += 1
            elif latest['stoch_k'] > 80:
                signals['bearish'] += 1
            else:
                signals['neutral'] += 1
            
            total = sum(signals.values())
            signal_score = (signals['bullish'] - signals['bearish']) / total if total > 0 else 0
            
            return {
                'signals': signals,
                'signal_score': signal_score,
                'recommendation': 'BUY' if signal_score > 0.3 else 'SELL' if signal_score < -0.3 else 'HOLD'
            }
            
        except Exception as e:
            logger.error(f"Error getting signal summary: {e}")
            return {'signals': {'bullish': 0, 'bearish': 0, 'neutral': 0}, 'signal_score': 0, 'recommendation': 'HOLD'}

