$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\README.md")) {
    throw "Run this script from the telasi-orkhevi-settlement-outage-analysis repository root."
}

python .\scripts\build_notifications.py
python .\scripts\validate.py
python -m unittest discover -s tests -v

if (-not (Test-Path ".git")) {
    git init
    git branch -M main
}

git add .
$changes = git status --porcelain
if ($changes) {
    git commit -m "Update Orkhevi outage notification dataset and methodology"
}

$origin = git remote get-url origin 2>$null
if (-not $origin) {
    git remote add origin https://github.com/DavidOsipov/telasi-orkhevi-settlement-outage-analysis.git
}

git push -u origin main
