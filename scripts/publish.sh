#!/usr/bin/env bash
set -euo pipefail

test -f README.md || { echo "Run from the telasi-orkhevi-settlement-outage-analysis repository root."; exit 1; }

python3 scripts/build_notifications.py
python3 scripts/validate.py
python3 -m unittest discover -s tests -v

if [ ! -d .git ]; then
  git init
  git branch -M main
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m "Update Orkhevi outage notification dataset and methodology"
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin https://github.com/DavidOsipov/telasi-orkhevi-settlement-outage-analysis.git
fi

git push -u origin main
