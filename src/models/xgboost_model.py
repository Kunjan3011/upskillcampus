"""
XGBoost Model for Crop Yield Prediction
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
from pathlib import Path
from typing import Tuple, Optional, Dict
import warnings
warnings.filterwarnings('ignore')


class XGBoostYieldPredictor:
    """XGBoost model for crop yield prediction."""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 6,
                 learning_rate: float = 0.1, random_state: int = 42):
        """
        Initialize XGBoost model.
        
        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate
            random_state: Random seed
        """
        self.model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state,
            n_jobs=-1,
            objective='reg:squarederror'
        )
        self.feature_names = None
        self.is_trained = False
    
    def train(self, X: pd.DataFrame, y: pd.Series,
              test_size: float = 0.2, tune_hyperparameters: bool = False) -> Dict:
        """
        Train the XGBoost model.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            test_size: Proportion of data for testing
            tune_hyperparameters: Whether to tune hyperparameters
        
        Returns:
            Dictionary with training metrics
        """
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        if tune_hyperparameters:
            # Hyperparameter tuning
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [4, 6, 8],
                'learning_rate': [0.01, 0.1, 0.2]
            }
            grid_search = GridSearchCV(
                self.model, param_grid, cv=5,
                scoring='neg_mean_squared_error', n_jobs=-1
            )
            grid_search.fit(X_train, y_train)
            self.model = grid_search.best_estimator_
            print(f"Best parameters: {grid_search.best_params_}")
        else:
            # Train model
            self.model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        self.is_trained = True
        
        metrics = {
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2
        }
        
        print(f"XGBoost Training Results:")
        print(f"  Train RMSE: {train_rmse:.2f}, Test RMSE: {test_rmse:.2f}")
        print(f"  Train MAE: {train_mae:.2f}, Test MAE: {test_mae:.2f}")
        print(f"  Train R²: {train_r2:.3f}, Test R²: {test_r2:.3f}")
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict crop yield.
        
        Args:
            X: Feature DataFrame
        
        Returns:
            Predicted yields
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        return self.model.predict(X)
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance scores."""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        importances = self.model.feature_importances_
        feature_importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        return feature_importance_df
    
    def save(self, filepath: str):
        """Save model to disk."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    @staticmethod
    def load(filepath: str):
        """Load model from disk."""
        model_data = joblib.load(filepath)
        predictor = XGBoostYieldPredictor()
        predictor.model = model_data['model']
        predictor.feature_names = model_data['feature_names']
        predictor.is_trained = model_data['is_trained']
        return predictor


if __name__ == "__main__":
    # Example usage
    from src.utils.data_loader import load_data, preprocess_data
    from src.utils.preprocessing import prepare_model_features
    
    # Load and prepare data
    print("Loading data...")
    df = load_data()
    df_processed = preprocess_data(df)
    X, y, encoder = prepare_model_features(df_processed, target_col='Quantity')
    
    # Train model
    print("\nTraining XGBoost model...")
    model = XGBoostYieldPredictor(n_estimators=100, max_depth=6, learning_rate=0.1)
    metrics = model.train(X, y, tune_hyperparameters=False)
    
    # Feature importance
    print("\nTop 10 Most Important Features:")
    importance_df = model.get_feature_importance()
    print(importance_df.head(10))
    
    # Save model
    model_path = "models/saved_models/xgboost_model.joblib"
    model.save(model_path)
    print(f"\nModel saved to {model_path}")








