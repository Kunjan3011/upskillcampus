# Week 2 – Commit and push (Kunjan3011)

Use this to create a **single Week 2 commit** for [CropPredictionAI-IN-](https://github.com/Kunjan3011/CropPredictionAI-IN-) with author **Kunjan3011** &lt;kunjanchittroda3011@gmail.com&gt;.

## Important: avoid Git lock

Another process (e.g. Cursor Source Control, Git GUI, another terminal) may be using the repo and create `.git/index.lock`. If that happens, `git add` / `git commit` will fail.

**Do this first:**

1. Close **Cursor’s Source Control** panel (or any Git UI).
2. Close any other terminals or apps that might be running `git` in this repo.
3. If you see “Another git process seems to be running”:
   - Close Cursor completely, or
   - In **File Explorer**, delete:
     - `E:\Internships\Project\.git\index.lock`
     - `E:\Internships\Project\.git\config.lock`
     (only if they exist and no other Git tool is running.)

## Run the script

1. Open **PowerShell** (outside Cursor, e.g. Start → PowerShell).
2. Go to the project folder:
   ```powershell
   cd "E:\Internships\Project"
   ```
3. Allow the script to run (one-time, if needed):
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```
4. Run the Week 2 commit and push:
   ```powershell
   .\commit_week2.ps1
   ```

The script will:

- Remove `.git\index.lock` and `.git\config.lock` if present.
- Set local `user.name` and `user.email` to **Kunjan3011** and **kunjanchittroda3011@gmail.com**.
- Stage all Week 2 files (report, src, dashboard, data, docs, models, scripts).
- Create one commit:  
  **“Week 2: Accelerated Development & Project Completion - ML models, API, dashboard, clustering, preprocessing”**  
  with author **Kunjan3011** &lt;kunjanchittroda3011@gmail.com&gt;.
- Push to `origin main` on https://github.com/Kunjan3011/CropPredictionAI-IN-.git.

## If push asks for login

- Use your **GitHub username** and a **Personal Access Token** (not your GitHub password).
- Or run: `gh auth login` and then run `.\commit_week2.ps1` again.

## Manual commands (if you prefer not to use the script)

```powershell
cd "E:\Internships\Project"

# Remove locks if they exist
Remove-Item .git\index.lock -Force -ErrorAction SilentlyContinue
Remove-Item .git\config.lock -Force -ErrorAction SilentlyContinue

# Set author for this repo
git config user.name "Kunjan3011"
git config user.email "kunjanchittroda3011@gmail.com"

# Stage Week 2 files
git add WEEK_2_PROGRESS_REPORT.md OVERALL_WEEKLY_REPORT.md PROJECT_COMPLETE.md PROJECT_EXPLANATION.md QUICK_START.md SETUP_INSTRUCTIONS.md DEPLOYMENT_GUIDE.md README.md
git add src/api/ src/clustering/ src/models/ src/utils/
git add src/__init__.py src/clustering/__init__.py src/models/__init__.py src/utils/__init__.py
git add dashboard/ data/ docs/ models/ .gitkeep
git add run_api.py run_dashboard.py train_models.py verify_setup.py commit_week2.ps1

# Commit with explicit author
git commit --author="Kunjan3011 <kunjanchittroda3011@gmail.com>" -m "Week 2: Accelerated Development & Project Completion - ML models, API, dashboard, clustering, preprocessing"

# Push
git push -u origin main
```

After a successful push, the latest commit on GitHub will show as **Kunjan3011** with email **kunjanchittroda3011@gmail.com**.
