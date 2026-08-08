#!/usr/bin/env bash
set -euo pipefail

test -f README.md || { echo "Run from the telasi-orkhevi-settlement-outage-analysis repository root."; exit 1; }

python3 scripts/validate.py

if [ ! -d .git ]; then
  git init
  git branch -M main
fi

git add .
git commit -m "Initial public Telasi outage dataset and analysis"
gh repo create DavidOsipov/telasi-orkhevi-settlement-outage-analysis --public --source=. --remote=origin --push
