"""
Script to run the FastAPI server
"""

import uvicorn
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    uvicorn.run(
        "src.api.Agriculture_Crop_Production_Prediction_System:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )








