"""
Machine Learning models for EV charging analytics.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import logging
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime
import os

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseMLModel:
    """Base class for ML models."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.feature_names = []
        self.is_trained = False
        self.performance_metrics = {}
        
    def save_model(self, version: str = None) -> str:
        """Save model to disk."""
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        model_dir = os.path.join(settings.MODEL_PATH, self.model_name)
        os.makedirs(model_dir, exist_ok=True)
        
        model_file = os.path.join(model_dir, f"{self.model_name}_v{version}.joblib")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'performance_metrics': self.performance_metrics,
            'version': version,
            'trained_at': datetime.now()
        }
        
        joblib.dump(model_data, model_file)
        logger.info(f"Model {self.model_name} v{version} saved to {model_file}")
        return model_file
    
    def load_model(self, model_file: str) -> bool:
        """Load model from disk."""
        try:
            model_data = joblib.load(model_file)
            self.model = model_data['model']
            self.scaler = model_data.get('scaler')
            self.label_encoders = model_data.get('label_encoders', {})
            self.feature_names = model_data.get('feature_names', [])
            self.performance_metrics = model_data.get('performance_metrics', {})
            self.is_trained = True
            logger.info(f"Model loaded from {model_file}")
            return True
        except Exception as e:
            logger.error(f"Error loading model from {model_file}: {e}")
            return False
    
    def preprocess_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess features for training/prediction."""
        df = df.copy()
        
        # Handle categorical variables
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
            else:
                # Handle unseen categories
                df[col] = df[col].astype(str)
                known_categories = set(self.label_encoders[col].classes_)
                df[col] = df[col].apply(lambda x: x if x in known_categories else 'unknown')
                
                # Add 'unknown' to encoder if not present
                if 'unknown' not in known_categories:
                    self.label_encoders[col].classes_ = np.append(self.label_encoders[col].classes_, 'unknown')
                
                df[col] = self.label_encoders[col].transform(df[col])
        
        # Handle missing values
        df = df.fillna(df.median(numeric_only=True))
        
        return df


class DurationPredictionModel(BaseMLModel):
    """Model for predicting charging duration."""
    
    def __init__(self):
        super().__init__("duration_prediction")
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for duration prediction."""
        features = df.copy()
        
        # Calculate energy needed
        features['energy_needed_kwh'] = (
            features['battery_capacity_kwh'] * 
            (features['state_of_charge_end_percent'] - features['state_of_charge_start_percent']) / 100
        )
        
        # Add time-based features
        if 'charging_start_time' in features.columns:
            features['charging_start_time'] = pd.to_datetime(features['charging_start_time'])
            features['hour'] = features['charging_start_time'].dt.hour
            features['day_of_week_num'] = features['charging_start_time'].dt.dayofweek
        
        # Select relevant features
        feature_columns = [
            'vehicle_model', 'battery_capacity_kwh', 'state_of_charge_start_percent',
            'state_of_charge_end_percent', 'energy_needed_kwh', 'charger_type',
            'temperature_celsius', 'vehicle_age_years', 'time_of_day'
        ]
        
        # Add time features if available
        if 'hour' in features.columns:
            feature_columns.extend(['hour', 'day_of_week_num'])
        
        return features[feature_columns]
    
    def train(self, df: pd.DataFrame) -> Dict[str, float]:
        """Train the duration prediction model."""
        logger.info("Training duration prediction model...")
        
        # Prepare features and target
        X = self.prepare_features(df)
        y = df['charging_duration_hours']
        
        # Preprocess features
        X = self.preprocess_features(X)
        self.feature_names = X.columns.tolist()
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        metrics = {
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test)
        }
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_scaled, y, cv=5, scoring='r2')
        metrics['cv_r2_mean'] = cv_scores.mean()
        metrics['cv_r2_std'] = cv_scores.std()
        
        self.performance_metrics = metrics
        self.is_trained = True
        
        logger.info(f"Duration model training completed. Test R²: {metrics['test_r2']:.3f}")
        return metrics
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict charging duration."""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        # Convert to DataFrame
        df = pd.DataFrame([features])
        
        # Prepare features
        X = self.prepare_features(df)
        X = self.preprocess_features(X)
        
        # Ensure feature order matches training
        X = X.reindex(columns=self.feature_names, fill_value=0)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make prediction
        prediction = self.model.predict(X_scaled)[0]
        
        # Calculate feature importance for this prediction
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        return {
            'predicted_duration_hours': max(0, prediction),  # Ensure non-negative
            'confidence_score': min(1.0, self.performance_metrics.get('test_r2', 0.5)),
            'feature_importance': feature_importance
        }


class CostOptimizationModel(BaseMLModel):
    """Model for predicting and optimizing charging costs."""
    
    def __init__(self):
        super().__init__("cost_optimization")
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for cost prediction."""
        features = df.copy()
        
        # Add time-based features
        if 'charging_start_time' in features.columns:
            features['charging_start_time'] = pd.to_datetime(features['charging_start_time'])
            features['hour'] = features['charging_start_time'].dt.hour
            features['day_of_week_num'] = features['charging_start_time'].dt.dayofweek
            features['is_weekend'] = features['day_of_week_num'].isin([5, 6]).astype(int)
        
        # Calculate cost per kWh if energy consumed is available
        if 'energy_consumed_kwh' in features.columns and 'charging_cost_usd' in features.columns:
            features['cost_per_kwh'] = features['charging_cost_usd'] / features['energy_consumed_kwh']
            features['cost_per_kwh'] = features['cost_per_kwh'].replace([np.inf, -np.inf], np.nan)
        
        # Select relevant features
        feature_columns = [
            'charging_station_location', 'charger_type', 'time_of_day',
            'day_of_week', 'user_type', 'energy_consumed_kwh',
            'charging_duration_hours', 'temperature_celsius'
        ]
        
        # Add time features if available
        if 'hour' in features.columns:
            feature_columns.extend(['hour', 'is_weekend'])
        
        return features[feature_columns]
    
    def train(self, df: pd.DataFrame) -> Dict[str, float]:
        """Train the cost optimization model."""
        logger.info("Training cost optimization model...")
        
        # Prepare features and target
        X = self.prepare_features(df)
        y = df['charging_cost_usd']
        
        # Remove outliers (costs beyond 3 standard deviations)
        z_scores = np.abs((y - y.mean()) / y.std())
        mask = z_scores < 3
        X, y = X[mask], y[mask]
        
        # Preprocess features
        X = self.preprocess_features(X)
        self.feature_names = X.columns.tolist()
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        metrics = {
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test)
        }
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_scaled, y, cv=5, scoring='r2')
        metrics['cv_r2_mean'] = cv_scores.mean()
        metrics['cv_r2_std'] = cv_scores.std()
        
        self.performance_metrics = metrics
        self.is_trained = True
        
        logger.info(f"Cost model training completed. Test R²: {metrics['test_r2']:.3f}")
        return metrics
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict charging cost."""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        # Convert to DataFrame
        df = pd.DataFrame([features])
        
        # Prepare features
        X = self.prepare_features(df)
        X = self.preprocess_features(X)
        
        # Ensure feature order matches training
        X = X.reindex(columns=self.feature_names, fill_value=0)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make prediction
        prediction = self.model.predict(X_scaled)[0]
        
        # Calculate feature importance
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        return {
            'predicted_cost_usd': max(0, prediction),
            'confidence_score': min(1.0, self.performance_metrics.get('test_r2', 0.5)),
            'feature_importance': feature_importance
        }
