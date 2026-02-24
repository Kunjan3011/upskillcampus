# Setup and Running Instructions

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Train Models (First Time Only)

Before running the API or dashboard, you need to train the models:

```bash
python train_models.py
```

This will:
- Generate sample data (if no dataset is provided)
- Train Random Forest and XGBoost models
- Train K-Means clustering model
- Save all models to `models/saved_models/`

**Note**: Training may take a few minutes depending on your system.

### 3. Run the API

**Option A: Using the run script**
```bash
python run_api.py
```

**Option B: Using uvicorn directly**
```bash
uvicorn src.api.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 4. Run the Dashboard

**Option A: Using the run script**
```bash
python run_dashboard.py
```

**Option B: Using streamlit directly**
```bash
streamlit run dashboard/app.py
```

The dashboard will open automatically in your browser at http://localhost:8501

## Running Both Together

You need to run the API and dashboard in separate terminals:

**Terminal 1 - API:**
```bash
python run_api.py
```

**Terminal 2 - Dashboard:**
```bash
python run_dashboard.py
```

## Using Your Own Dataset

1. Place your CSV file in `data/raw/` directory
2. Update the file path in `src/utils/data_loader.py` if needed
3. The file should have columns: Crop, State, Season, Year, Quantity, Production, Cost, etc.
4. Retrain models: `python train_models.py`

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

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
```

### Using Python

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
```

### Using Browser

1. Go to http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Enter parameters
5. Click "Execute"

## Troubleshooting

### Issue: Models not found

**Solution**: Run `python train_models.py` first

### Issue: Port already in use

**Solution**: 
- Change port in `run_api.py`: `port=8001`
- Update `API_BASE_URL` in `dashboard/app.py` to match

### Issue: Module not found

**Solution**: 
- Ensure you're in the project root directory
- Install dependencies: `pip install -r requirements.txt`
- Check Python path

### Issue: API connection error in dashboard

**Solution**: 
- Make sure API is running: `python run_api.py`
- Check API_BASE_URL in `dashboard/app.py` matches API port

### Issue: Data file not found

**Solution**: 
- The system will generate sample data automatically
- Or place your dataset in `data/raw/` directory

## Project Structure

```
Project/
├── train_models.py          # Train all models
├── run_api.py               # Run FastAPI server
├── run_dashboard.py         # Run Streamlit dashboard
├── requirements.txt         # Python dependencies
├── data/
│   ├── raw/                # Original dataset
│   └── processed/          # Processed data
├── src/
│   ├── api/                # FastAPI application
│   ├── models/             # ML models
│   ├── clustering/         # Clustering algorithms
│   └── utils/              # Utilities
├── dashboard/               # Streamlit dashboard
└── models/
    └── saved_models/       # Trained models
```

## Next Steps

1. **Train Models**: `python train_models.py`
2. **Start API**: `python run_api.py`
3. **Start Dashboard**: `python run_dashboard.py`
4. **Explore**: Use the dashboard or API docs to test predictions

## Production Deployment

For production deployment:

1. **API**: Use a production ASGI server like Gunicorn with Uvicorn workers
2. **Dashboard**: Deploy to Streamlit Cloud or similar
3. **Models**: Ensure models are trained and saved
4. **Environment**: Set up proper environment variables
5. **Security**: Update CORS settings, add authentication

---

Happy coding! 🌾








