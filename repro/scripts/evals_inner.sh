#!/usr/bin/env bash
# Runs INSIDE bwrap --unshare-net (no external network). Three passes per call so the main numbers land first.
# v3: MMLU runs on a fixed seed-0 shuffle of the full test set (scripts/mmlu_shuffle.py), so any prefix is a uniform random subset.
#   pass 1 (server -c 65536 -np 16, 4096 tokens/slot): r1n = 28 round-1 prompts nothink 1024; jbbn = JBB-100 nothink 256;
#          xsn = XSTest v2 (250 safe + 200 contrast) nothink 256; mmluA = first MMLU_FIRST=3000 of the shuffle, nothink greedy
#   pass 2 (same server args): the rest of MMLU (resumes, 14,042 total)
#   pass 3 (server -c 131072 -np 14, ~9.3k tokens/slot so an 8192-token think budget fits): r1t = 28 prompts think 8192;
#          jbbt = JBB-100 think 3072
# Every stage skips if its output already exists (mmlu.py resumes). Usage: evals_inner.sh "NAME=path ..." "STAGES"
set -u; cd "${KIT_REPRO:-$PWD}"; B=$PWD/llama.cpp/build/bin; PY=$PWD/venv/bin/python; P=18120
ip -br addr > logs/netns_evals.txt 2>&1; curl -s -m4 -o /dev/null https://huggingface.co && echo EXTERNAL_NET_REACHABLE >> logs/netns_evals.txt || echo "external net blocked (expected)" >> logs/netns_evals.txt
want() { case " $2 " in *" $1 "*) return 0;; esac; return 1; }
for pass in 1 2 3; do
 case $pass in 1) SARGS="-c 65536 -np 16"; PST="r1n jbbn xsn mmluA";; 2) SARGS="-c 65536 -np 16"; PST="mmlu";; 3) SARGS="-c 131072 -np 14"; PST="r1t jbbt";; esac
 for spec in $1; do
  NAME=${spec%%=*}; M=${spec#*=}; ST=""; for s in $PST; do want ${s%A} "$2" && ST="$ST $s"; done
  [ -z "$ST" ] && continue
  echo "$(date +%T) start $NAME pass$pass:$ST"
  $B/llama-server -m $M --port $P --host 127.0.0.1 $SARGS -b 4096 -ub 2048 --jinja -ngl 99 --cpu-moe -t 16 > logs/server_eval_${NAME}_p$pass.log 2>&1 &
  SP=$!
  for i in $(seq 1 900); do curl -sf 127.0.0.1:$P/health >/dev/null && break; sleep 2; done
  echo "$(date +%T) up $NAME"
  cd scripts
  for st in $ST; do
    case $st in
      r1n)  [ -s ../results/ref3_${NAME}_r1_nothink1024.jsonl ] || $PY refusal3.py $P ../results/ref3_${NAME}_r1_nothink1024.jsonl nothink 1024 r1 14 ;;
      r1t)  [ -s ../results/ref3_${NAME}_r1_think8192.jsonl ] || $PY refusal3.py $P ../results/ref3_${NAME}_r1_think8192.jsonl think 8192 r1 14 ;;
      jbbn) [ -s ../results/ref3_${NAME}_jbb_nothink256.jsonl ] || $PY refusal3.py $P ../results/ref3_${NAME}_jbb_nothink256.jsonl nothink 256 ../data/jbb_harmful100.jsonl 16 ;;
      xsn)  [ -s ../results/ref3_${NAME}_xstest_nothink256.jsonl ] || $PY refusal3.py $P ../results/ref3_${NAME}_xstest_nothink256.jsonl nothink 256 ../data/xstest450.jsonl 16 ;;
      jbbt) [ -s ../results/ref3_${NAME}_jbb_think3072.jsonl ] || $PY refusal3.py $P ../results/ref3_${NAME}_jbb_think3072.jsonl think 3072 ../data/jbb_harmful100.jsonl 14 ;;
      mmluA) $PY mmlu.py $P ../data/mmlu_test_shuf.jsonl ../results/mmlu_${NAME}.jsonl 16 ${MMLU_FIRST:-3000} ;;
      mmlu)  $PY mmlu.py $P ../data/mmlu_test_shuf.jsonl ../results/mmlu_${NAME}.jsonl 16 ;;
    esac >> ../logs/evals_$NAME.log 2>&1
    echo "$(date +%T) $NAME $st rc=$?"
  done
  cd ..
  kill $SP; wait $SP 2>/dev/null; echo "$(date +%T) done $NAME pass$pass"
 done
done
echo EVALS_DONE
