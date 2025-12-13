# Prediction of Agriculture Crop Production in India

## 📋 Project Overview

India, with over 1.3 billion people, relies heavily on agriculture as the backbone of its economy. However, farmers face significant challenges including unpredictable yields, high cultivation costs, and regional disparities. This project aims to address these challenges by leveraging data science and machine learning to predict crop production, optimize profitability, and provide actionable recommendations for farmers and policymakers.

## 🎯 Problem Statement

- **Unpredictable Yields**: Farmers struggle with uncertain crop production outcomes
- **High Costs**: Rising cultivation and production costs impact profitability
- **Regional Disparities**: Different states and regions have varying productivity levels
- **Lack of Data-Driven Insights**: Limited access to predictive analytics for crop selection

## 📊 Dataset

The dataset (2001-2014) is licensed from [data.gov.in](https://data.gov.in) and contains:

- **Crop**: Name of the crop
- **Variety**: Subsidiary crop type
- **State**: Location of cultivation
- **Quantity**: Yield in Quintals/Hectares
- **Production**: Years of production data
- **Season**: Crop cycle duration (short/medium/long)
- **Unit**: Measurement unit (Tons)
- **Cost**: Cost of cultivation and production
- **Recommended Zone**: Suggested region (State/Mandal/Village)

## 🔧 Solution Approach

### 1. Hybrid ML Approach for Prediction
- **Random Forest/XGBoost**: For capturing non-linear relationships and feature importance
- **ARIMA/Prophet**: For time-series forecasting of production trends
- **Combined Model**: Ensemble approach for robust predictions

### 2. Profitability Index Calculation
```
Profitability Index = (Predicted Yield × Market Price) ÷ Cost
```
This metric helps farmers identify the most profitable crops based on:
- Predicted yield from ML models
- Current market prices
- Total cultivation costs

### 3. Clustering for Zone-Based Recommendations
- **K-Means/DBSCAN**: Group states into productivity zones based on:
  - Historical yield patterns
  - Soil characteristics
  - Climate conditions
  - Economic factors
- **Zone-Specific Recommendations**: Suggest optimal crops for each productivity zone

### 4. FastAPI Backend
RESTful API endpoints for:
- `/predict/yield` - Crop yield prediction
- `/predict/production` - Production trend forecasting
- `/profitability` - Calculate profitability index
- `/recommendations` - Zone-based crop recommendations
- `/zones` - Get productivity zones information

### 5. Streamlit/Plotly Dashboard
Interactive visualizations including:
- **Trend Analysis**: Historical and predicted production trends
- **Profitability Heatmaps**: Visual representation of profitable crops by region
- **Zone-Based Recommendations**: Interactive maps and charts for crop suggestions
- **Comparative Analysis**: Compare crops across different states and seasons

## 🏗️ Project Structure

```
.
├── README.md
├── requirements.txt
├── data/
│   ├── raw/              # Original dataset
│   └── processed/        # Cleaned and preprocessed data
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   └── 04_clustering_analysis.ipynb
├── src/
│   ├── models/
│   │   ├── random_forest.py
│   │   ├── xgboost_model.py
│   │   ├── arima_model.py
│   │   └── prophet_model.py
│   ├── clustering/
│   │   ├── kmeans_clustering.py
│   │   └── dbscan_clustering.py
│   ├── utils/
│   │   ├── data_loader.py
│   │   ├── preprocessing.py
│   │   └── profitability_calculator.py
│   └── api/
│       ├── main.py       # FastAPI application
│       └── endpoints.py  # API endpoints
├── dashboard/
│   └── app.py            # Streamlit dashboard
├── models/
│   └── saved_models/     # Trained model artifacts
└── docs/
    ├── methodology.md
    └── api_documentation.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd Project
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

### Running the Application

1. **Start the FastAPI backend**:
```bash
cd src/api
uvicorn main:app --reload
```

2. **Launch the Streamlit dashboard**:
```bash
cd dashboard
streamlit run app.py
```

## 📈 Expected Outcomes

1. **Accurate Yield Forecasts**: ML models predicting crop yields with high accuracy for major Indian crops
2. **Profitability Insights**: Data-driven recommendations on which crops maximize farmer profits
3. **Zone-Based Recommendations**: Geographic clustering identifying optimal crops for specific regions
4. **Scalable Solution**: Production-ready backend and dashboard for real-world deployment

## 🎓 Key Features

- **Hybrid ML Models**: Combining tree-based models with time-series forecasting
- **Economic Analysis**: Profitability calculations considering market dynamics
- **Spatial Clustering**: Geographic insights for regional optimization
- **Real-Time Predictions**: Fast API responses for production use
- **Interactive Visualizations**: User-friendly dashboard for stakeholders

## 🔬 Methodology

### Data Preprocessing
- Handling missing values
- Feature engineering (seasonal indicators, state encodings)
- Normalization and scaling
- Time-series decomposition

### Model Training
- Train-test split with temporal considerations
- Hyperparameter tuning using GridSearchCV/RandomSearchCV
- Cross-validation for robust evaluation
- Model ensemble for improved accuracy

### Clustering Analysis
- Feature selection for clustering (yield, cost, production)
- Optimal cluster number determination (elbow method, silhouette score)
- Zone characterization and interpretation

## 📊 Performance Metrics

- **Regression Models**: RMSE, MAE, R² Score
- **Time-Series Models**: MAPE, AIC, BIC
- **Clustering**: Silhouette Score, Inertia, Davies-Bouldin Index

## 🤝 Contributing

This project is designed to address real-world agricultural challenges in India. Contributions, suggestions, and improvements are welcome.

## 📝 License

Dataset is licensed from data.gov.in. Please refer to the original data source for licensing information.

## 🙏 Acknowledgments

- Data source: [data.gov.in](https://data.gov.in)
- Inspiration: Solving sustainable agriculture challenges for India's massive population

## 📧 Contact

For questions, suggestions, or collaborations, please open an issue or contact the project maintainers.

---

**Note**: This project combines data science, backend engineering, and economic insights to create a practical solution for one of India's biggest challenges - sustainable agriculture for a massive population.



