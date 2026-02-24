"""
Ensemble Model combining Random Forest, XGBoost, ARIMA, and Prophet
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from pathlib import Path
import joblib

from src.models.random_forest import RandomForestYieldPredictor
from src.models.xgboost_model import XGBoostYieldPredictor
from src.models.arima_model import ARIMAForecaster, prepare_time_series
from src.models.prophet_model import ProphetForecaster, prepare_prophet_data


class EnsembleYieldPredictor:
    """Ensemble model combining multiple ML approaches."""
    
    def __init__(self, model_dir: str = "models/saved_models"):
        """
        Initialize ensemble predictor.
        
        Args:
            model_dir: Directory containing saved models
        """
        self.model_dir = Path(model_dir)
        self.rf_model = None
        self.xgb_model = None
        self.arima_model = None
        self.prophet_model = None
        self.encoder = None  # Feature encoder for categorical variables
        self.weights = {
            'random_forest': 0.5,  # Increased weight since we skip time-series for speed
            'xgboost': 0.5,
            'arima': 0.2,  # Only used for trend forecasting
            'prophet': 0.2  # Only used for trend forecasting
        }
        self.is_loaded = False
    
    def load_models(self):
        """Load all trained models."""
        try:
            # Load feature encoder
            encoder_path = self.model_dir / "feature_encoder.joblib"
            if encoder_path.exists():
                from src.utils.preprocessing import FeatureEncoder
                self.encoder = FeatureEncoder.load(str(encoder_path))
                print("[OK] Feature encoder loaded")
            else:
                print("[WARNING] Feature encoder not found")
            
            # Load Random Forest
            rf_path = self.model_dir / "random_forest_model.joblib"
            if rf_path.exists():
                self.rf_model = RandomForestYieldPredictor.load(str(rf_path))
                print("[OK] Random Forest model loaded")
            else:
                print("[WARNING] Random Forest model not found")
            
            # Load XGBoost
            xgb_path = self.model_dir / "xgboost_model.joblib"
            if xgb_path.exists():
                self.xgb_model = XGBoostYieldPredictor.load(str(xgb_path))
                print("[OK] XGBoost model loaded")
            else:
                print("[WARNING] XGBoost model not found")
            
            self.is_loaded = True
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def predict_yield(self, crop: str, state: str, season: str, 
                     year: int, cost: float, df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Predict yield using ensemble approach.
        
        Args:
            crop: Crop name
            state: State name
            season: Season
            year: Year
            cost: Cost of cultivation
            df: Optional DataFrame for time-series models
        
        Returns:
            Dictionary with predictions and confidence intervals
        """
        predictions = []
        model_names = []
        
        # Random Forest prediction
        if self.rf_model and self.rf_model.is_trained:
            try:
                # Prepare input (simplified - would need proper encoding)
                input_data = self._prepare_input(crop, state, season, year, cost)
                rf_pred = self.rf_model.predict(input_data)[0]
                predictions.append(rf_pred)
                model_names.append('random_forest')
            except Exception as e:
                print(f"RF prediction error: {e}")
        
        # XGBoost prediction
        if self.xgb_model and self.xgb_model.is_trained:
            try:
                input_data = self._prepare_input(crop, state, season, year, cost)
                xgb_pred = self.xgb_model.predict(input_data)[0]
                predictions.append(xgb_pred)
                model_names.append('xgboost')
            except Exception as e:
                print(f"XGB prediction error: {e}")
        
        # Time-series predictions (SKIPPED for single predictions - too slow)
        # Only use pre-trained RF and XGBoost models for fast responses
        # Time-series models (ARIMA/Prophet) should only be used for trend forecasting endpoints
        
        # If no predictions, use default
        if len(predictions) == 0:
            # Fallback: use simple heuristic
            base_yield = {
                'Rice': 40, 'Wheat': 35, 'Cotton': 12, 'Soybean': 10,
                'Sugarcane': 70, 'Maize': 25, 'Groundnut': 15,
                'Pulses': 8, 'Oilseeds': 12, 'Jute': 20
            }.get(crop, 20)
            predictions = [base_yield]
            model_names = ['heuristic']
        
        # Weighted average
        weights = [self.weights.get(name, 1.0/len(predictions)) for name in model_names]
        weights = np.array(weights) / sum(weights)  # Normalize
        
        ensemble_pred = np.average(predictions, weights=weights)
        std_pred = np.std(predictions) if len(predictions) > 1 else ensemble_pred * 0.1
        
        return {
            'predicted_yield': max(0, float(ensemble_pred)),
            'confidence_interval': {
                'lower': max(0, float(ensemble_pred - 1.96 * std_pred)),
                'upper': float(ensemble_pred + 1.96 * std_pred)
            },
            'model_used': f"Ensemble ({', '.join(model_names)})",
            'individual_predictions': dict(zip(model_names, predictions))
        }
    
    def _prepare_input(self, crop: str, state: str, season: str, 
                      year: int, cost: float) -> pd.DataFrame:
        """Prepare input DataFrame for tree-based models."""
        # Get expected feature names from model
        if self.rf_model and hasattr(self.rf_model, 'feature_names'):
            expected_features = self.rf_model.feature_names
        else:
            # Default feature list
            expected_features = ['Crop', 'Variety', 'State', 'Season', 'Year', 'Cost', 
                               'Year_Squared', 'Cost_per_Unit', 'Production_per_Cost']
        
        # Create DataFrame with all expected features
        # Use default values for missing features
        input_data = pd.DataFrame({
            'Crop': [crop],
            'State': [state],
            'Season': [season],
            'Year': [year],
            'Cost': [cost],
            'Year_Squared': [year ** 2],
            'Cost_per_Unit': [cost / 1000.0],
            'Production_per_Cost': [0.1]
        })
        
        # Add missing features with default values
        for feat in expected_features:
            if feat not in input_data.columns:
                if feat == 'Variety':
                    input_data[feat] = 'Standard'  # Default variety
                else:
                    input_data[feat] = 0
        
        # Encode categorical features if encoder is available
        if self.encoder and self.encoder.is_fitted:
            # Only encode the categorical columns that were encoded during training
            categorical_cols = ['Crop', 'State', 'Season', 'Variety']
            categorical_cols = [col for col in categorical_cols if col in input_data.columns]
            
            # Create a copy for encoding
            input_encoded = input_data.copy()
            
            # Transform only categorical columns
            for col in categorical_cols:
                if col in self.encoder.label_encoders:
                    try:
                        # Handle unseen labels by using a default value
                        le = self.encoder.label_encoders[col]
                        if crop in le.classes_ if col == 'Crop' else (state in le.classes_ if col == 'State' else (season in le.classes_ if col == 'Season' else True)):
                            input_encoded[col] = le.transform([input_data[col].iloc[0]])[0]
                        else:
                            # Use most common class (index 0) for unseen labels
                            input_encoded[col] = 0
                    except:
                        input_encoded[col] = 0
                else:
                    # If column wasn't encoded during training, keep as is or use hash
                    input_encoded[col] = hash(str(input_data[col].iloc[0])) % 1000
            
            input_data = input_encoded
        
        # Select only expected features in correct order
        available_features = [f for f in expected_features if f in input_data.columns]
        input_data = input_data[available_features]
        
        return input_data
    
    def predict_production_trends(self, crop: str, state: str, 
                                 start_year: int, end_year: int,
                                 df: pd.DataFrame) -> Dict:
        """
        Predict production trends using time-series models.
        
        Args:
            crop: Crop name
            state: State name
            start_year: Start year
            end_year: End year
            df: Historical data
        
        Returns:
            Dictionary with forecasts
        """
        try:
            series = prepare_time_series(df, crop, state)
            
            # Try Prophet first (usually better)
            try:
                prophet_df = prepare_prophet_data(series)
                prophet = ProphetForecaster()
                prophet.train(prophet_df)
                predictions = prophet.predict(series, start_year, end_year)
                if predictions:
                    return {
                        'forecast': predictions,
                        'trend': 'increasing' if predictions[-1]['predicted_production'] > predictions[0]['predicted_production'] else 'decreasing',
                        'model_used': 'Prophet'
                    }
            except:
                pass
            
            # Fallback to ARIMA
            try:
                arima = ARIMAForecaster()
                arima.train(series)
                predictions = arima.predict(series, start_year, end_year)
                if predictions:
                    return {
                        'forecast': predictions,
                        'trend': 'increasing' if predictions[-1]['predicted_production'] > predictions[0]['predicted_production'] else 'decreasing',
                        'model_used': 'ARIMA'
                    }
            except:
                pass
            
        except Exception as e:
            print(f"Time-series prediction error: {e}")
        
        # Fallback: linear extrapolation
        avg_production = df[(df['Crop'] == crop) & (df['State'] == state)]['Production'].mean()
        if pd.isna(avg_production):
            avg_production = df['Production'].mean()
        
        forecast = []
        for year in range(start_year, end_year + 1):
            forecast.append({
                'year': year,
                'predicted_production': float(avg_production),
                'unit': 'Tons'
            })
        
        return {
            'forecast': forecast,
            'trend': 'stable',
            'model_used': 'Linear Extrapolation'
        }


if __name__ == "__main__":
    # Example usage
    from src.utils.data_loader import load_data
    
    print("Loading data...")
    df = load_data()
    
    print("\nInitializing ensemble predictor...")
    ensemble = EnsembleYieldPredictor()
    ensemble.load_models()
    
    print("\nPredicting yield...")
    result = ensemble.predict_yield(
        crop="Rice",
        state="Punjab",
        season="Kharif",
        year=2024,
        cost=80000.0,
        df=df
    )
    print(f"Predicted yield: {result['predicted_yield']:.2f}")
    print(f"Confidence interval: {result['confidence_interval']}")

