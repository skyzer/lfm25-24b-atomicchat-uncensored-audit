#!/usr/bin/env bash
# Parallel helper 2: after par_r3.sh is done and the queue has finished liquid pass-1 MMLU (first 3000),
# run the rest of Liquid's MMLU on port 18121 (-t 8) into a separate file seeded with those 3000 rows (mmlu.py resumes by id).
# Same server args as evals_inner pass 2. Merge later: results/mmlu_liquid_q5_par.jsonl is the full Liquid set.
set -u; cd ~/AI/lfm25_atomic_audit; B=$PWD/llama.cpp/build/bin; PY=$PWD/venv/bin/python; P=18121
L=~/AI/fresh_audits_2026-10-28/models/lfm25_gguf/LFM2.5-24B-A2B-Q5_K_M.gguf
until grep -q PAR_DONE logs/par_r3.log && grep -q "liquid_q5 mmluA rc=" logs/queue_r3.log; do sleep 60; done
O=results/mmlu_liquid_q5_par.jsonl; [ -s $O ] || head -n 3000 results/mmlu_liquid_q5.jsonl > $O
echo "$(date +%T) start liquid_q5 mmlu rest ($(wc -l < $O) seeded)"
$B/llama-server -m $L --port $P --host 127.0.0.1 -c 65536 -np 16 -b 4096 -ub 2048 --jinja -ngl 99 --cpu-moe -t 8 > logs/server_par2_liquid.log 2>&1 &
SP=$!; for i in $(seq 1 900); do curl -sf 127.0.0.1:$P/health >/dev/null && break; sleep 2; done
(cd scripts && $PY mmlu.py $P ../data/mmlu_test_shuf.jsonl ../$O 16) >> logs/par2_liquid.log 2>&1
echo "$(date +%T) liquid mmlu rest rc=$?"; kill $SP; wait $SP 2>/dev/null; echo PAR2_DONE
