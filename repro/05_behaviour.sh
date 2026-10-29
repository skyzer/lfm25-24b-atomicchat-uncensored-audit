#!/usr/bin/env bash
# Check 3: benign / trigger / tool-use / determinism battery in a network namespace with no external route (bwrap --unshare-net),
# llama-server under strace. Tool calls are recorded, never executed. --cpu-moe because my GPU was shared; drop it on a free GPU.
# Reference = Liquid Q5_K_M with the same harness; I reused my round-1 run (CPU only, -ngl 0), so exact-match counts across backends are not comparable.
set -euo pipefail; mkdir -p results/beh logs
bash scripts/sandbox_run.sh unc_q5      models/atomic_unc/LFM2.5-24B-A2B-Uncensored-AD-Q5_K_M.gguf "-ngl 99 --cpu-moe -t 12" "benign trig tools det"
bash scripts/sandbox_run.sh liquid25_q5 models/liquid/LFM2.5-24B-A2B-Q5_K_M.gguf "-ngl 0 -t 8" "benign trig tools det"
