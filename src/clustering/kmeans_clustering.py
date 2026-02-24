"""
K-Means Clustering for Productivity Zone Identification
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class ProductivityZoneClusterer:
    """K-Means clustering for identifying productivity zones."""
    
    def __init__(self, n_clusters: int = 3, random_state: int = 42):
        """
        Initialize K-Means clusterer.
        
        Args:
            n_clusters: Number of clusters (zones)
            random_state: Random seed
        """
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = None
    
    def find_optimal_clusters(self, X: np.ndarray, max_clusters: int = 10) -> int:
        """
        Find optimal number of clusters using elbow method and silhouette score.
        
        Args:
            X: Feature array
            max_clusters: Maximum number of clusters to test
        
        Returns:
            Optimal number of clusters
        """
        inertias = []
        silhouette_scores = []
        k_range = range(2, min(max_clusters + 1, len(X)))
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X, labels))
        
        # Find optimal k (highest silhouette score)
        optimal_k = k_range[np.argmax(silhouette_scores)]
        
        print(f"Optimal number of clusters: {optimal_k}")
        print(f"Silhouette score: {silhouette_scores[np.argmax(silhouette_scores)]:.3f}")
        
        return optimal_k
    
    def train(self, df: pd.DataFrame, feature_cols: Optional[List[str]] = None,
              find_optimal: bool = False) -> Dict:
        """
        Train K-Means model.
        
        Args:
            df: DataFrame with state-level aggregated data
            feature_cols: List of feature column names
            find_optimal: Whether to find optimal number of clusters
        
        Returns:
            Dictionary with training metrics
        """
        if feature_cols is None:
            # Default features: average yield, cost, production
            feature_cols = ['Avg_Quantity', 'Avg_Cost', 'Avg_Production']
        
        # Select features
        available_cols = [col for col in feature_cols if col in df.columns]
        if not available_cols:
            raise ValueError("No valid feature columns found")
        
        self.feature_names = available_cols
        X = df[available_cols].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Find optimal clusters if requested
        if find_optimal:
            optimal_k = self.find_optimal_clusters(X_scaled)
            self.n_clusters = optimal_k
            self.model = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        
        # Train model
        labels = self.model.fit_predict(X_scaled)
        df['Zone'] = labels
        
        self.is_trained = True
        
        # Calculate metrics
        silhouette_avg = silhouette_score(X_scaled, labels)
        inertia = self.model.inertia_
        
        metrics = {
            'n_clusters': self.n_clusters,
            'silhouette_score': silhouette_avg,
            'inertia': inertia
        }
        
        print(f"K-Means Clustering Results:")
        print(f"  Number of clusters: {self.n_clusters}")
        print(f"  Silhouette score: {silhouette_avg:.3f}")
        print(f"  Inertia: {inertia:.2f}")
        
        return metrics
    
    def predict_zone(self, state_data: Dict) -> int:
        """
        Predict zone for a state.
        
        Args:
            state_data: Dictionary with feature values
        
        Returns:
            Zone label (0, 1, 2, ...)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Prepare input
        features = np.array([[state_data.get(col, 0) for col in self.feature_names]])
        features_scaled = self.scaler.transform(features)
        
        zone = self.model.predict(features_scaled)[0]
        return int(zone)
    
    def get_zone_characteristics(self, df: pd.DataFrame) -> List[Dict]:
        """
        Get characteristics of each zone.
        
        Args:
            df: DataFrame with zone labels
        
        Returns:
            List of zone characteristics
        """
        if 'Zone' not in df.columns:
            raise ValueError("DataFrame must have 'Zone' column")
        
        zones = []
        for zone_id in sorted(df['Zone'].unique()):
            zone_data = df[df['Zone'] == zone_id]
            
            zone_info = {
                'zone_id': int(zone_id),
                'zone_name': self._get_zone_name(zone_id, zone_data),
                'states': zone_data['State'].tolist() if 'State' in zone_data.columns else [],
                'n_states': len(zone_data),
                'average_yield': float(zone_data['Avg_Quantity'].mean()) if 'Avg_Quantity' in zone_data.columns else 0,
                'average_cost': float(zone_data['Avg_Cost'].mean()) if 'Avg_Cost' in zone_data.columns else 0,
                'average_production': float(zone_data['Avg_Production'].mean()) if 'Avg_Production' in zone_data.columns else 0,
                'recommended_crops': self._get_recommended_crops(zone_data),
                'characteristics': self._get_characteristics(zone_data)
            }
            
            zones.append(zone_info)
        
        return zones
    
    def _get_zone_name(self, zone_id: int, zone_data: pd.DataFrame) -> str:
        """Get descriptive zone name based on productivity."""
        if 'Avg_Quantity' in zone_data.columns:
            avg_yield = zone_data['Avg_Quantity'].mean()
            if avg_yield > 40:
                return "High Productivity Zone"
            elif avg_yield > 25:
                return "Medium Productivity Zone"
            else:
                return "Low Productivity Zone"
        return f"Zone {zone_id + 1}"
    
    def _get_recommended_crops(self, zone_data: pd.DataFrame) -> List[str]:
        """Get recommended crops for a zone."""
        if 'Crop' in zone_data.columns:
            # Get top crops by average yield in this zone
            crop_yields = zone_data.groupby('Crop')['Avg_Quantity'].mean().sort_values(ascending=False)
            return crop_yields.head(5).index.tolist()
        return []
    
    def _get_characteristics(self, zone_data: pd.DataFrame) -> Dict:
        """Get zone characteristics."""
        characteristics = {}
        
        if 'Avg_Cost' in zone_data.columns:
            avg_cost = zone_data['Avg_Cost'].mean()
            if avg_cost < 60000:
                characteristics['cost_level'] = "Low"
            elif avg_cost < 80000:
                characteristics['cost_level'] = "Moderate"
            else:
                characteristics['cost_level'] = "High"
        
        # Add more characteristics based on data
        characteristics['soil_type'] = "Mixed"  # Could be enhanced with actual data
        characteristics['irrigation'] = "Moderate"  # Could be enhanced
        characteristics['climate'] = "Favorable"  # Could be enhanced
        
        return characteristics
    
    def save(self, filepath: str):
        """Save model to disk."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'n_clusters': self.n_clusters,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    @staticmethod
    def load(filepath: str):
        """Load model from disk."""
        model_data = joblib.load(filepath)
        clusterer = ProductivityZoneClusterer(n_clusters=model_data['n_clusters'])
        clusterer.model = model_data['model']
        clusterer.scaler = model_data['scaler']
        clusterer.feature_names = model_data['feature_names']
        clusterer.is_trained = model_data['is_trained']
        return clusterer


if __name__ == "__main__":
    # Example usage
    from src.utils.data_loader import load_data, get_state_crop_combinations
    
    print("Loading data...")
    df = load_data()
    
    # Aggregate by state
    print("\nAggregating data by state...")
    state_agg = df.groupby('State').agg({
        'Quantity': 'mean',
        'Cost': 'mean',
        'Production': 'mean'
    }).reset_index()
    state_agg.columns = ['State', 'Avg_Quantity', 'Avg_Cost', 'Avg_Production']
    
    print(f"States: {len(state_agg)}")
    print(state_agg.head())
    
    # Train clustering model
    print("\nTraining K-Means clustering...")
    clusterer = ProductivityZoneClusterer(n_clusters=3)
    metrics = clusterer.train(state_agg, find_optimal=True)
    
    # Get zone characteristics
    state_agg['Zone'] = clusterer.model.labels_
    zones = clusterer.get_zone_characteristics(state_agg)
    
    print("\nProductivity Zones:")
    for zone in zones:
        print(f"\n{zone['zone_name']} (Zone {zone['zone_id']}):")
        print(f"  States: {', '.join(zone['states'])}")
        print(f"  Average Yield: {zone['average_yield']:.2f}")
        print(f"  Average Cost: {zone['average_cost']:.2f}")
        print(f"  Recommended Crops: {', '.join(zone['recommended_crops'][:3])}")
    
    # Save model
    model_path = "models/saved_models/kmeans_clusterer.joblib"
    clusterer.save(model_path)
    print(f"\nModel saved to {model_path}")








