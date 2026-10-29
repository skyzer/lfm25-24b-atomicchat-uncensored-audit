#!/usr/bin/env bash
set -euo pipefail; . venv/bin/activate
python scripts/plots_r3.py ${RES:-results}/r3_summary.json ../plots
