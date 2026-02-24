"""
Preprocessing utilities for feature engineering and encoding.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from typing import Tuple, Optional
import joblib
from pathlib import Path


class FeatureEncoder:
    """Handles encoding of categorical features."""
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def fit(self, df: pd.DataFrame, categorical_cols: list):
        """Fit encoders on training data."""
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                le.fit(df[col].astype(str))
                self.label_encoders[col] = le
        self.is_fitted = True
    
    def transform(self, df: pd.DataFrame, categorical_cols: list) -> pd.DataFrame:
        """Transform data using fitted encoders."""
        df = df.copy()
        for col in categorical_cols:
            if col in df.columns and col in self.label_encoders:
                df[col] = self.label_encoders[col].transform(df[col].astype(str))
        return df
    
    def fit_transform(self, df: pd.DataFrame, categorical_cols: list) -> pd.DataFrame:
        """Fit and transform in one step."""
        self.fit(df, categorical_cols)
        return self.transform(df, categorical_cols)
    
    def save(self, filepath: str):
        """Save encoders to disk."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, filepath)
    
    @staticmethod
    def load(filepath: str):
        """Load encoders from disk."""
        return joblib.load(filepath)


def encode_categorical_features(df: pd.DataFrame, 
                                 categorical_cols: list,
                                 encoder: Optional[FeatureEncoder] = None) -> Tuple[pd.DataFrame, FeatureEncoder]:
    """
    Encode categorical features.
    
    Args:
        df: DataFrame with categorical columns
        categorical_cols: List of categorical column names
        encoder: Optional pre-fitted encoder
    
    Returns:
        Tuple of (encoded_df, encoder)
    """
    if encoder is None:
        encoder = FeatureEncoder()
        encoded_df = encoder.fit_transform(df, categorical_cols)
    else:
        encoded_df = encoder.transform(df, categorical_cols)
    
    return encoded_df, encoder


def scale_features(df: pd.DataFrame, 
                  numeric_cols: list,
                  scaler: Optional[StandardScaler] = None) -> Tuple[pd.DataFrame, StandardScaler]:
    """
    Scale numeric features.
    
    Args:
        df: DataFrame with numeric columns
        numeric_cols: List of numeric column names
        scaler: Optional pre-fitted scaler
    
    Returns:
        Tuple of (scaled_df, scaler)
    """
    if scaler is None:
        scaler = StandardScaler()
        df_scaled = df.copy()
        df_scaled[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    else:
        df_scaled = df.copy()
        df_scaled[numeric_cols] = scaler.transform(df[numeric_cols])
    
    return df_scaled, scaler


def create_time_features(df: pd.DataFrame, date_col: str = 'Year') -> pd.DataFrame:
    """
    Create time-based features.
    
    Args:
        df: DataFrame with date column
        date_col: Name of date/year column
    
    Returns:
        DataFrame with additional time features
    """
    df = df.copy()
    
    if date_col in df.columns:
        df['Year_Squared'] = df[date_col] ** 2
        df['Year_Centered'] = df[date_col] - df[date_col].mean()
        
        # Cyclical encoding for year (if needed)
        df['Year_Sin'] = np.sin(2 * np.pi * df[date_col] / df[date_col].max())
        df['Year_Cos'] = np.cos(2 * np.pi * df[date_col] / df[date_col].max())
    
    return df


def prepare_model_features(df: pd.DataFrame, 
                          target_col: str = 'Quantity',
                          categorical_cols: Optional[list] = None,
                          encoder: Optional[FeatureEncoder] = None) -> Tuple[pd.DataFrame, pd.Series, FeatureEncoder]:
    """
    Prepare features for model training.
    
    Args:
        df: Preprocessed DataFrame
        target_col: Name of target column
        categorical_cols: List of categorical columns (auto-detected if None)
        encoder: Optional pre-fitted encoder
    
    Returns:
        Tuple of (features_df, target_series, encoder)
    """
    if categorical_cols is None:
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        categorical_cols = [col for col in categorical_cols if col != target_col]
    
    # Separate features and target
    feature_cols = [col for col in df.columns if col != target_col]
    X = df[feature_cols].copy()
    y = df[target_col].copy()
    
    # Encode categorical features
    cat_cols_in_X = [col for col in categorical_cols if col in X.columns]
    if cat_cols_in_X:
        X, encoder = encode_categorical_features(X, cat_cols_in_X, encoder)
    
    return X, y, encoder








