"""
FastAPI Main Application

This is the main FastAPI application for the Agriculture Crop Production
Prediction System.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import pandas as pd

# Import actual implementations
from src.utils.profitability_calculator import calculate_profitability_index
from src.models.ensemble_model import EnsembleYieldPredictor
from src.clustering.kmeans_clustering import ProductivityZoneClusterer
from src.utils.data_loader import load_data

app = FastAPI(
    title="Agriculture Crop Production Prediction System",
    description="API for predicting crop yields, production trends, and profitability",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for models and data
ensemble_predictor = None
clusterer = None
df_data = None
_models_loading = False


def load_models_background():
    """Load models in background (synchronous)."""
    global ensemble_predictor, clusterer, df_data, _models_loading
    if _models_loading:
        return  # Already loading

    _models_loading = True
    try:
        print("Loading models and data...")

        # Load ensemble predictor
        ensemble_predictor = EnsembleYieldPredictor()
        ensemble_predictor.load_models()

        # Load clustering model
        clusterer_path = Path("models/saved_models/kmeans_clusterer.joblib")
        if clusterer_path.exists():
            clusterer = ProductivityZoneClusterer.load(str(clusterer_path))
            print("[OK] Clustering model loaded")
        else:
            clusterer = None
            print("[WARNING] Clustering model not found")

        # Load data (use direct path for speed)
        df_data = load_data("data/raw/crop_production_data.csv")
        print(f"[OK] Data loaded: {len(df_data)} rows")

        print("[OK] All models and data loaded successfully!")
    except Exception as e:
        print(f"[WARNING] Warning during startup: {e}")
        print("  API will use fallback predictions")
    finally:
        _models_loading = False


@app.on_event("startup")
async def startup_event():
    """Start API immediately, load models in background."""
    # Don't block - start loading models in background
    import threading

    thread = threading.Thread(target=load_models_background, daemon=True)
    thread.start()


# Pydantic Models for Request/Response
class YieldPredictionRequest(BaseModel):
    crop: str
    state: str
    season: str
    year: int
    cost: float


class YieldPredictionResponse(BaseModel):
    predicted_yield: float
    unit: str
    confidence_interval: dict
    model_used: str
    timestamp: str


class ProductionForecastRequest(BaseModel):
    crop: str
    state: str
    start_year: int
    end_year: int


class ProfitabilityRequest(BaseModel):
    crop: str
    state: str
    market_price: float
    cost: float


class RecommendationsRequest(BaseModel):
    state: str
    budget: float
    season: str
    top_n: Optional[int] = 5


# Root Endpoint
@app.get("/")
async def root():
    """Root endpoint - instant response."""
    return {
        "message": "Agriculture Crop Production Prediction System",
        "status": "running",
        "models_loading": _models_loading,
        "models_ready": ensemble_predictor is not None and ensemble_predictor.is_loaded,
        "docs": "/docs",
        "health": "/health",
    }


# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Check API health and model availability."""
    models_loaded = {
        "random_forest": ensemble_predictor.rf_model is not None
        if ensemble_predictor
        else False,
        "xgboost": ensemble_predictor.xgb_model is not None
        if ensemble_predictor
        else False,
        "arima": True,  # Available as fallback
        "prophet": True,  # Available as fallback
        "clustering": clusterer is not None,
    }

    return {
        "status": "healthy",
        "models_loaded": models_loaded,
        "data_loaded": df_data is not None,
        "timestamp": datetime.utcnow().isoformat(),
    }


