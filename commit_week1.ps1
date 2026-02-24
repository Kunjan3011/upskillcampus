# PowerShell script to commit Week 1 deliverables only
# Based on WEEK_1_PROGRESS_REPORT_FORMATTED.md

Write-Host "=== Week 1 Git Commit Script ===" -ForegroundColor Green
Write-Host ""

# Configure git user (if not already set)
Write-Host "Checking git configuration..." -ForegroundColor Yellow
$gitUser = git config user.name
$gitEmail = git config user.email

if (-not $gitUser) {
    Write-Host "Git user not configured. Please set:" -ForegroundColor Yellow
    Write-Host "  git config user.name 'Your Name'" -ForegroundColor Cyan
    Write-Host "  git config user.email 'your.email@example.com'" -ForegroundColor Cyan
    exit 1
}

Write-Host "Git user: $gitUser" -ForegroundColor Green
Write-Host "Git email: $gitEmail" -ForegroundColor Green
Write-Host ""

# Stage Week 1 files only
Write-Host "Staging Week 1 files..." -ForegroundColor Yellow

# 1. Project Setup & Environment Configuration
git add .gitignore
git add requirements.txt
git add README.md

# 2. Project Structure (__init__.py files only - no implementation code)
git add src/__init__.py
git add src/utils/__init__.py
git add src/models/__init__.py
git add src/api/__init__.py
git add src/clustering/__init__.py

# 3. Documentation (Week 1 deliverables)
git add 6_WEEK_PROJECT_PLAN.md
git add LEARNING_PREREQUISITES.md
git add EXECUTION_GUIDE.md
git add WEEK_1_PROGRESS_REPORT_FORMATTED.md

# 4. Notebooks (Week 1 - Data Exploration)
git add notebooks/01_data_exploration.ipynb
git add notebooks/02_feature_engineering.ipynb
git add notebooks/03_model_training.ipynb
git add notebooks/04_clustering_analysis.ipynb

# 5. Data directory structure (empty directories with .gitkeep)
if (Test-Path "data/raw/.gitkeep") {
    git add data/raw/.gitkeep
}
if (Test-Path "data/processed/.gitkeep") {
    git add data/processed/.gitkeep
}

Write-Host ""
Write-Host "=== Files Staged for Week 1 Commit ===" -ForegroundColor Green
git status --short

Write-Host ""
Write-Host "=== Review the staged files above ===" -ForegroundColor Yellow
Write-Host "If everything looks correct, the commit will be created with message:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Commit Message:" -ForegroundColor Cyan
Write-Host "Week 1: Project Setup, Data Exploration, and Architecture Design" -ForegroundColor White
Write-Host ""
Write-Host "- Project setup and environment configuration" -ForegroundColor White
Write-Host "- Comprehensive data exploration and EDA notebooks" -ForegroundColor White
Write-Host "- System architecture design and documentation" -ForegroundColor White
Write-Host "- Agricultural domain knowledge documentation" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Proceed with commit? (y/n)"
if ($confirm -eq 'y' -or $confirm -eq 'Y') {
    git commit -m "Week 1: Project Setup, Data Exploration, and Architecture Design

- Project setup and environment configuration
  - Created project directory structure
  - Configured requirements.txt with all dependencies
  - Set up .gitignore for version control
  - Created initial README.md

- Data Acquisition & Exploratory Data Analysis
  - Performed comprehensive EDA using Jupyter notebooks
  - Created 4 optional notebooks for data exploration, feature engineering, model training, and clustering analysis
  - Documented data structure, quality issues, and key insights

- System Architecture Design
  - Designed complete end-to-end system architecture
  - Created 6-week project plan and execution guide
  - Documented API structure and dashboard design

- Learning Resources & Documentation
  - Created learning prerequisites guide
  - Documented agricultural domain knowledge
  - Prepared Week 1 progress report"
    
    Write-Host ""
    Write-Host "=== Commit Created Successfully! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Create a GitHub repository (if not already created)" -ForegroundColor Cyan
    Write-Host "2. Add remote: git remote add origin <your-repo-url>" -ForegroundColor Cyan
    Write-Host "3. Push: git push -u origin main" -ForegroundColor Cyan
} else {
    Write-Host "Commit cancelled. Files are still staged." -ForegroundColor Yellow
    Write-Host "To unstage: git reset" -ForegroundColor Cyan
}

