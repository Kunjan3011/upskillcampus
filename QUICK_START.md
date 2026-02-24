# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for version control)

## Installation Steps

### 1. Clone or Navigate to Project Directory

```bash
cd E:\Internships\Project
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Data

1. Download the dataset from [data.gov.in](https://data.gov.in)
2. Place the dataset file(s) in `data/raw/` directory
3. Update file paths in preprocessing scripts

### 5. Run the Application

#### Option A: FastAPI Backend Only

```bash
cd src/api
python main.py
```

Or using uvicorn directly:
```bash
uvicorn src.api.main:app --reload
```

The API will be available at: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

#### Option B: Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open in your browser automatically.

#### Option C: Both (Recommended)

**Terminal 1 - Start API:**
```bash
uvicorn src.api.main:app --reload
```

**Terminal 2 - Start Dashboard:**
```bash
streamlit run dashboard/app.py
```

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

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

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

1. Open `http://localhost:8000/docs`
2. Click on any endpoint
3. Click "Try it out"
4. Enter parameters
5. Click "Execute"

## Project Structure Overview

```
Project/
├── data/
│   ├── raw/              # Original dataset files
│   └── processed/        # Cleaned data
├── notebooks/            # Jupyter notebooks for analysis
├── src/
│   ├── models/           # ML model implementations
│   ├── clustering/       # Clustering algorithms
│   ├── utils/            # Utility functions
│   └── api/              # FastAPI application
├── dashboard/             # Streamlit dashboard
├── models/                # Saved model artifacts
└── docs/                  # Documentation
```

## Next Steps

1. **Data Exploration**: Use Jupyter notebooks in `notebooks/` to explore the dataset
2. **Model Training**: Implement and train ML models (see `docs/methodology.md`)
3. **API Integration**: Connect dashboard to actual API endpoints
4. **Model Deployment**: Save trained models and load them in the API

## Common Issues

### Issue: Port already in use

**Solution**: Change the port
```bash
uvicorn src.api.main:app --reload --port 8001
```

### Issue: Module not found

**Solution**: Ensure virtual environment is activated and dependencies are installed
```bash
pip install -r requirements.txt
```

### Issue: Dataset not found

**Solution**: 
1. Download dataset from data.gov.in
2. Place in `data/raw/` directory
3. Update file paths in code

## Getting Help

- Check `docs/methodology.md` for detailed methodology
- Check `docs/api_documentation.md` for API details
- Check `PROJECT_EXPLANATION.md` for comprehensive project explanation

## Development Workflow

1. **Data Preprocessing**: Clean and prepare data
2. **Model Development**: Train models in notebooks
3. **Model Integration**: Integrate models into API
4. **Testing**: Test API endpoints
5. **Dashboard**: Connect dashboard to API
6. **Deployment**: Deploy to production (optional)

---

Happy coding! 🌾








