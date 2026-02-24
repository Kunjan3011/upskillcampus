"""
DBSCAN Clustering for Productivity Zone Identification
"""

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib
from pathlib import Path
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class DBSCANClusterer:
    """DBSCAN clustering for identifying productivity zones."""
    
    def __init__(self, eps: float = 0.5, min_samples: int = 3):
        """
        Initialize DBSCAN clusterer.
        
        Args:
            eps: Maximum distance between samples in same cluster
            min_samples: Minimum samples in a cluster
        """
        self.eps = eps
        self.min_samples = min_samples
        self.model = DBSCAN(eps=eps, min_samples=min_samples)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = None
    
    def train(self, df: pd.DataFrame, feature_cols: Optional[List[str]] = None) -> Dict:
        """
        Train DBSCAN model.
        
        Args:
            df: DataFrame with state-level aggregated data
            feature_cols: List of feature column names
        
        Returns:
            Dictionary with training metrics
        """
        if feature_cols is None:
            feature_cols = ['Avg_Quantity', 'Avg_Cost', 'Avg_Production']
        
        # Select features
        available_cols = [col for col in feature_cols if col in df.columns]
        if not available_cols:
            raise ValueError("No valid feature columns found")
        
        self.feature_names = available_cols
        X = df[available_cols].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        labels = self.model.fit_predict(X_scaled)
        df['Zone'] = labels
        
        self.is_trained = True
        
        # Calculate metrics (only for non-outlier points)
        non_outliers = labels != -1
        if non_outliers.sum() > 1:
            silhouette_avg = silhouette_score(X_scaled[non_outliers], labels[non_outliers])
        else:
            silhouette_avg = -1
        
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_outliers = (labels == -1).sum()
        
        metrics = {
            'n_clusters': n_clusters,
            'n_outliers': n_outliers,
            'silhouette_score': silhouette_avg,
            'eps': self.eps,
            'min_samples': self.min_samples
        }
        
        print(f"DBSCAN Clustering Results:")
        print(f"  Number of clusters: {n_clusters}")
        print(f"  Number of outliers: {n_outliers}")
        print(f"  Silhouette score: {silhouette_avg:.3f}")
        
        return metrics
    
    def get_zone_characteristics(self, df: pd.DataFrame) -> List[Dict]:
        """Get characteristics of each zone."""
        if 'Zone' not in df.columns:
            raise ValueError("DataFrame must have 'Zone' column")
        
        zones = []
        unique_zones = sorted([z for z in df['Zone'].unique() if z != -1])
        
        for zone_id in unique_zones:
            zone_data = df[df['Zone'] == zone_id]
            
            zone_info = {
                'zone_id': int(zone_id),
                'zone_name': f"Zone {zone_id + 1}",
                'states': zone_data['State'].tolist() if 'State' in zone_data.columns else [],
                'n_states': len(zone_data),
                'average_yield': float(zone_data['Avg_Quantity'].mean()) if 'Avg_Quantity' in zone_data.columns else 0,
                'average_cost': float(zone_data['Avg_Cost'].mean()) if 'Avg_Cost' in zone_data.columns else 0,
                'average_production': float(zone_data['Avg_Production'].mean()) if 'Avg_Production' in zone_data.columns else 0,
                'recommended_crops': [],
                'characteristics': {}
            }
            
            zones.append(zone_info)
        
        return zones
    
    def save(self, filepath: str):
        """Save model to disk."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'eps': self.eps,
            'min_samples': self.min_samples,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")


if __name__ == "__main__":
    # Example usage
    from src.utils.data_loader import load_data
    
    print("Loading data...")
    df = load_data()
    
    # Aggregate by state
    state_agg = df.groupby('State').agg({
        'Quantity': 'mean',
        'Cost': 'mean',
        'Production': 'mean'
    }).reset_index()
    state_agg.columns = ['State', 'Avg_Quantity', 'Avg_Cost', 'Avg_Production']
    
    # Train DBSCAN
    print("\nTraining DBSCAN clustering...")
    clusterer = DBSCANClusterer(eps=0.5, min_samples=2)
    metrics = clusterer.train(state_agg)
    
    print(f"\nClusters found: {metrics['n_clusters']}")
    print(f"Outliers: {metrics['n_outliers']}")








