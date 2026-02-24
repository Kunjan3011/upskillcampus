"""
Model Training Script

Trains all ML models for the agriculture crop production prediction system.
"""

import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.utils.data_loader import load_data, preprocess_data
from src.utils.preprocessing import prepare_model_features
from src.models.random_forest import RandomForestYieldPredictor
from src.models.xgboost_model import XGBoostYieldPredictor
from src.clustering.kmeans_clustering import ProductivityZoneClusterer


def train_yield_models():
    """Train Random Forest and XGBoost models for yield prediction."""
    print("=" * 60)
    print("Training Yield Prediction Models")
    print("=" * 60)
    
    # Load and prepare data
    print("\n1. Loading and preprocessing data...")
    df = load_data()
    df_processed = preprocess_data(df)
    print(f"   Processed data shape: {df_processed.shape}")
    
    # Prepare features
    print("\n2. Preparing features...")
    X, y, encoder = prepare_model_features(df_processed, target_col='Quantity')
    print(f"   Features shape: {X.shape}")
    print(f"   Target shape: {y.shape}")
    
    # Train Random Forest
    print("\n3. Training Random Forest model...")
    rf_model = RandomForestYieldPredictor(n_estimators=100, max_depth=20)
    rf_metrics = rf_model.train(X, y, tune_hyperparameters=False)
    rf_model.save("models/saved_models/random_forest_model.joblib")
    
    # Train XGBoost
    print("\n4. Training XGBoost model...")
    xgb_model = XGBoostYieldPredictor(n_estimators=100, max_depth=6, learning_rate=0.1)
    xgb_metrics = xgb_model.train(X, y, tune_hyperparameters=False)
    xgb_model.save("models/saved_models/xgboost_model.joblib")
    
    print("\n[OK] Yield prediction models trained successfully!")
    return rf_model, xgb_model, encoder


def train_clustering_model():
    """Train K-Means clustering model for zone identification."""
    print("\n" + "=" * 60)
    print("Training Clustering Model")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading data...")
    df = load_data()
    
    # Aggregate by state
    print("\n2. Aggregating data by state...")
    state_agg = df.groupby('State').agg({
        'Quantity': 'mean',
        'Cost': 'mean',
        'Production': 'mean'
    }).reset_index()
    state_agg.columns = ['State', 'Avg_Quantity', 'Avg_Cost', 'Avg_Production']
    print(f"   States: {len(state_agg)}")
    
    # Train clustering
    print("\n3. Training K-Means clustering...")
    clusterer = ProductivityZoneClusterer(n_clusters=3)
    metrics = clusterer.train(state_agg, find_optimal=True)
    
    # Get zone characteristics
    state_agg['Zone'] = clusterer.model.labels_
    zones = clusterer.get_zone_characteristics(state_agg)
    
    print("\n4. Zone Summary:")
    for zone in zones:
        print(f"   {zone['zone_name']}: {len(zone['states'])} states")
    
    # Save model
    clusterer.save("models/saved_models/kmeans_clusterer.joblib")
    
    # Save zone data
    state_agg.to_csv("data/processed/state_zones.csv", index=False)
    print("\n[OK] Clustering model trained successfully!")
    
    return clusterer, zones


def main():
    """Main training function."""
    print("\n" + "=" * 60)
    print("Agriculture Crop Production - Model Training")
    print("=" * 60)
    
    try:
        # Create directories
        Path("models/saved_models").mkdir(parents=True, exist_ok=True)
        Path("data/processed").mkdir(parents=True, exist_ok=True)
        
        # Train yield models
        rf_model, xgb_model, encoder = train_yield_models()
        
        # Train clustering model
        clusterer, zones = train_clustering_model()
        
        # Save encoder
        encoder.save("models/saved_models/feature_encoder.joblib")
        
        print("\n" + "=" * 60)
        print("Training Complete!")
        print("=" * 60)
        print("\nTrained Models:")
        print("  [OK] Random Forest (yield prediction)")
        print("  [OK] XGBoost (yield prediction)")
        print("  [OK] K-Means (zone clustering)")
        print("  [OK] Feature Encoder")
        print("\nModels saved in: models/saved_models/")
        print("Zone data saved in: data/processed/state_zones.csv")
        
    except Exception as e:
        print(f"\n[ERROR] Error during training: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

