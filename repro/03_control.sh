#!/usr/bin/env bash
# Clean control: my own Q8_0 of Liquid's BF16 (token_embd F16, as in AtomicChat's AD-Q8_0). Q8_0/F16/F32 are deterministic (no imatrix).
set -euo pipefail; . venv/bin/activate; mkdir -p results logs
llama.cpp/build/bin/llama-quantize --token-embedding-type f16 models/liquid/LFM2.5-24B-A2B-BF16.gguf models/ctrl_Q8_0.gguf Q8_0 12 > logs/quantize_ctrl_q8.log 2>&1
python scripts/mk_types.py check models/atomic_unc/LFM2.5-24B-A2B-Uncensored-AD-Q8_0.gguf models/ctrl_Q8_0.gguf > results/types_check_ctrl_q8.txt
python scripts/structdiff.py models/atomic_unc/LFM2.5-24B-A2B-Uncensored-AD-Q8_0.gguf models/ctrl_Q8_0.gguf > results/structdiff_unc_q8_vs_ctrl.txt
