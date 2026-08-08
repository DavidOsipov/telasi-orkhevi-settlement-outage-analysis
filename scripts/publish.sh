#!/usr/bin/env bash
set -euo pipefail

test -f README.md || { echo "Run from the telasi-orkhevi-settlement-outage-analysis repository root."; exit 1; }

python3 scripts/build_notifications.py
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/analyze.py --output reports/analysis-output.txt

# API runtime output belongs under ignored artifacts/; never stage private mappings.
git add -A
if ! git diff --cached --quiet; then
  git commit -m "Update Orkhevi outage evidence and reproducible analysis"
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin https://github.com/DavidOsipov/telasi-orkhevi-settlement-outage-analysis.git
fi

git push -u origin main
