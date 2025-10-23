import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from typing import Tuple, Dict, Optional
import logging
import joblib
import os
from datetime import datetime

# Try to import TensorFlow (optional)
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow not installed. LSTM model will be disabled. Install with: pip install tensorflow")

logger = logging.getLogger(__name__)

class MLPredictor:
    """Machine Learning predictor for crypto price movements"""
    
    def __init__(self, model_type: str = 'ensemble'):
        """
        Initialize ML Predictor
        
        Args:
            model_type: 'lstm', 'random_forest', 'gradient_boost', or 'ensemble'
        """
        self.model_type = model_type
        self.scaler = StandardScaler()
        self.models = {}
        self.feature_importance = {}
        self.last_training_time = None
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for ML model"""
        try:
            # Create target variable (1 if price goes up, 0 if down)
            df['future_return'] = df['close'].shift(-1) / df['close'] - 1
            df['target'] = (df['future_return'] > 0).astype(int)
            
            # Feature list
            feature_columns = [
                'rsi', 'macd', 'macd_signal', 'macd_diff',
                'bb_upper', 'bb_middle', 'bb_lower', 'bb_width', 'bb_percent',
                'atr', 'adx', 'adx_pos', 'adx_neg',
                'stoch_k', 'stoch_d', 'williams_r',
                'obv', 'vwap', 'volume_sma',
                'sma_20', 'sma_50', 'ema_9', 'ema_21',
                'price_momentum_5', 'price_momentum_10', 'price_momentum_20',
                'volatility_20', 'trend_strength'
            ]
            
            # Additional engineered features
            df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'] + 1e-10)
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            df['distance_from_sma20'] = (df['close'] - df['sma_20']) / df['sma_20']
            
            feature_columns.extend(['price_position', 'volume_ratio', 'distance_from_sma20'])
            
            # Remove rows with NaN values
            df_clean = df.dropna()
            
            X = df_clean[feature_columns]
            y = df_clean['target']
            
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return pd.DataFrame(), pd.Series()
    
    def train_random_forest(self, X_train, y_train) -> RandomForestClassifier:
        """Train Random Forest model"""
        logger.info("Training Random Forest model...")
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Feature importance
        self.feature_importance['random_forest'] = dict(zip(
            X_train.columns,
            model.feature_importances_
        ))
        
        return model
    
    def train_gradient_boost(self, X_train, y_train) -> GradientBoostingClassifier:
        """Train Gradient Boosting model"""
        logger.info("Training Gradient Boosting model...")
        model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        # Feature importance
        self.feature_importance['gradient_boost'] = dict(zip(
            X_train.columns,
            model.feature_importances_
        ))
        
        return model
    
    def build_lstm_model(self, input_shape: Tuple):
        """Build LSTM neural network"""
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available, cannot build LSTM model")
            return None
        
        model = keras.Sequential([
            layers.LSTM(128, return_sequences=True, input_shape=input_shape),
            layers.Dropout(0.3),
            layers.LSTM(64, return_sequences=True),
            layers.Dropout(0.3),
            layers.LSTM(32),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC()]
        )
        
        return model
    
    def prepare_lstm_data(self, X, y, lookback: int = 20):
        """Prepare sequences for LSTM"""
        X_seq = []
        y_seq = []
        
        for i in range(lookback, len(X)):
            X_seq.append(X.iloc[i-lookback:i].values)
            y_seq.append(y.iloc[i])
        
        return np.array(X_seq), np.array(y_seq)
    
    def train_lstm(self, X_train, y_train, X_val, y_val, lookback: int = 20):
        """Train LSTM model"""
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available, skipping LSTM training")
            return None
        
        logger.info("Training LSTM model...")
        
        # Scale the data
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Prepare sequences
        X_train_seq, y_train_seq = self.prepare_lstm_data(
            pd.DataFrame(X_train_scaled), pd.Series(y_train.values), lookback
        )
        X_val_seq, y_val_seq = self.prepare_lstm_data(
            pd.DataFrame(X_val_scaled), pd.Series(y_val.values), lookback
        )
        
        # Build and train model
        model = self.build_lstm_model((lookback, X_train.shape[1]))
        
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        model.fit(
            X_train_seq, y_train_seq,
            validation_data=(X_val_seq, y_val_seq),
            epochs=50,
            batch_size=32,
            callbacks=[early_stopping],
            verbose=0
        )
        
        return model
    
    def train(self, df: pd.DataFrame) -> Dict:
        """Train all models"""
        logger.info(f"Training {self.model_type} model...")
        
        X, y = self.prepare_features(df)
        
        if X.empty or y.empty:
            logger.error("No data available for training")
            return {'status': 'error', 'message': 'No data available'}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        results = {'status': 'success', 'models': {}}
        
        if self.model_type in ['random_forest', 'ensemble']:
            rf_model = self.train_random_forest(X_train, y_train)
            rf_score = rf_model.score(X_test, y_test)
            self.models['random_forest'] = rf_model
            results['models']['random_forest'] = {'accuracy': rf_score}
            logger.info(f"Random Forest accuracy: {rf_score:.4f}")
        
        if self.model_type in ['gradient_boost', 'ensemble']:
            gb_model = self.train_gradient_boost(X_train, y_train)
            gb_score = gb_model.score(X_test, y_test)
            self.models['gradient_boost'] = gb_model
            results['models']['gradient_boost'] = {'accuracy': gb_score}
            logger.info(f"Gradient Boost accuracy: {gb_score:.4f}")
        
        if self.model_type in ['lstm', 'ensemble'] and TENSORFLOW_AVAILABLE:
            X_train_lstm, X_val_lstm, y_train_lstm, y_val_lstm = train_test_split(
                X_train, y_train, test_size=0.2, shuffle=False
            )
            lstm_model = self.train_lstm(X_train_lstm, y_train_lstm, X_val_lstm, y_val_lstm)
            if lstm_model is not None:
                self.models['lstm'] = lstm_model
                results['models']['lstm'] = {'status': 'trained'}
                logger.info("LSTM model trained")
        
        self.last_training_time = datetime.now()
        return results
    
    def predict(self, df: pd.DataFrame) -> Dict:
        """Make predictions using trained models"""
        try:
            X, _ = self.prepare_features(df)
            
            if X.empty:
                return {'prediction': 0.5, 'confidence': 0, 'signal': 'HOLD'}
            
            X_latest = X.iloc[-1:].fillna(0)
            predictions = []
            
            # Get predictions from all available models
            if 'random_forest' in self.models:
                rf_pred = self.models['random_forest'].predict_proba(X_latest)[0][1]
                predictions.append(rf_pred)
            
            if 'gradient_boost' in self.models:
                gb_pred = self.models['gradient_boost'].predict_proba(X_latest)[0][1]
                predictions.append(gb_pred)
            
            if 'lstm' in self.models:
                X_scaled = self.scaler.transform(X.iloc[-20:].fillna(0))
                X_seq = np.array([X_scaled])
                lstm_pred = self.models['lstm'].predict(X_seq, verbose=0)[0][0]
                predictions.append(lstm_pred)
            
            # Ensemble prediction (average)
            avg_prediction = np.mean(predictions) if predictions else 0.5
            
            # Calculate confidence (agreement between models)
            confidence = 1 - np.std(predictions) if len(predictions) > 1 else 0.5
            
            # Generate signal
            if avg_prediction > 0.6 and confidence > 0.6:
                signal = 'STRONG_BUY'
            elif avg_prediction > 0.55:
                signal = 'BUY'
            elif avg_prediction < 0.4 and confidence > 0.6:
                signal = 'STRONG_SELL'
            elif avg_prediction < 0.45:
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            return {
                'prediction': float(avg_prediction),
                'confidence': float(confidence),
                'signal': signal,
                'individual_predictions': predictions
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return {'prediction': 0.5, 'confidence': 0, 'signal': 'HOLD'}
    
    def save_models(self, directory: str = 'models'):
        """Save trained models to disk"""
        try:
            os.makedirs(directory, exist_ok=True)
            
            if 'random_forest' in self.models:
                joblib.dump(self.models['random_forest'], 
                          os.path.join(directory, 'random_forest.pkl'))
            
            if 'gradient_boost' in self.models:
                joblib.dump(self.models['gradient_boost'], 
                          os.path.join(directory, 'gradient_boost.pkl'))
            
            if 'lstm' in self.models:
                self.models['lstm'].save(os.path.join(directory, 'lstm_model.h5'))
            
            # Save scaler
            joblib.dump(self.scaler, os.path.join(directory, 'scaler.pkl'))
            
            logger.info(f"Models saved to {directory}")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self, directory: str = 'models'):
        """Load trained models from disk"""
        try:
            if os.path.exists(os.path.join(directory, 'random_forest.pkl')):
                self.models['random_forest'] = joblib.load(
                    os.path.join(directory, 'random_forest.pkl'))
            
            if os.path.exists(os.path.join(directory, 'gradient_boost.pkl')):
                self.models['gradient_boost'] = joblib.load(
                    os.path.join(directory, 'gradient_boost.pkl'))
            
            if TENSORFLOW_AVAILABLE and os.path.exists(os.path.join(directory, 'lstm_model.h5')):
                self.models['lstm'] = keras.models.load_model(
                    os.path.join(directory, 'lstm_model.h5'))
            
            if os.path.exists(os.path.join(directory, 'scaler.pkl')):
                self.scaler = joblib.load(os.path.join(directory, 'scaler.pkl'))
            
            logger.info(f"Models loaded from {directory}")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")

