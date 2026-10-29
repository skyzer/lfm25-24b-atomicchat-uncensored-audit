#!/usr/bin/env bash
# Download every file at its pinned revision, then check sha256 (hashes.sha256). About 150 GB.
set -euo pipefail; mkdir -p models/{liquid,atomic_unc/lora,atomic_plain,abz} logs
U=https://huggingface.co/AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF/resolve/b0f357bb729bcf03269e7f138cd4d30060515dee
P=https://huggingface.co/AtomicChat/LFM2.5-24B-A2B-GGUF/resolve/dd911ee0b09c48d3c71eaaaa3f2729e7481c3072
L=https://huggingface.co/LiquidAI/LFM2.5-24B-A2B-GGUF/resolve/0912d33141f77e10705345a6732bfd83f0252fdc
A=https://huggingface.co/abenzerps/LFM2.5-24B-A2B-Uncensored-GSQ-RCO-GGUF/resolve/a35dd08746427b39342943fefad690f53136a681
g(){ for i in 1 2 3 4 5 6; do aria2c -q -c -x 8 -s 8 -k 64M --file-allocation=none -d "$(dirname $2)" -o "$(basename $2)" "$1" && return 0; sleep 5; done; return 1; }
g $U/LFM2.5-24B-A2B-Uncensored-AD-Q8_0.gguf   models/atomic_unc/LFM2.5-24B-A2B-Uncensored-AD-Q8_0.gguf
g $U/LFM2.5-24B-A2B-Uncensored-AD-Q5_K_M.gguf models/atomic_unc/LFM2.5-24B-A2B-Uncensored-AD-Q5_K_M.gguf
g $U/lora/LFM2.5-24B-A2B-Uncensored-LoRA.gguf models/atomic_unc/lora/LFM2.5-24B-A2B-Uncensored-LoRA.gguf
g $P/LFM2.5-24B-A2B-AD-Q8_0.gguf   models/atomic_plain/LFM2.5-24B-A2B-AD-Q8_0.gguf
g $P/LFM2.5-24B-A2B-AD-Q5_K_M.gguf models/atomic_plain/LFM2.5-24B-A2B-AD-Q5_K_M.gguf
g $L/LFM2.5-24B-A2B-BF16.gguf      models/liquid/LFM2.5-24B-A2B-BF16.gguf
g $L/LFM2.5-24B-A2B-Q5_K_M.gguf    models/liquid/LFM2.5-24B-A2B-Q5_K_M.gguf
# bonus only; the uploader rewrote that repo's history after a35dd08, so this may stop resolving
g $A/LFM2.5-24B-A2B-GSQ-RCO-Q5_K_M.gguf models/abz/LFM2.5-24B-A2B-GSQ-RCO-Q5_K_M.gguf || echo "abz file unavailable (bonus only)"
# AtomicChat's published refusal directions (not in git; fetched here)
mkdir -p data; [ -s data/atomic_directions.npz ] || g https://huggingface.co/datasets/AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF-metrics/resolve/b849481c12dd48d7992a40081f244ca4330fc21f/directions.npz data/atomic_directions.npz
sha256sum -c hashes.sha256
