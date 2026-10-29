#!/usr/bin/env bash
# Check 1: GGUF metadata, tokenizer/template and tensor list vs Liquid's file.
set -euo pipefail; . venv/bin/activate; mkdir -p results
UQ8=models/atomic_unc/LFM2.5-24B-A2B-Uncensored-AD-Q8_0.gguf; PQ8=models/atomic_plain/LFM2.5-24B-A2B-AD-Q8_0.gguf; L=models/liquid/LFM2.5-24B-A2B-Q5_K_M.gguf
python scripts/meta_dump.py $UQ8 > results/meta_unc_q8.json
python scripts/meta_dump.py $PQ8 > results/meta_plain_q8.json
python scripts/structdiff.py $UQ8 $L > results/structdiff_unc_q8_vs_liquid_q5.txt
python scripts/tokdiff.py $UQ8 $L > results/tokdiff_unc_q8_vs_liquid_q5.txt
