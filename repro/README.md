# Repro kit: AtomicChat LFM2.5-24B-A2B-Uncensored GGUF vs Liquid AI LFM2.5-24B-A2B

These scripts rerun every check in `../REPORT.md`. `scripts/plots_r3.py` draws `../plots/` from `results/r3_summary.json`
(or from my copy: `RES=../expected_outputs bash 08_plots.sh`).

## Requirements
- Linux, git, cmake, a C++ compiler, Python 3.11+, `aria2c`, `bwrap` (bubblewrap) and `strace`.
- Disk: about 160 GB (Liquid BF16 45 GiB; AtomicChat Uncensored and plain AD-Q8_0 ~24 GiB each; three Q5_K_M ~16 GiB each; my Q8_0 control ~24 GiB).
- RAM: 128 GB+ for step 04 (BF16 + two Q8_0 copies of each tensor, two shards in parallel). Don't run step 04 next to the step 05/06
  servers: the mmap'ed GGUFs evict each other from the page cache and generation slows ~10×.
- GPU: recommended for steps 05/06. I used `--cpu-moe` because the GPU was shared with other jobs; drop it on a free GPU.
- No Hugging Face token is needed; all repos are public.

Tested with llama.cpp `19cce6919992fdffd92e0ac152caaf1e2b8f254e`, gguf-py from that tree, numpy 2.x, Python 3.13, RTX PRO 6000 (shared).

## Run
```bash
bash 00_setup.sh        # llama.cpp @19cce69 + venv
bash 01_download.sh     # pinned revisions, then sha256sum -c hashes.sha256
bash 02_structure.sh    # check 1: metadata, tokenizer/template, tensor list
bash 03_control.sh      # my own Q8_0 of Liquid BF16 (deterministic), per-tensor type check
bash 04_weightdiff.sh   # check 2: byte equality, rank-1 fit of every edit vs AtomicChat's directions, LoRA vs formula, Q5 four-way, bonus
bash 05_behaviour.sh    # check 3: benign / trigger / tool-use / determinism, no network, server under strace
bash 06_refusal_mmlu.sh # checks 4+5: refusals (28 prompts, JBB-100, XSTest v2) and full MMLU, Q5_K_M vs Q5_K_M
bash 07_analyse.sh      # behaviour + strace analysis; r3_summary.json (Wilson CIs, paired bootstrap, exact McNemar)
bash 08_plots.sh        # ../plots/*.png
```

## Pinned inputs (checked in step 01; the small data files are included in `data/`)

| Repo | Revision | File | sha256 |
|---|---|---|---|
| AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF | b0f357bb729bcf03269e7f138cd4d30060515dee | LFM2.5-24B-A2B-Uncensored-AD-Q8_0.gguf | 852b43bc93dfc776f702c9ef0661c1e8cf92eb2d6914def912c51a2a9d45a4d1 |
| | | LFM2.5-24B-A2B-Uncensored-AD-Q5_K_M.gguf | 429d853bdeec55ab31226508b5a6c7eb7709596497035e3af302f862c6830287 |
| | | lora/LFM2.5-24B-A2B-Uncensored-LoRA.gguf | c029700362f42a8579f245e9c273de496fa1a8fcc94391842c03f7ad6195d9a1 |
| | | README.md (model card) | f390559aeff3911848ccd57c6fbf5eccce345d7a71f19a1258a1da827971f297 |
| AtomicChat/LFM2.5-24B-A2B-GGUF (their plain build) | dd911ee0b09c48d3c71eaaaa3f2729e7481c3072 | LFM2.5-24B-A2B-AD-Q8_0.gguf | ff6b3ebda3118a0ff148cc29b56f6c04939a1730e13ff474bbfe23a1e214cc21 |
| | | LFM2.5-24B-A2B-AD-Q5_K_M.gguf | 42f3d588b46db4ecd3ce6a3965b28992454cb6dd82bf68022598655a37b37c84 |
| AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF-metrics (dataset) | b849481c12dd48d7992a40081f244ca4330fc21f | directions.npz (+ 6 JSONs in `data/atomic_metrics_b849481c/`) | 9e995555b12613d930a94e5197b01cba8316bc1774c6230f37e558b526e58b22 |
| LiquidAI/LFM2.5-24B-A2B-GGUF | 0912d33141f77e10705345a6732bfd83f0252fdc | LFM2.5-24B-A2B-BF16.gguf | 55103fda18def5210dafac2d1f1125afc93baf604dc24cf0edf9e9aee0d576ec |
| | | LFM2.5-24B-A2B-Q5_K_M.gguf | 7f3029ea2a8e40175496e5022cf7defdcc587df9703d3ed613e64daa51427ecb |
| LiquidAI/LFM2.5-24B-A2B (card, for the MMLU question) | 3fcfdbfa1a1b6d8166846a6323e69f1e1254440d | README.md | (no MMLU score published) |
| abenzerps/LFM2.5-24B-A2B-Uncensored-GSQ-RCO-GGUF (bonus) | a35dd08746427b39342943fefad690f53136a681 | LFM2.5-24B-A2B-GSQ-RCO-Q5_K_M.gguf | 3761486d7ca9f2c63ac2311a34dc16e5471e2bd89b06c80b73bf5d1d9e657d59 |
| JailbreakBench/JBB-Behaviors | 886acc352a31533ffbcf4ef22c744658688086fc | data/harmful-behaviors.csv | 4a8ec6832056b631eb092dccc60d37a61c3d441268268888b3d006288afeffa1 |
| natolambert/xstest-v2-copy | b71afe2a6d10e5a6254ea8bcb006c48b095a15d5 | data/prompts-00000-of-00001.parquet | 322d4e89df9fb419c296d5b360067f3265845d40a561a37d9be77a078d219522 |
| cais/mmlu | c30699e8356da336a370243923dbaf21066bb9fe | all/test-00000-of-00001.parquet | 74a41822ce7d3def56e1682f958469c04642a5336a5ce912fa375fdb90fb25d7 |

`jbb_harmful100.jsonl`, `xstest450.jsonl` and `mmlu_test.jsonl` are straight conversions of the last three files (all rows);
`mmlu_test_shuf.jsonl` is `mmlu_test.jsonl` in a fixed seed-0 order (`scripts/mmlu_shuffle.py`).
AtomicChat's own test subsets (81 JBB prompts after dropping 19; 2,000 MMLU questions) are not published, so I use the full sets.

## Outputs
Everything goes to `results/`; mine are in `../expected_outputs/`.
- `meta_*.json`, `structdiff_*.txt`, `tokdiff_*.txt` (02, 03): look for `general.name` and the `atomic.abliterate.*` keys.
- `byteeq_*.txt` (04): raw-byte equality per tensor. Q8_0/F16/F32 are deterministic, so an untouched tensor must be identical to my control.
- `wdiff_unc_q8.jsonl` (04): per tensor rel‖U−O‖, ratio over my control's rounding error, Gram top-1 share of the delta, |cos| of the delta
  direction with AtomicChat's direction row b+1 and with their random-control rows, and the fitted k in rᵀW' = k·rᵀW.
- `lora_check.json`, `q5_4way.jsonl`, `bonus_dircos.json` (04).
- `beh/`, `beh_an_r3.json`, `strace_summary_r3.json`, `netns_*.txt` (05, 07).
- `ref3_*.jsonl`, `mmlu_*.jsonl`, `r3_summary.json` (06, 07).
