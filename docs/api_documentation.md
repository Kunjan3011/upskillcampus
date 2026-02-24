# API Documentation: Agriculture Crop Production Prediction

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Predict Crop Yield

**Endpoint**: `POST /predict/yield`

**Description**: Predicts crop yield for given parameters using hybrid ML models.

**Request Body**:
```json
{
  "crop": "Rice",
  "state": "Punjab",
  "season": "Kharif",
  "year": 2024,
  "cost": 50000.0
}
```

**Response**:
```json
{
  "predicted_yield": 45.2,
  "unit": "Quintals/Hectare",
  "confidence_interval": {
    "lower": 42.1,
    "upper": 48.3
  },
  "model_used": "Hybrid Ensemble",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `500`: Internal Server Error

---

### 2. Predict Production Trends

**Endpoint**: `POST /predict/production`

**Description**: Forecasts production trends over a time period using time-series models.

**Request Body**:
```json
{
  "crop": "Wheat",
  "state": "Uttar Pradesh",
  "start_year": 2024,
  "end_year": 2026
}
```

**Response**:
```json
{
  "forecast": [
    {
      "year": 2024,
      "predicted_production": 1250000.5,
      "unit": "Tons"
    },
    {
      "year": 2025,
      "predicted_production": 1285000.2,
      "unit": "Tons"
    },
    {
      "year": 2026,
      "predicted_production": 1310000.8,
      "unit": "Tons"
    }
  ],
  "trend": "increasing",
  "model_used": "Prophet",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad Request
- `500`: Internal Server Error

---

### 3. Calculate Profitability Index

**Endpoint**: `POST /profitability`

**Description**: Calculates profitability index for a crop based on predicted yield, market price, and cost.

**Request Body**:
```json
{
  "crop": "Cotton",
  "state": "Gujarat",
  "market_price": 6500.0,
  "cost": 75000.0
}
```

**Response**:
```json
{
  "profitability_index": 1.35,
  "predicted_yield": 15.6,
  "unit": "Quintals/Hectare",
  "expected_revenue": 101400.0,
  "cost": 75000.0,
  "expected_profit": 26400.0,
  "profit_margin": 26.2,
  "recommendation": "Profitable - Recommended",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Interpretation**:
- `profitability_index > 1`: Profitable
- `profitability_index < 1`: Loss-making
- Higher index = More profitable

**Status Codes**:
- `200`: Success
- `400`: Bad Request
- `500`: Internal Server Error

---

### 4. Get Crop Recommendations

**Endpoint**: `POST /recommendations`

**Description**: Provides zone-based crop recommendations for a given state, considering budget and season.

**Request Body**:
```json
{
  "state": "Maharashtra",
  "budget": 100000.0,
  "season": "Kharif",
  "top_n": 5
}
```

**Response**:
```json
{
  "state": "Maharashtra",
  "zone": "High Productivity Zone",
  "recommendations": [
    {
      "crop": "Soybean",
      "rank": 1,
      "profitability_index": 1.45,
      "predicted_yield": 12.5,
      "estimated_cost": 85000.0,
      "expected_revenue": 123250.0,
      "expected_profit": 38250.0,
      "reason": "High yield potential in this zone"
    },
    {
      "crop": "Cotton",
      "rank": 2,
      "profitability_index": 1.32,
      "predicted_yield": 18.2,
      "estimated_cost": 95000.0,
      "expected_revenue": 125400.0,
      "expected_profit": 30400.0,
      "reason": "Stable production and good market demand"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad Request
- `500`: Internal Server Error

---

### 5. Get Productivity Zones

**Endpoint**: `GET /zones`

**Description**: Returns all productivity zones with their characteristics and recommended crops.

**Response**:
```json
{
  "zones": [
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
        "climate": "Favorable"
      }
    },
    {
      "zone_id": 2,
      "zone_name": "Medium Productivity Zone",
      "states": ["Maharashtra", "Gujarat", "Karnataka"],
      "average_yield": 32.5,
      "average_cost": 65000.0,
      "recommended_crops": ["Cotton", "Soybean", "Groundnut"],
      "characteristics": {
        "soil_type": "Mixed",
        "irrigation": "Moderate",
        "climate": "Semi-arid"
      }
    }
  ],
  "total_zones": 3,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `200`: Success
- `500`: Internal Server Error

---

### 6. Health Check

**Endpoint**: `GET /health`

**Description**: Checks API health and model availability.

**Response**:
```json
{
  "status": "healthy",
  "models_loaded": {
    "random_forest": true,
    "xgboost": true,
    "arima": true,
    "prophet": true
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Common Error Codes**:
- `400`: Bad Request - Invalid input parameters
- `404`: Not Found - Resource not found
- `422`: Unprocessable Entity - Validation error
- `500`: Internal Server Error - Server-side error

---

## Rate Limiting

- **Free Tier**: 100 requests/hour
- **Premium Tier**: 1000 requests/hour

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642234560
```

---

## Authentication

Currently, the API is open. For production, implement authentication:

**Header**:
```
Authorization: Bearer <your_api_key>
```

---

## Example Usage

### Python
```python
import requests

# Predict yield
response = requests.post(
    "http://localhost:8000/predict/yield",
    json={
        "crop": "Rice",
        "state": "Punjab",
        "season": "Kharif",
        "year": 2024,
        "cost": 50000.0
    }
)
print(response.json())

# Get recommendations
response = requests.post(
    "http://localhost:8000/recommendations",
    json={
        "state": "Maharashtra",
        "budget": 100000.0,
        "season": "Kharif",
        "top_n": 5
    }
)
print(response.json())
```

### cURL
```bash
# Predict yield
curl -X POST "http://localhost:8000/predict/yield" \
  -H "Content-Type: application/json" \
  -d '{
    "crop": "Rice",
    "state": "Punjab",
    "season": "Kharif",
    "year": 2024,
    "cost": 50000.0
  }'

# Get profitability
curl -X POST "http://localhost:8000/profitability" \
  -H "Content-Type: application/json" \
  -d '{
    "crop": "Cotton",
    "state": "Gujarat",
    "market_price": 6500.0,
    "cost": 75000.0
  }'
```

---

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to test endpoints directly from the browser.








