# Week 2 Commit and Push to GitHub
# Author: Kunjan3011 <kunjanchittroda3011@gmail.com>
# Run this AFTER closing any other Git operations (Cursor, Git GUI, other terminals).

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== Week 2 commit for CropPredictionAI-IN- ===" -ForegroundColor Cyan

# 1. Remove lock files if they exist (unlock git)
if (Test-Path ".git\index.lock") {
    Remove-Item ".git\index.lock" -Force
    Write-Host "Removed .git\index.lock" -ForegroundColor Yellow
}
if (Test-Path ".git\config.lock") {
    Remove-Item ".git\config.lock" -Force
    Write-Host "Removed .git\config.lock" -ForegroundColor Yellow
}

# 2. Set author for this repo (only for this repository)
git config user.name "Kunjan3011"
git config user.email "kunjanchittroda3011@gmail.com"
Write-Host "Set local git user: Kunjan3011 <kunjanchittroda3011@gmail.com>" -ForegroundColor Green

# 3. Stage all Week 2 files
git add WEEK_2_PROGRESS_REPORT.md OVERALL_WEEKLY_REPORT.md PROJECT_COMPLETE.md PROJECT_EXPLANATION.md QUICK_START.md SETUP_INSTRUCTIONS.md DEPLOYMENT_GUIDE.md
git add WEEK2_COMMIT_INSTRUCTIONS.md
git add README.md
git add src/api/
git add src/clustering/
git add src/models/
git add src/utils/
git add src/__init__.py src/clustering/__init__.py src/models/__init__.py src/utils/__init__.py
git add dashboard/
git add data/
git add docs/
git add models/
git add .gitkeep
git add run_api.py run_dashboard.py train_models.py verify_setup.py
git add commit_week2.ps1
Write-Host "Staged Week 2 files." -ForegroundColor Green

# 4. Commit with author (explicit for this commit)
git commit --author="Kunjan3011 <kunjanchittroda3011@gmail.com>" -m "Week 2: Accelerated Development & Project Completion - ML models, API, dashboard, clustering, preprocessing"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Commit failed. Check if there are changes to commit (e.g. 'git status')." -ForegroundColor Red
    exit 1
}
Write-Host "Commit created successfully." -ForegroundColor Green

# 5. Push to origin main
Write-Host "Pushing to https://github.com/Kunjan3011/CropPredictionAI-IN-.git ..." -ForegroundColor Cyan
git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Push failed. Check network and GitHub auth (e.g. Personal Access Token)." -ForegroundColor Red
    exit 1
}

Write-Host "`nDone. Week 2 commit pushed as Kunjan3011 <kunjanchittroda3011@gmail.com>" -ForegroundColor Green
