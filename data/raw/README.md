# Dataset Directory

## 📁 Where to Place Your Dataset

Place your agricultural crop production dataset (CSV file) in this directory (`data/raw/`).

## 📋 Supported File Names

The system will automatically detect datasets with these names:
- `crop_production_data.csv`
- `agriculture_data.csv`
- `crop_data.csv`
- `production_data.csv`
- `dataset.csv`
- `data.csv`

**OR** any `.csv` file placed in this directory (the first CSV file found will be used).

## 📊 Expected Dataset Format

Your dataset should contain the following columns (or similar):

### Required Columns:
- **Crop**: Name of the crop (e.g., "Rice", "Wheat", "Cotton")
- **State**: State name (e.g., "Punjab", "Maharashtra")
- **Year**: Year of production (e.g., 2001, 2002, ...)
- **Quantity**: Yield in Quintals/Hectare or Tons/Hectare
- **Production**: Total production (in Tons)
- **Cost**: Cost of cultivation and production

### Optional but Recommended:
- **Season**: Crop cycle duration (Kharif, Rabi, Zaid)
- **Variety**: Subsidiary crop type
- **Unit**: Measurement unit
- **Recommended_Zone**: Suggested region

## 🔄 How It Works

1. Place your CSV file in this directory
2. Run `python train_models.py` or start the API
3. The system will automatically detect and load your dataset
4. If no dataset is found, sample data will be generated

## 📝 Example

```
data/
└── raw/
    └── crop_production_data.csv  ← Your dataset here
```

## ⚠️ Notes

- Supported formats: CSV (.csv)
- The system tries multiple encodings (UTF-8, Latin-1, etc.)
- Column names are case-insensitive
- Missing values will be handled automatically

## 🚀 Next Steps

After placing your dataset:
1. Run `python train_models.py` to train models with your data
2. Start the API: `python run_api.py`
3. Start the dashboard: `python run_dashboard.py`

---

**Your dataset will be automatically detected and used!** 🌾








