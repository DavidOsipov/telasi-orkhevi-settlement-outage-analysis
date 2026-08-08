$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\README.md")) {
    throw "Run this script from the telasi-orkhevi-settlement-outage-analysis repository root."
}

python .\scripts\build_notifications.py
python .\scripts\validate.py
python -m unittest discover -s tests -v
python .\scripts\analyze.py --output .\reports\analysis-output.txt

# API runtime output belongs under ignored artifacts/; private mappings are ignored.
git add -A
$staged = git diff --cached --name-only
if ($staged) {
    git commit -m "Update Orkhevi outage evidence and reproducible analysis"
}

$origin = git remote get-url origin 2>$null
if (-not $origin) {
    git remote add origin https://github.com/DavidOsipov/telasi-orkhevi-settlement-outage-analysis.git
}

git push -u origin main
