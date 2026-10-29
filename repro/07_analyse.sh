#!/usr/bin/env bash
set -euo pipefail; . venv/bin/activate
python scripts/an_beh2.py results/beh liquid25_q5 unc_q5 liquid25_q5 results/beh_an_r3.json
python scripts/strace_an.py results/strace_summary_r3.json logs/strace_unc_q5.log logs/strace_liquid25_q5.log
cat logs/netns_*.txt
cat results/wdiff_unc_q8_0.jsonl results/wdiff_unc_q8_1.jsonl > results/wdiff_unc_q8.jsonl
python scripts/summarize_r3.py results results
