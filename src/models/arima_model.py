"""
ARIMA Model for Time-Series Production Forecasting
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class ARIMAForecaster:
    """ARIMA model for time-series forecasting."""
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.order = None
    
    def check_stationarity(self, series: pd.Series) -> bool:
        """
        Check if time series is stationary using ADF test.
        
        Args:
            series: Time series data
        
        Returns:
            True if stationary, False otherwise
        """
        result = adfuller(series.dropna())
        return result[1] <= 0.05  # p-value <= 0.05 means stationary
    
    def find_optimal_order(self, series: pd.Series, max_p: int = 3, 
                          max_d: int = 2, max_q: int = 3) -> Tuple[int, int, int]:
        """
        Find optimal ARIMA order using AIC.
        
        Args:
            series: Time series data
            max_p: Maximum AR order
            max_d: Maximum differencing order
            max_q: Maximum MA order
        
        Returns:
            Optimal (p, d, q) order
        """
        best_aic = np.inf
        best_order = (1, 1, 1)
        
        # Check stationarity
        is_stationary = self.check_stationarity(series)
        d_range = [0] if is_stationary else [1, 2]
        
        for p in range(max_p + 1):
            for d in d_range:
                for q in range(max_q + 1):
                    try:
                        model = ARIMA(series, order=(p, d, q))
                        fitted_model = model.fit()
                        if fitted_model.aic < best_aic:
                            best_aic = fitted_model.aic
                            best_order = (p, d, q)
                    except:
                        continue
        
        return best_order
    
    def train(self, series: pd.Series, order: Optional[Tuple[int, int, int]] = None) -> Dict:
        """
        Train ARIMA model.
        
        Args:
            series: Time series data (should be sorted by time)
            order: ARIMA order (p, d, q). If None, auto-selects
        
        Returns:
            Dictionary with model metrics
        """
        if order is None:
            print("Finding optimal ARIMA order...")
            order = self.find_optimal_order(series)
            print(f"Optimal order: {order}")
        
        self.order = order
        
        # Fit model
        self.model = ARIMA(series, order=order)
        fitted_model = self.model.fit()
        
        self.is_trained = True
        
        # Calculate metrics
        predictions = fitted_model.fittedvalues
        residuals = series - predictions
        
        metrics = {
            'aic': fitted_model.aic,
            'bic': fitted_model.bic,
            'rmse': np.sqrt(np.mean(residuals ** 2)),
            'mae': np.mean(np.abs(residuals)),
            'order': order
        }
        
        print(f"ARIMA Model Metrics:")
        print(f"  AIC: {metrics['aic']:.2f}")
        print(f"  BIC: {metrics['bic']:.2f}")
        print(f"  RMSE: {metrics['rmse']:.2f}")
        
        return metrics
    
    def forecast(self, steps: int, confidence_level: float = 0.95) -> Dict:
        """
        Forecast future values.
        
        Args:
            steps: Number of steps ahead to forecast
            confidence_level: Confidence level for intervals
        
        Returns:
            Dictionary with forecasts and confidence intervals
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before forecasting")
        
        forecast_result = self.model.fit().forecast(steps=steps, alpha=1-confidence_level)
        
        forecast = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int()
        
        return {
            'forecast': forecast.values,
            'lower_bound': conf_int.iloc[:, 0].values,
            'upper_bound': conf_int.iloc[:, 1].values
        }
    
    def predict(self, series: pd.Series, start_year: int, end_year: int) -> List[Dict]:
        """
        Predict production for a range of years.
        
        Args:
            series: Historical time series
            start_year: Start year for prediction
            end_year: End year for prediction
        
        Returns:
            List of predictions with years
        """
        if not self.is_trained:
            # Train if not already trained
            self.train(series)
        
        # Get last year in series
        if isinstance(series.index, pd.DatetimeIndex):
            last_year = series.index[-1].year
        else:
            last_year = int(series.index[-1])
        
        steps = end_year - last_year
        if steps <= 0:
            return []
        
        forecast_result = self.forecast(steps=steps)
        
        predictions = []
        for i, year in enumerate(range(last_year + 1, end_year + 1)):
            predictions.append({
                'year': year,
                'predicted_production': float(forecast_result['forecast'][i]),
                'lower_bound': float(forecast_result['lower_bound'][i]),
                'upper_bound': float(forecast_result['upper_bound'][i]),
                'unit': 'Tons'
            })
        
        return predictions


def prepare_time_series(df: pd.DataFrame, crop: str, state: str) -> pd.Series:
    """
    Prepare time series data for a specific crop-state combination.
    
    Args:
        df: DataFrame with agricultural data
        crop: Crop name
        state: State name
    
    Returns:
        Time series of production/yield
    """
    # Filter data
    filtered = df[(df['Crop'] == crop) & (df['State'] == state)].copy()
    
    if len(filtered) == 0:
        raise ValueError(f"No data found for {crop} in {state}")
    
    # Group by year and aggregate
    time_series = filtered.groupby('Year')['Production'].mean().sort_index()
    
    return time_series


if __name__ == "__main__":
    # Example usage
    from src.utils.data_loader import load_data
    
    print("Loading data...")
    df = load_data()
    
    # Prepare time series
    crop = "Rice"
    state = "Punjab"
    print(f"\nPreparing time series for {crop} in {state}...")
    
    try:
        series = prepare_time_series(df, crop, state)
        print(f"Time series length: {len(series)}")
        print(f"Years: {series.index.min()} to {series.index.max()}")
        
        # Train model
        print("\nTraining ARIMA model...")
        forecaster = ARIMAForecaster()
        metrics = forecaster.train(series)
        
        # Forecast
        print("\nForecasting next 3 years...")
        predictions = forecaster.predict(series, 2015, 2017)
        for pred in predictions:
            print(f"  {pred['year']}: {pred['predicted_production']:.2f} Tons")
    
    except ValueError as e:
        print(f"Error: {e}")








