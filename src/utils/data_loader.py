"""
Data Loading and Preprocessing Utilities

Handles loading, cleaning, and preprocessing of agricultural data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


# Cache for data file path to avoid repeated searches
_cached_data_path = None

def load_data(file_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load agricultural dataset from CSV file.
    
    Args:
        file_path: Path to CSV file. If None, searches for dataset in data/raw/
    
    Returns:
        DataFrame with agricultural data
    """
    global _cached_data_path
    
    # If no file path provided, use cached path or search
    if file_path is None:
        if _cached_data_path and Path(_cached_data_path).exists():
            file_path = _cached_data_path
        else:
            raw_data_dir = Path("data/raw")
            if raw_data_dir.exists():
                # Look for common dataset file names (prioritized order)
                common_names = [
                    "crop_production_data.csv",  # Preprocessed dataset
                    "agriculture_data.csv",
                    "crop_data.csv",
                    "production_data.csv",
                    "dataset.csv",
                    "data.csv"
                ]
                
                # Check for preprocessed dataset first
                for name in common_names:
                    potential_file = raw_data_dir / name
                    if potential_file.exists():
                        file_path = str(potential_file)
                        _cached_data_path = file_path  # Cache it
                        break
                
                # If not found, check in subdirectories
                if file_path is None:
                    # Check in Project4 folder
                    project_folder = raw_data_dir / "Project4_Ag_Prediction of Agriculture Crop Production In India"
                    if project_folder.exists():
                        main_file = project_folder / "main_crop_data.csv"
                        if main_file.exists():
                            file_path = str(main_file)
                            _cached_data_path = file_path  # Cache it
                            print("Found main dataset in Project4 folder")
                
                # If still not found, check for any CSV file in raw directory
                if file_path is None:
                    csv_files = list(raw_data_dir.glob("*.csv"))
                    if csv_files:
                        file_path = str(csv_files[0])
                        _cached_data_path = file_path  # Cache it
                        print(f"Found dataset: {csv_files[0].name}")
    
    # Load the dataset if file path exists
    if file_path and Path(file_path).exists():
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    print(f"[OK] Loaded data from {file_path}: {len(df)} rows, {len(df.columns)} columns")
                    print(f"  Encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("Could not read file with any encoding")
            
            return df
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            print("Falling back to sample data generation...")
    
    # Generate sample data if no dataset found
    print("No dataset file found in data/raw/. Generating sample data...")
    print("To use your own dataset, place it in data/raw/ directory")
    df = generate_sample_data()
    # Save sample data for future use
    sample_path = Path("data/raw/sample_data.csv")
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(sample_path, index=False)
    print(f"Sample data saved to {sample_path}")
    
    return df


def generate_sample_data(n_samples: int = 5000) -> pd.DataFrame:
    """
    Generate sample agricultural data for testing.
    
    Args:
        n_samples: Number of samples to generate
    
    Returns:
        DataFrame with sample agricultural data
    """
    np.random.seed(42)
    
    crops = ['Rice', 'Wheat', 'Cotton', 'Soybean', 'Sugarcane', 'Maize', 
             'Groundnut', 'Pulses', 'Oilseeds', 'Jute']
    
    states = ['Punjab', 'Maharashtra', 'Uttar Pradesh', 'Gujarat', 'Karnataka',
              'Haryana', 'Tamil Nadu', 'Andhra Pradesh', 'Madhya Pradesh', 'Rajasthan']
    
    seasons = ['Kharif', 'Rabi', 'Zaid']
    
    varieties = ['High Yield', 'Standard', 'Organic', 'Hybrid']
    
    years = list(range(2001, 2015))
    
    data = []
    
    for _ in range(n_samples):
        crop = np.random.choice(crops)
        state = np.random.choice(states)
        season = np.random.choice(seasons)
        year = np.random.choice(years)
        variety = np.random.choice(varieties)
        
        # Generate realistic yield based on crop, state, and season
        base_yield = {
            'Rice': 40, 'Wheat': 35, 'Cotton': 12, 'Soybean': 10,
            'Sugarcane': 70, 'Maize': 25, 'Groundnut': 15,
            'Pulses': 8, 'Oilseeds': 12, 'Jute': 20
        }.get(crop, 20)
        
        # State multipliers (some states are more productive)
        state_multiplier = {
            'Punjab': 1.3, 'Haryana': 1.25, 'Uttar Pradesh': 1.2,
            'Maharashtra': 1.0, 'Gujarat': 1.1, 'Karnataka': 0.95,
            'Tamil Nadu': 1.05, 'Andhra Pradesh': 1.0, 
            'Madhya Pradesh': 0.9, 'Rajasthan': 0.85
        }.get(state, 1.0)
        
        # Season adjustments
        season_adjustment = {
            'Kharif': 1.0, 'Rabi': 1.1, 'Zaid': 0.8
        }.get(season, 1.0)
        
        # Add some randomness
        quantity = base_yield * state_multiplier * season_adjustment * np.random.uniform(0.85, 1.15)
        
        # Generate cost (correlated with yield)
        cost = quantity * np.random.uniform(1500, 2500)
        
        # Generate production (assuming area of 1 hectare for simplicity)
        production = quantity * np.random.uniform(0.8, 1.2)  # in tons
        
        data.append({
            'Crop': crop,
            'Variety': variety,
            'State': state,
            'Season': season,
            'Year': year,
            'Quantity': round(quantity, 2),
            'Production': round(production, 2),
            'Unit': 'Tons',
            'Cost': round(cost, 2),
            'Recommended_Zone': state
        })
    
    df = pd.DataFrame(data)
    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the agricultural dataset.
    
    Args:
        df: Raw DataFrame
    
    Returns:
        Preprocessed DataFrame
    """
    df = df.copy()
    
    # Handle missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].notna().sum() > 0:  # Only fill if there are some non-null values
            df[col].fillna(df[col].median(), inplace=True)
        else:
            # If all values are NaN, fill with 0 or drop the column
            df[col].fillna(0, inplace=True)
    
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df[col].notna().sum() > 0:
            mode_val = df[col].mode()
            df[col].fillna(mode_val[0] if len(mode_val) > 0 else 'Unknown', inplace=True)
        else:
            df[col].fillna('Unknown', inplace=True)
    
    # Remove outliers (using IQR method for numeric columns)
    # Only apply to columns with sufficient variance and non-null values
    outlier_cols = []
    for col in numeric_cols:
        # Skip columns that are all NaN, have no variance, or are identifiers
        if (df[col].notna().sum() > 0 and 
            df[col].nunique() > 1 and 
            col not in ['Year', 'Season_Duration', 'Recommended_Zone']):  # Skip ID-like columns
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            # Only apply outlier removal if IQR is valid (not NaN and not zero)
            if pd.notna(IQR) and IQR > 0:
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_cols.append((col, lower_bound, upper_bound))
    
    # Apply outlier removal to all selected columns at once (not sequentially)
    if outlier_cols:
        mask = pd.Series([True] * len(df), index=df.index)
        for col, lower_bound, upper_bound in outlier_cols:
            mask = mask & (df[col] >= lower_bound) & (df[col] <= upper_bound)
        df = df[mask]
    
    # Feature engineering
    if 'Year' in df.columns:
        df['Year_Squared'] = df['Year'] ** 2
    if 'Cost' in df.columns and 'Quantity' in df.columns:
        df['Cost_per_Unit'] = df['Cost'] / (df['Quantity'] + 1e-6)
    if 'Production' in df.columns and 'Cost' in df.columns:
        df['Production_per_Cost'] = df['Production'] / (df['Cost'] + 1e-6)
    
    # Encode categorical variables (will be done in model training)
    return df


def prepare_features(df: pd.DataFrame, target: str = 'Quantity') -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare features and target for model training.
    
    Args:
        df: Preprocessed DataFrame
        target: Target column name
    
    Returns:
        Tuple of (features_df, target_series)
    """
    # Select features
    feature_cols = ['Crop', 'State', 'Season', 'Year', 'Cost', 'Year_Squared', 
                    'Cost_per_Unit', 'Production_per_Cost']
    
    # Ensure all columns exist
    available_cols = [col for col in feature_cols if col in df.columns]
    X = df[available_cols].copy()
    y = df[target].copy()
    
    return X, y


def get_state_crop_combinations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get unique state-crop combinations for time-series analysis.
    
    Args:
        df: DataFrame with agricultural data
    
    Returns:
        DataFrame with unique state-crop combinations
    """
    combinations = df.groupby(['State', 'Crop']).agg({
        'Quantity': 'mean',
        'Production': 'mean',
        'Cost': 'mean',
        'Year': ['min', 'max']
    }).reset_index()
    
    combinations.columns = ['State', 'Crop', 'Avg_Quantity', 'Avg_Production', 
                          'Avg_Cost', 'Min_Year', 'Max_Year']
    
    return combinations


if __name__ == "__main__":
    # Test data loading
    df = load_data()
    print(f"\nDataset shape: {df.shape}")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nData types:")
    print(df.dtypes)
    print(f"\nMissing values:")
    print(df.isnull().sum())
    
    # Test preprocessing
    df_processed = preprocess_data(df)
    print(f"\nAfter preprocessing: {df_processed.shape}")
    
    # Test feature preparation
    X, y = prepare_features(df_processed)
    print(f"\nFeatures shape: {X.shape}")
    print(f"Target shape: {y.shape}")

