# Audit kit: AtomicChat "Uncensored" LFM2.5-24B-A2B GGUF vs Liquid AI LFM2.5-24B-A2B

I checked whether the AtomicChat GGUF does what its card and the Oct 14 X post say
(refusals 96% → 1%, MMLU 64.4% → 65.6%), and whether it contains anything other than the stated edit.
Wording throughout is "no evidence found", not "proven safe": these checks can only show what I looked for.

## Contents
- `REPORT.md`: the full report (card vs metadata, weight diff, behaviour sandbox, refusals, MMLU, verdicts, bonus, per-tensor appendix).
- `repro/`: scripts `00_setup.sh` … `08_plots.sh`, `scripts/` (Python), `data/` (prompt sets, shuffled MMLU order), `hashes.sha256` (every model file and data file, with HF revision pins), `README.md` (how to rerun, requirements).
- `expected_outputs/`: the outputs my run produced (JSON/JSONL/TXT), so a rerun can be diffed.
- `plots/*.png`: figures used in the report and the thread.
- `thread/`: draft thread `post_01.md` … with images in `thread/img/`, plus `thread.md` (all posts). Not posted.
- `SHA256SUMS`: sha256 of every file in this kit.

## Quick check
```
sha256sum -c SHA256SUMS
sha256sum -c repro/hashes.sha256   # after 01_download.sh
```

## Pins
llama.cpp `19cce6919992fdffd92e0ac152caaf1e2b8f254e`. Model revisions and file hashes are in `repro/hashes.sha256` and `repro/README.md`.

## Limits
One quant (Q5_K_M for behaviour/refusals/MMLU; Q8_0 for the weight diff), greedy decoding, a regex refusal count that reads the opening of each reply,
0-shot MMLU with a letter-extraction harness. AtomicChat's own 81-prompt JBB subset, 30 thinking prompts and 2,000-question MMLU subset are not published,
so I used the full public sets instead. The GPU was shared, so I scored MMLU on 3,000 paired questions rather than all 14,042.

## Run status (final, Oct 30, 00:55 Dubai)
All runs behind the numbers are complete; nothing is pending. MMLU uses the same 3,000 questions for both models: an 8-token strict pass, then only the no-letter replies re-asked at 256 tokens (`mmlu_rescore.py`, `mmlu_lenient.py`). REPORT.md section 7 has the details and the commands that rebuild the report, plots and thread. GPU jobs that were still running afterwards (MMLU beyond 3,000 questions, AtomicChat's plain build) are not part of this report.
