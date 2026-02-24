"""
Random Forest Model for Crop Yield Prediction
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
from pathlib import Path
from typing import Tuple, Optional, Dict
import warnings
warnings.filterwarnings('ignore')


class RandomForestYieldPredictor:
    """Random Forest model for crop yield prediction."""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 20, 
                 min_samples_split: int = 5, random_state: int = 42):
        """
        Initialize Random Forest model.
        
        Args:
            n_estimators: Number of trees
            max_depth: Maximum depth of trees
            min_samples_split: Minimum samples to split
            random_state: Random seed
        """
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=random_state,
            n_jobs=-1
        )
        self.feature_names = None
        self.is_trained = False
    
    def train(self, X: pd.DataFrame, y: pd.Series, 
              test_size: float = 0.2, tune_hyperparameters: bool = False) -> Dict:
        """
        Train the Random Forest model.
        
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
                'max_depth': [10, 20, 30],
                'min_samples_split': [2, 5, 10]
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
        
        print(f"Random Forest Training Results:")
        print(f"  Train RMSE: {train_rmse:.2f}, Test RMSE: {test_rmse:.2f}")
        print(f"  Train MAE: {train_mae:.2f}, Test MAE: {test_mae:.2f}")
        print(f"  Train R²: {train_r2:.3f}, Test R²: {test_r2:.3f}")
        
        return metrics
    
    def predict(self, X: pd.DataFrame, return_std: bool = False) -> np.ndarray:
        """
        Predict crop yield.
        
        Args:
            X: Feature DataFrame
            return_std: Whether to return standard deviation
        
        Returns:
            Predicted yields (and optionally std)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        predictions = self.model.predict(X)
        
        if return_std:
            # Estimate prediction uncertainty using tree predictions
            tree_predictions = np.array([tree.predict(X) for tree in self.model.estimators_])
            std = np.std(tree_predictions, axis=0)
            return predictions, std
        
        return predictions
    
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
        predictor = RandomForestYieldPredictor()
        predictor.model = model_data['model']
        predictor.feature_names = model_data['feature_names']
        predictor.is_trained = model_data['is_trained']
        return predictor


def predict_yield(crop: str, state: str, season: str, year: int, 
                 cost: float, model_path: Optional[str] = None) -> float:
    """
    Predict yield for given parameters.
    
    Args:
        crop: Crop name
        state: State name
        season: Season (Kharif/Rabi/Zaid)
        year: Year
        cost: Cost of cultivation
        model_path: Path to saved model
    
    Returns:
        Predicted yield
    """
    # Load model
    if model_path and Path(model_path).exists():
        model = RandomForestYieldPredictor.load(model_path)
    else:
        # Use default model (would need to be trained first)
        raise ValueError("Model not found. Please train the model first.")
    
    # Prepare input features
    input_data = pd.DataFrame({
        'Crop': [crop],
        'State': [state],
        'Season': [season],
        'Year': [year],
        'Cost': [cost],
        'Year_Squared': [year ** 2],
        'Cost_per_Unit': [cost / 1000],  # Approximate
        'Production_per_Cost': [0.1]  # Approximate
    })
    
    # Encode categorical features (would need encoder)
    # For now, return a default prediction
    # In production, this would use the actual encoder
    
    # Predict
    prediction = model.predict(input_data)[0]
    
    return max(0, prediction)  # Ensure non-negative


if __name__ == "__main__":
    # Example usage
    from src.utils.data_loader import load_data, preprocess_data, prepare_features
    from src.utils.preprocessing import prepare_model_features
    
    # Load and prepare data
    print("Loading data...")
    df = load_data()
    df_processed = preprocess_data(df)
    X, y, encoder = prepare_model_features(df_processed, target_col='Quantity')
    
    # Train model
    print("\nTraining Random Forest model...")
    model = RandomForestYieldPredictor(n_estimators=100, max_depth=20)
    metrics = model.train(X, y, tune_hyperparameters=False)
    
    # Feature importance
    print("\nTop 10 Most Important Features:")
    importance_df = model.get_feature_importance()
    print(importance_df.head(10))
    
    # Save model
    model_path = "models/saved_models/random_forest_model.joblib"
    model.save(model_path)
    print(f"\nModel saved to {model_path}")








