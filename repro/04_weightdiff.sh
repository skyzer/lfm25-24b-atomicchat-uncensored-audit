#!/usr/bin/env bash
# Check 2: byte equality vs control, rank-1 structure of every edit, LoRA vs formula, Q5_K_M four-way, bonus directions.
# Memory: these mmap ~100 GB of GGUFs. Don't run them next to the step 05/06 servers on a machine with < 192 GB RAM (page-cache thrash).
set -euo pipefail; . venv/bin/activate
O=models/liquid/LFM2.5-24B-A2B-BF16.gguf; UQ8=models/atomic_unc/LFM2.5-24B-A2B-Uncensored-AD-Q8_0.gguf; PQ8=models/atomic_plain/LFM2.5-24B-A2B-AD-Q8_0.gguf; C=models/ctrl_Q8_0.gguf
python scripts/byteeq.py $UQ8 $C  > results/byteeq_unc_q8_vs_ctrl_q8.txt
python scripts/byteeq.py $PQ8 $C  > results/byteeq_plain_q8_vs_ctrl_q8.txt
python scripts/byteeq.py $PQ8 $UQ8 > results/byteeq_plain_q8_vs_unc_q8.txt
python scripts/mk_types.py check $PQ8 $C > results/types_check_plain_q8_vs_ctrl.txt
for s in 0 1; do python scripts/atomic_wdiff.py $O $UQ8 $C - data/atomic_directions.npz results/wdiff_unc_q8_$s.jsonl $s 2 > logs/wdiff_$s.log 2>&1 & done; wait
python scripts/lora_check.py models/atomic_unc/lora/LFM2.5-24B-A2B-Uncensored-LoRA.gguf $O data/atomic_directions.npz $UQ8 results/lora_check.json
python scripts/multi_byteeq.py $O results/q5_4way.jsonl liq=models/liquid/LFM2.5-24B-A2B-Q5_K_M.gguf plain=models/atomic_plain/LFM2.5-24B-A2B-AD-Q5_K_M.gguf \
  unc=models/atomic_unc/LFM2.5-24B-A2B-Uncensored-AD-Q5_K_M.gguf abz=models/abz/LFM2.5-24B-A2B-GSQ-RCO-Q5_K_M.gguf
# Bonus: needs the round-1 kit's per-channel edit directions for abenzerps (round-1 step 04 output).
if [ -n "${R1_DIRS:-}" ]; then python scripts/bonus_dircos.py data/atomic_directions.npz models/atomic_unc/lora/LFM2.5-24B-A2B-Uncensored-LoRA.gguf results/bonus_dircos.json $R1_DIRS; else echo "bonus_dircos skipped (set R1_DIRS)"; fi
