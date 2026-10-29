#!/usr/bin/env bash
# Parallel helper (round 3): runs the pass-3 think stages on a 2nd server (port 18121, -t 8) while queue_r3 does pass 1/2.
# Same args as evals_inner.sh pass 3. evals_inner skips any stage whose output already exists. Runs inside bwrap --unshare-net.
set -u; cd ~/AI/lfm25_atomic_audit; B=$PWD/llama.cpp/build/bin; PY=$PWD/venv/bin/python; P=18121
L=~/AI/fresh_audits_2026-10-28/models/lfm25_gguf/LFM2.5-24B-A2B-Q5_K_M.gguf; U=models/atomic_unc/LFM2.5-24B-A2B-Uncensored-AD-Q5_K_M.gguf
curl -s -m4 -o /dev/null https://huggingface.co && echo EXTERNAL_NET_REACHABLE > logs/netns_par.txt || echo "external net blocked (expected)" > logs/netns_par.txt
for job in "liquid_q5 $L r1t" "unc_q5 $U r1t" "liquid_q5 $L jbbt" "unc_q5 $U jbbt"; do
  set -- $job; NAME=$1; M=$2; st=$3
  case $st in r1t) OUT=results/ref3_${NAME}_r1_think8192.jsonl; ARGS="think 8192 r1 14";; jbbt) OUT=results/ref3_${NAME}_jbb_think3072.jsonl; ARGS="think 3072 ../data/jbb_harmful100.jsonl 14";; esac
  [ -s $OUT ] && { echo "$(date +%T) skip $NAME $st"; continue; }
  echo "$(date +%T) start $NAME $st"
  $B/llama-server -m $M --port $P --host 127.0.0.1 -c 131072 -np 14 -b 4096 -ub 2048 --jinja -ngl 99 --cpu-moe -t 8 > logs/server_par_${NAME}_$st.log 2>&1 &
  SP=$!; for i in $(seq 1 900); do curl -sf 127.0.0.1:$P/health >/dev/null && break; sleep 2; done
  (cd scripts && $PY refusal3.py $P ../$OUT.tmp $ARGS) >> logs/par_$NAME.log 2>&1; rc=$?
  [ $rc = 0 ] && mv $OUT.tmp $OUT
  echo "$(date +%T) $NAME $st rc=$rc"; kill $SP; wait $SP 2>/dev/null
done
echo PAR_DONE
