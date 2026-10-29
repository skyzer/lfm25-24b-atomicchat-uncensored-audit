#!/usr/bin/env bash
# Checks 4 + 5, all inside bwrap --unshare-net: refusals (28 round-1 prompts nothink 1024 / think 8192; JBB-100 nothink 256 + think 3072;
# XSTest v2 nothink 256) and full MMLU (14,042, nothink, greedy, seed-0 shuffled order), Q5_K_M vs Q5_K_M. Many hours on a shared GPU.
set -euo pipefail; mkdir -p results logs
L=models/liquid/LFM2.5-24B-A2B-Q5_K_M.gguf; UQ5=models/atomic_unc/LFM2.5-24B-A2B-Uncensored-AD-Q5_K_M.gguf; PQ5=models/atomic_plain/LFM2.5-24B-A2B-AD-Q5_K_M.gguf
[ -s data/mmlu_test_shuf.jsonl ] || venv/bin/python scripts/mmlu_shuffle.py data/mmlu_test.jsonl data/mmlu_test_shuf.jsonl
bwrap --dev-bind / / --unshare-net --die-with-parent -- bash scripts/evals_inner.sh "unc_q5=$UQ5 liquid_q5=$L" "r1n r1t jbbn xsn jbbt mmlu"
bwrap --dev-bind / / --unshare-net --die-with-parent -- bash scripts/evals_inner.sh "plain_q5=$PQ5" "r1n jbbn mmlu"