# Predict Yield Endpoint
@app.post("/predict/yield", response_model=YieldPredictionResponse)
async def predict_yield(request: YieldPredictionRequest):
    """
    Predict crop yield for given parameters.

    This endpoint uses hybrid ML models (Random Forest, XGBoost, ARIMA, Prophet)
    to predict crop yield.
    """
    try:
        if ensemble_predictor is None:
            ensemble_predictor_local = EnsembleYieldPredictor()
            ensemble_predictor_local.load_models()
            predictor = ensemble_predictor_local
        else:
            predictor = ensemble_predictor

        # Get prediction
        result = predictor.predict_yield(
            crop=request.crop,
            state=request.state,
            season=request.season,
            year=request.year,
            cost=request.cost,
            df=df_data,
        )

        return YieldPredictionResponse(
            predicted_yield=result["predicted_yield"],
            unit="Quintals/Hectare",
            confidence_interval=result["confidence_interval"],
            model_used=result["model_used"],
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


# Predict Production Trends Endpoint
@app.post("/predict/production")
async def predict_production(request: ProductionForecastRequest):
    """
    Forecast production trends over a time period.
    """
    try:
        if ensemble_predictor is None:
            ensemble_predictor_local = EnsembleYieldPredictor()
            ensemble_predictor_local.load_models()
            predictor = ensemble_predictor_local
        else:
            predictor = ensemble_predictor

        if df_data is None:
            df_data_local = load_data()
        else:
            df_data_local = df_data

        # Get forecast
        result = predictor.predict_production_trends(
            crop=request.crop,
            state=request.state,
            start_year=request.start_year,
            end_year=request.end_year,
            df=df_data_local,
        )

        return {
            "forecast": result["forecast"],
            "trend": result["trend"],
            "model_used": result["model_used"],
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")


# Calculate Profitability Endpoint
@app.post("/profitability")
async def calculate_profitability(request: ProfitabilityRequest):
    """
    Calculate profitability index for a crop.
    """
    try:
        # Get predicted yield
        if ensemble_predictor is None:
            ensemble_predictor_local = EnsembleYieldPredictor()
            ensemble_predictor_local.load_models()
            predictor = ensemble_predictor_local
        else:
            predictor = ensemble_predictor

        # Predict yield (using average season and current year)
        yield_result = predictor.predict_yield(
            crop=request.crop,
            state=request.state,
            season="Kharif",  # Default season
            year=2024,  # Current year
            cost=request.cost,
            df=df_data,
        )

        predicted_yield = yield_result["predicted_yield"]

        # Calculate profitability
        profitability = calculate_profitability_index(
            predicted_yield=predicted_yield,
            market_price=request.market_price,
            cost=request.cost,
        )

        profitability["timestamp"] = datetime.utcnow().isoformat()

        return profitability
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Profitability calculation error: {str(e)}"
        )


# Get Recommendations Endpoint
@app.post("/recommendations")
async def get_recommendations(request: RecommendationsRequest):
    """
    Get zone-based crop recommendations.
    """
    try:
        if df_data is None:
            df_data_local = load_data()
        else:
            df_data_local = df_data

        # Get unique crops
        crops = df_data_local["Crop"].unique().tolist()

        # Get zone for state
        zone_name = "Unknown Zone"
        if clusterer is not None:
            try:
                state_data = df_data_local[df_data_local["State"] == request.state]
                if len(state_data) > 0:
                    state_agg = state_data.groupby("State").agg(
                        {
                            "Quantity": "mean",
                            "Cost": "mean",
                            "Production": "mean",
                        }
                    ).reset_index()
                    state_agg.columns = [
                        "State",
                        "Avg_Quantity",
                        "Avg_Cost",
                        "Avg_Production",
                    ]

                    if len(state_agg) > 0:
                        zone_id = clusterer.predict_zone(state_agg.iloc[0].to_dict())
                        zone_name = f"Zone {zone_id + 1}"
            except Exception:
                pass

        # Get recommendations for each crop
        recommendations = []
        market_prices = {
            "Rice": 2000,
            "Wheat": 1800,
            "Cotton": 6500,
            "Soybean": 4000,
            "Sugarcane": 3000,
            "Maize": 1500,
            "Groundnut": 5000,
            "Pulses": 6000,
            "Oilseeds": 4500,
            "Jute": 3500,
        }

        if ensemble_predictor is None:
            ensemble_predictor_local = EnsembleYieldPredictor()
            ensemble_predictor_local.load_models()
            predictor = ensemble_predictor_local
        else:
            predictor = ensemble_predictor

        for crop in crops[:10]:  # Limit to top 10 crops for performance
            try:
                # Estimate cost (use average or budget-based)
                estimated_cost = min(
                    request.budget,
                    df_data_local[
                        (df_data_local["Crop"] == crop)
                        & (df_data_local["State"] == request.state)
                    ]["Cost"].mean()
                    if len(
                        df_data_local[
                            (df_data_local["Crop"] == crop)
                            & (df_data_local["State"] == request.state)
                        ]
                    )
                    > 0
                    else request.budget * 0.8,
                )

                # Predict yield
                yield_result = predictor.predict_yield(
                    crop=crop,
                    state=request.state,
                    season=request.season,
                    year=2024,
                    cost=estimated_cost,
                    df=df_data_local,
                )

                predicted_yield = yield_result["predicted_yield"]
                market_price = market_prices.get(crop, 2000)

                # Calculate profitability
                profitability = calculate_profitability_index(
                    predicted_yield=predicted_yield,
                    market_price=market_price,
                    cost=estimated_cost,
                )

                recommendations.append(
                    {
                        "crop": crop,
                        "rank": 0,  # Will be set after sorting
                        "profitability_index": profitability["profitability_index"],
                        "predicted_yield": predicted_yield,
                        "estimated_cost": estimated_cost,
                        "expected_revenue": profitability["expected_revenue"],
                        "expected_profit": profitability["expected_profit"],
                        "reason": profitability["recommendation"],
                    }
                )
            except Exception:
                continue

        # Sort by profitability and rank
        recommendations.sort(key=lambda x: x["profitability_index"], reverse=True)
        for i, rec in enumerate(recommendations, 1):
            rec["rank"] = i

        return {
            "state": request.state,
            "zone": zone_name,
            "recommendations": recommendations[: request.top_n],
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations error: {str(e)}")


# Get Zones Endpoint
@app.get("/zones")
async def get_zones():
    """
    Get all productivity zones with characteristics.
    """
    try:
        if clusterer is None:
            # Return default zones if clusterer not loaded
            zones = [
                {
                    "zone_id": 1,
                    "zone_name": "High Productivity Zone",
                    "states": ["Punjab", "Haryana", "Uttar Pradesh"],
                    "average_yield": 45.2,
                    "average_cost": 55000.0,
                    "recommended_crops": ["Wheat", "Rice", "Sugarcane"],
                    "characteristics": {
                        "soil_type": "Alluvial",
                        "irrigation": "Well-irrigated",
                        "climate": "Favorable",
                    },
                }
            ]
        else:
            # Load zone data from processed file
            zone_file = Path("data/processed/state_zones.csv")
            if zone_file.exists():
                state_zones_df = pd.read_csv(zone_file)
                zones = clusterer.get_zone_characteristics(state_zones_df)
            else:
                # Generate zones from current data
                if df_data is not None:
                    state_agg = df_data.groupby("State").agg(
                        {
                            "Quantity": "mean",
                            "Cost": "mean",
                            "Production": "mean",
                        }
                    ).reset_index()
                    state_agg.columns = [
                        "State",
                        "Avg_Quantity",
                        "Avg_Cost",
                        "Avg_Production",
                    ]
                    state_agg["Zone"] = [
                        clusterer.predict_zone(row.to_dict())
                        for _, row in state_agg.iterrows()
                    ]
                    zones = clusterer.get_zone_characteristics(state_agg)
                else:
                    zones = []

        return {
            "zones": zones,
            "total_zones": len(zones),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Zones retrieval error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

