"""
Comprehensive Project Setup Verification Script

This script verifies all aspects of the project setup including:
- Python version
- Virtual environment
- Package installation
- Project structure
- Data files
- Model files
"""

import sys
import os
from pathlib import Path
import importlib

# Color codes for terminal output (Windows compatible)
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print("=" * 70)

def print_success(text):
    """Print success message."""
    try:
        print(f"{Colors.GREEN}[OK]{Colors.RESET} {text}")
    except (UnicodeEncodeError, AttributeError):
        print(f"[OK] {text}")

def print_error(text):
    """Print error message."""
    try:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} {text}")
    except (UnicodeEncodeError, AttributeError):
        print(f"[ERROR] {text}")

def print_warning(text):
    """Print warning message."""
    try:
        print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} {text}")
    except (UnicodeEncodeError, AttributeError):
        print(f"[WARNING] {text}")

def check_python_version():
    """Check Python version."""
    print_header("Python Version Check")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"Python version: {version_str}")
    
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version_str} meets requirements (>= 3.8)")
        return True
    else:
        print_error(f"Python {version_str} does not meet requirements (>= 3.8)")
        return False

def check_virtual_environment():
    """Check if virtual environment is active."""
    print_header("Virtual Environment Check")
    
    venv_path = sys.executable
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    print(f"Python executable: {venv_path}")
    
    if in_venv:
        print_success("Virtual environment is active")
        if 'agriculture' in venv_path or 'venv' in venv_path:
            print_success(f"Using project virtual environment")
        return True
    else:
        print_warning("Virtual environment may not be active")
        print("  Recommended: Activate virtual environment before running")
        return False

def check_packages():
    """Check if required packages are installed."""
    print_header("Package Installation Check")
    
    required_packages = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'sklearn': 'scikit-learn',
        'xgboost': 'xgboost',
        'scipy': 'scipy',
        'statsmodels': 'statsmodels',
        'prophet': 'prophet',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'pydantic': 'pydantic',
        'streamlit': 'streamlit',
        'plotly': 'plotly',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'joblib': 'joblib',
        'requests': 'requests',
        'dotenv': 'python-dotenv'
    }
    
    missing_packages = []
    installed_packages = []
    
    for import_name, package_name in required_packages.items():
        try:
            importlib.import_module(import_name)
            installed_packages.append(package_name)
            print_success(f"{package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print_error(f"{package_name} - MISSING")
    
    print(f"\nInstalled: {len(installed_packages)}/{len(required_packages)}")
    
    if missing_packages:
        print_warning(f"Missing packages: {', '.join(missing_packages)}")
        print("\nTo install missing packages, run:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    else:
        print_success("All required packages are installed!")
        return True

def check_project_structure():
    """Check if project structure is correct."""
    print_header("Project Structure Check")
    
    required_dirs = [
        'src',
        'src/api',
        'src/models',
        'src/clustering',
        'src/utils',
        'dashboard',
        'data',
        'data/raw',
        'data/processed',
        'models',
        'models/saved_models',
        'docs'
    ]
    
    required_files = [
        'requirements.txt',
        'README.md',
        'train_models.py',
        'run_api.py',
        'run_dashboard.py',
        'src/api/main.py',
        'dashboard/app.py',
        'src/utils/data_loader.py',
        'src/utils/preprocessing.py',
        'src/utils/profitability_calculator.py'
    ]
    
    all_good = True
    
    # Check directories
    print("\nChecking directories...")
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print_success(f"Directory: {dir_path}/")
        else:
            print_error(f"Directory missing: {dir_path}/")
            all_good = False
    
    # Check files
    print("\nChecking files...")
    for file_path in required_files:
        path = Path(file_path)
        if path.exists() and path.is_file():
            print_success(f"File: {file_path}")
        else:
            print_error(f"File missing: {file_path}")
            all_good = False
    
    return all_good

def check_data_files():
    """Check if data files exist."""
    print_header("Data Files Check")
    
    raw_data_dir = Path("data/raw")
    processed_data_dir = Path("data/processed")
    
    data_found = False
    
    if raw_data_dir.exists():
        csv_files = list(raw_data_dir.glob("*.csv"))
        if csv_files:
            print_success(f"Found {len(csv_files)} CSV file(s) in data/raw/")
            for csv_file in csv_files[:5]:  # Show first 5
                print(f"  - {csv_file.name}")
            if len(csv_files) > 5:
                print(f"  ... and {len(csv_files) - 5} more")
            data_found = True
        else:
            print_warning("No CSV files found in data/raw/")
            print("  The system will generate sample data automatically")
    else:
        print_error("data/raw/ directory does not exist")
    
    if processed_data_dir.exists():
        processed_files = list(processed_data_dir.glob("*.csv"))
        if processed_files:
            print_success(f"Found {len(processed_files)} processed file(s)")
        else:
            print_warning("No processed data files found")
            print("  This is normal if models haven't been trained yet")
    
    return data_found

def check_model_files():
    """Check if trained model files exist."""
    print_header("Trained Models Check")
    
    models_dir = Path("models/saved_models")
    
    if not models_dir.exists():
        print_error("models/saved_models/ directory does not exist")
        return False
    
    model_files = list(models_dir.glob("*.joblib"))
    
    if model_files:
        print_success(f"Found {len(model_files)} trained model file(s):")
        for model_file in model_files:
            size_kb = model_file.stat().st_size / 1024
            print(f"  - {model_file.name} ({size_kb:.1f} KB)")
        return True
    else:
        print_warning("No trained model files found")
        print("  Run 'python train_models.py' to train models")
        return False

def check_configuration():
    """Check configuration files."""
    print_header("Configuration Check")
    
    config_files = {
        'requirements.txt': 'Dependencies list',
        'README.md': 'Project documentation',
        'SETUP_INSTRUCTIONS.md': 'Setup instructions',
        'QUICK_START.md': 'Quick start guide'
    }
    
    all_good = True
    for file_path, description in config_files.items():
        path = Path(file_path)
        if path.exists():
            print_success(f"{file_path} - {description}")
        else:
            print_warning(f"{file_path} - {description} (optional)")
    
    return all_good

def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print(f"{Colors.BOLD}{Colors.BLUE}Agriculture Crop Production Project - Setup Verification{Colors.RESET}")
    print("=" * 70)
    
    results = {
        'Python Version': check_python_version(),
        'Virtual Environment': check_virtual_environment(),
        'Packages': check_packages(),
        'Project Structure': check_project_structure(),
        'Data Files': check_data_files(),
        'Model Files': check_model_files(),
        'Configuration': check_configuration()
    }
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        if result:
            print_success(f"{check}")
        else:
            print_error(f"{check}")
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} checks passed{Colors.RESET}")
    
    if passed == total:
        try:
            print(f"\n{Colors.GREEN}{Colors.BOLD}[SUCCESS] Project setup is complete and ready to use!{Colors.RESET}")
        except:
            print(f"\n[SUCCESS] Project setup is complete and ready to use!")
        print("\nNext steps:")
        print("  1. Train models: python train_models.py")
        print("  2. Run API: python run_api.py")
        print("  3. Run Dashboard: python run_dashboard.py")
    else:
        try:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}[WARNING] Some checks failed. Please review the issues above.{Colors.RESET}")
        except:
            print(f"\n[WARNING] Some checks failed. Please review the issues above.")
        print("\nCommon fixes:")
        print("  - Install missing packages: pip install -r requirements.txt")
        print("  - Activate virtual environment: .\\agriculture\\Scripts\\Activate.ps1")
        print("  - Train models: python train_models.py")
    
    print("\n" + "=" * 70)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())

