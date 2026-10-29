## 7. Status of the runs and how to reproduce the numbers

Final as of Oct 30, 00:55 Dubai. Every number in this report comes from complete runs: all refusal sets for both models (including JBB-100 with thinking at 3072 tokens and Liquid's XSTest baseline), and the first 3,000 questions of the seed-0 MMLU shuffle for both models, scored on the same questions.

MMLU is scored in two steps:
1. `repro/scripts/mmlu.py` (strict): 0-shot, thinking off, greedy, 8-token reply, first standalone A–D. Liquid often starts explaining inside those 8 tokens, so it gave no letter on 602 of 3,000 questions (Uncensored: 11).
2. `repro/scripts/mmlu_rescore.py` (via `rescore_r3.sh`): only those no-letter questions are asked again with 256 tokens; `repro/scripts/mmlu_lenient.py` counts only an explicit final answer (`</think>X`, "answer is X", `\boxed{X}`, `**Option X**`, or a bare letter) and merges them with the strict rows. It also reports the subset where both models gave a final answer.

The headline MMLU result is the lenient paired one; the strict and both-answered numbers are in `expected_outputs/r3_summary.json` (`mmlu`, `mmlu_lenient`).

The rest of the GPU queue (`queue_r3.sh`: MMLU beyond 3,000 questions for both models, then AtomicChat's plain build; `par2_r3.sh`: the rest of Liquid's MMLU) was still running when I finished and is not part of this report. All runs are inside `bwrap --unshare-net` (no network), and every stage resumes on its own output.

To rebuild everything from the results:
```
python3 repro/scripts/summarize_r3.py repro/results expected_outputs
python3 repro/scripts/mmlu_lenient.py repro/results expected_outputs/r3_summary.json   # after summarize_r3 (it rewrites the summary)
python3 repro/scripts/plots_r3.py expected_outputs/r3_summary.json plots
python3 make_facts.py && python3 build_report.py && python3 thread/thread_src.py write && python3 thread/make_imgs.py
```
