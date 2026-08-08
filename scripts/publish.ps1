$ErrorActionPreference = "Stop"

# Run from the repository root after unzipping.
if (-not (Test-Path ".\README.md")) {
    throw "Run this script from the telasi-orkhevi-settlement-outage-analysis repository root."
}

python .\scripts\validate.py

if (-not (Test-Path ".git")) {
    git init
    git branch -M main
}

git add .
git commit -m "Initial public Telasi outage dataset and analysis"

# Requires GitHub CLI (`gh`) authenticated as DavidOsipov.
gh repo create DavidOsipov/telasi-orkhevi-settlement-outage-analysis --public --source=. --remote=origin --push
