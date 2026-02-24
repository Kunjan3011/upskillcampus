"""
Prophet Model for Time-Series Production Forecasting
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class ProphetForecaster:
    """Prophet model for time-series forecasting."""
    
    def __init__(self, yearly_seasonality: bool = True, 
                 weekly_seasonality: bool = False,
                 daily_seasonality: bool = False):
        """
        Initialize Prophet model.
        
        Args:
            yearly_seasonality: Enable yearly seasonality
            weekly_seasonality: Enable weekly seasonality
            daily_seasonality: Enable daily seasonality
        """
        self.model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality
        )
        self.is_trained = False
    
    def train(self, df: pd.DataFrame) -> Dict:
        """
        Train Prophet model.
        
        Args:
            df: DataFrame with columns 'ds' (date) and 'y' (value)
        
        Returns:
            Dictionary with model metrics
        """
        # Prophet requires 'ds' and 'y' columns
        if 'ds' not in df.columns or 'y' not in df.columns:
            raise ValueError("DataFrame must have 'ds' (date) and 'y' (value) columns")
        
        # Fit model
        self.model.fit(df)
        self.is_trained = True
        
        # Make in-sample predictions for metrics
        forecast = self.model.predict(df)
        
        # Calculate metrics
        actual = df['y'].values
        predicted = forecast['yhat'].values
        residuals = actual - predicted
        
        metrics = {
            'rmse': np.sqrt(np.mean(residuals ** 2)),
            'mae': np.mean(np.abs(residuals)),
            'mape': np.mean(np.abs(residuals / (actual + 1e-6))) * 100
        }
        
        print(f"Prophet Model Metrics:")
        print(f"  RMSE: {metrics['rmse']:.2f}")
        print(f"  MAE: {metrics['mae']:.2f}")
        print(f"  MAPE: {metrics['mape']:.2f}%")
        
        return metrics
    
    def forecast(self, periods: int, freq: str = 'Y') -> pd.DataFrame:
        """
        Forecast future values.
        
        Args:
            periods: Number of periods to forecast
            freq: Frequency ('Y' for yearly, 'M' for monthly, etc.)
        
        Returns:
            DataFrame with forecasts
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before forecasting")
        
        future = self.model.make_future_dataframe(periods=periods, freq=freq)
        forecast = self.model.predict(future)
        
        return forecast
    
    def predict(self, series: pd.Series, start_year: int, end_year: int) -> List[Dict]:
        """
        Predict production for a range of years.
        
        Args:
            series: Historical time series (index should be years)
            start_year: Start year for prediction
            end_year: End year for prediction
        
        Returns:
            List of predictions with years
        """
        if not self.is_trained:
            # Prepare data for training
            df = pd.DataFrame({
                'ds': pd.to_datetime([f"{int(year)}-01-01" for year in series.index]),
                'y': series.values
            })
            self.train(df)
        
        # Get last year
        last_year = int(series.index[-1])
        periods = end_year - last_year
        
        if periods <= 0:
            return []
        
        # Forecast
        forecast_df = self.forecast(periods=periods, freq='Y')
        
        # Extract future predictions
        future_forecast = forecast_df.tail(periods)
        
        predictions = []
        for idx, row in future_forecast.iterrows():
            year = row['ds'].year
            if start_year <= year <= end_year:
                predictions.append({
                    'year': year,
                    'predicted_production': float(row['yhat']),
                    'lower_bound': float(row['yhat_lower']),
                    'upper_bound': float(row['yhat_upper']),
                    'unit': 'Tons'
                })
        
        return predictions


def prepare_prophet_data(series: pd.Series) -> pd.DataFrame:
    """
    Prepare time series data for Prophet.
    
    Args:
        series: Time series with year index
    
    Returns:
        DataFrame with 'ds' and 'y' columns
    """
    df = pd.DataFrame({
        'ds': pd.to_datetime([f"{int(year)}-01-01" for year in series.index]),
        'y': series.values
    })
    
    return df


if __name__ == "__main__":
    # Example usage
    from src.utils.data_loader import load_data
    from src.models.arima_model import prepare_time_series
    
    print("Loading data...")
    df = load_data()
    
    # Prepare time series
    crop = "Rice"
    state = "Punjab"
    print(f"\nPreparing time series for {crop} in {state}...")
    
    try:
        series = prepare_time_series(df, crop, state)
        print(f"Time series length: {len(series)}")
        
        # Prepare Prophet data
        prophet_df = prepare_prophet_data(series)
        
        # Train model
        print("\nTraining Prophet model...")
        forecaster = ProphetForecaster(yearly_seasonality=True)
        metrics = forecaster.train(prophet_df)
        
        # Forecast
        print("\nForecasting next 3 years...")
        predictions = forecaster.predict(series, 2015, 2017)
        for pred in predictions:
            print(f"  {pred['year']}: {pred['predicted_production']:.2f} Tons "
                  f"({pred['lower_bound']:.2f} - {pred['upper_bound']:.2f})")
    
    except ValueError as e:
        print(f"Error: {e}")








