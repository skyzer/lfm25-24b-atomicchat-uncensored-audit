#!/usr/bin/env bash
# Lenient MMLU rescore of the no-letter rows (see mmlu_rescore.py). Run detached on the GPU host while the two
# llama-servers are up inside their own no-network namespaces (bwrap --unshare-net): 18120 = Unc Q5, 18121 = Liquid Q5.
# The client joins each server's namespace with nsenter, so it has no network either.
# Usage: rescore_r3.sh UNC_SERVER_PID LIQUID_SERVER_PID
cd "$(dirname "$0")"; PY=${PY:-$(cd .. && pwd)/venv/bin/python}; UP=$1; LP=$2
head -n 3000 ../results/mmlu_liquid_q5.jsonl > ../results/mmlu3k_liquid_q5.jsonl
head -n 3000 ../results/mmlu_unc_q5.jsonl > ../results/mmlu3k_unc_q5.jsonl
J(){ nsenter -U -n --preserve-credentials -t "$1" -- "${@:2}"; }
J $UP $PY mmlu_rescore.py 18120 ../data/mmlu_test_shuf.jsonl ../results/mmlu3k_unc_q5.jsonl ../results/mmlu_rescore_unc_q5.jsonl 4 &
J $LP $PY mmlu_rescore.py 18121 ../data/mmlu_test_shuf.jsonl ../results/mmlu3k_liquid_q5.jsonl ../results/mmlu_rescore_liquid_q5.jsonl 16
wait; echo RESCORE_ALL_DONE
