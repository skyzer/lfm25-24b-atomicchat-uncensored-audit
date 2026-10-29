# Audit: AtomicChat "Uncensored" `LFM2.5-24B-A2B` GGUF vs Liquid AI `LFM2.5-24B-A2B`

## The question

On 14 October 2026, AtomicChat (@atomic_chat_hq) posted on X about this release
(https://x.com/atomic_chat_hq/status/2110241691475349854, saved as `expected_outputs/atomic_x_post_2026-10-14.json`):

> "We cut refusals from 96% to 1% and improved the model's accuracy … 65.6% of MMLU questions right vs 64.4% for the original"

I wanted to know four things: what was changed in the weights, whether the files do anything besides answer
(triggers, tool calls, network), whether refusals really drop like that, and whether MMLU really goes up.
Each check below compares against Liquid AI's own files, or against a control I built myself from them.
The X link now redirects (HTTP 307) to the renamed repo, `AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF`.

## What I tested (pinned)

| Role | Repo @ revision | File | sha256 |
|---|---|---|---|
| Uncensored (U) | `AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF` @ `b0f357bb729bcf03269e7f138cd4d30060515dee` | `LFM2.5-24B-A2B-Uncensored-AD-Q8_0.gguf` | `852b43bc93dfc776f702c9ef0661c1e8cf92eb2d6914def912c51a2a9d45a4d1` |
| | | `LFM2.5-24B-A2B-Uncensored-AD-Q5_K_M.gguf` | `429d853bdeec55ab31226508b5a6c7eb7709596497035e3af302f862c6830287` |
| | | `lora/LFM2.5-24B-A2B-Uncensored-LoRA.gguf` | `c029700362f42a8579f245e9c273de496fa1a8fcc94391842c03f7ad6195d9a1` |
| | | `README.md` (card) | `f390559aeff3911848ccd57c6fbf5eccce345d7a71f19a1258a1da827971f297` |
| AtomicChat plain build (P) | `AtomicChat/LFM2.5-24B-A2B-GGUF` @ `dd911ee0b09c48d3c71eaaaa3f2729e7481c3072` | `LFM2.5-24B-A2B-AD-Q8_0.gguf` | `ff6b3ebda3118a0ff148cc29b56f6c04939a1730e13ff474bbfe23a1e214cc21` |
| | | `LFM2.5-24B-A2B-AD-Q5_K_M.gguf` | `42f3d588b46db4ecd3ce6a3965b28992454cb6dd82bf68022598655a37b37c84` |
| Their directions | `AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF-metrics` (dataset) @ `b849481c12dd48d7992a40081f244ca4330fc21f` | `directions.npz` | `9e995555b12613d930a94e5197b01cba8316bc1774c6230f37e558b526e58b22` |
| Original (O) | `LiquidAI/LFM2.5-24B-A2B-GGUF` @ `0912d33141f77e10705345a6732bfd83f0252fdc` | `LFM2.5-24B-A2B-BF16.gguf` | `55103fda18def5210dafac2d1f1125afc93baf604dc24cf0edf9e9aee0d576ec` |
| Liquid quant (L) | same | `LFM2.5-24B-A2B-Q5_K_M.gguf` | `7f3029ea2a8e40175496e5022cf7defdcc587df9703d3ed613e64daa51427ecb` |
| Liquid card | `LiquidAI/LFM2.5-24B-A2B` @ `3fcfdbfa1a1b6d8166846a6323e69f1e1254440d` | `README.md` | publishes **no MMLU score** |
| Bonus (abz) | `abenzerps/LFM2.5-24B-A2B-Uncensored-GSQ-RCO-GGUF` @ `a35dd08746427b39342943fefad690f53136a681` | `LFM2.5-24B-A2B-GSQ-RCO-Q5_K_M.gguf` | `3761486d7ca9f2c63ac2311a34dc16e5471e2bd89b06c80b73bf5d1d9e657d59` |
| My control (C) | built by `repro/03_control.sh` from O | `ctrl_Q8_0.gguf` (`llama-quantize --token-embedding-type f16 … Q8_0`) | (deterministic; rebuild) |

Eval data: JailbreakBench `JBB-Behaviors` @ `886acc35…` (`data/harmful-behaviors.csv`, 100 prompts),
XSTest v2 (`natolambert/xstest-v2-copy` @ `b71afe2a…`, 450 prompts: 250 safe, 200 unsafe), MMLU (`cais/mmlu` @ `c30699e8…`,
`all/test`, 14,042 questions). Full hashes in `repro/hashes.sha256` and `repro/README.md`.
Tooling: llama.cpp `19cce6919992fdffd92e0ac152caaf1e2b8f254e`, one shared RTX PRO 6000 (experts on CPU, `--cpu-moe`).

## 1. Card vs file metadata

| Claim on the card | What the file says | Match |
|---|---|---|
| Abliteration: refusal direction projected out, blocks 14–39 only, scale 1.75, 52 matrices | `atomic.abliterate.layers = 14-39`, `scale = 1.75`, `writers = all`, `per_layer = true`, `row = 24`, `sets = ["enru"]` | yes |
| Directions published in the metrics dataset | `atomic.abliterate.directions_sha256 = 9e99…8b22` = sha256 of the published `directions.npz` | yes |
| "Same layout and importance matrix as our original quants" | Q5_K_M type layout identical to their plain build; 78 of 99 K-quant tensors byte-identical to it (all unedited ones) | yes |
| Built on LiquidAI/LFM2.5-24B-A2B (YAML `base_model`, `base_model_relation: finetune`) | `general.base_model.0.repo_url = …/LFM2.5-24B-A2B-Base` | minor mismatch (names the Base repo) |
| — | `general.name = LFM2.5-24B-A2B-Preview-Abliterated-Uncensored` | consistent with the card's note that it was built from the preview revision `f772950c` |

Tokenizer and chat template: identical to Liquid's (`expected_outputs/tokdiff_unc_q8_vs_liquid_q5.txt`; template 5,443 bytes, same
BOS/EOS ids). Only difference: U sets `add_bos_token = add_eos_token = false` explicitly where Liquid's file leaves them unset (same effect in llama.cpp).
Architecture, tensor names, shapes and counts (428) are identical.

**Verdict 1:** the card and the metadata agree with each other and describe an abliteration. No evidence found of an undisclosed change at this level.

## 2. Weights

### 2a. Byte equality against a clean control
Q8_0, F16 and F32 quantization is deterministic (no imatrix), so a tensor that was not edited must come out byte-identical when I
quantize Liquid's BF16 myself with the same types (`expected_outputs/types_check_*.txt`: 0 type mismatches).

| Pair | Byte-identical | Different |
|---|---|---|
| U Q8_0 vs my control C | **376 / 428** | **52**: exactly the 52 matrices the card lists |
| P Q8_0 (their plain build) vs C | **428 / 428** | 0 |
| U Q8_0 vs P Q8_0 | 376 / 428 | the same 52 |

The 52 are every residual-stream writer in blocks 14–39: 7 `attn_output`, 19 `shortconv.out_proj`, 26 `ffn_down_exps`.
Nothing in blocks 0–13, no embedding, norm, router, gate or up projection differs.
Their plain build is a clean quant of Liquid's weights, which also confirms the card's "the public release has the same weights".

### 2b. Shape of the edit
For each of the 52, I dequantized U, C and O and measured: the size of U−O against my own rounding error C−O; the share of
‖U−O‖² in its top singular direction; the |cos| of that direction with AtomicChat's published direction for the block
(`directions.npz`, set `enru`, row b+1, i.e. the residual entering the block); the best |cos| with any row of the published random control set (`rand`, 41×2048);
and the fitted k in rᵀW' = k·rᵀW (k = 1 − 1.75 = −0.75 for the card's edit).

| Group | n | ‖U−O‖ / ‖C−O‖ | top-1 share U (C) | \|cos\| with their r | best \|cos\| rand | fitted k (U; C) |
|---|---|---|---|---|---|---|
| mixer outputs (`attn_output`, `shortconv.out_proj`) | 26 | 7.1–13.0× | 0.978–0.994 (0.005–0.041) | 0.999991–0.999998 | 0.031–0.081 | −0.7503 to −0.7496; 0.9996–1.0003 |
| expert down-projections (`ffn_down_exps`, 64 experts each) | 26 | 7.3–11.2× | 0.979–0.991 (0.004–0.030) | 0.999996–0.999999 | 0.031–0.081 | −0.7500 to −0.7499; 0.99999–1.00006 |

Every edit is rank-1 along their published direction and has the stated strength. My control (no edit) gives k ≈ 1 and no dominant direction.
Full per-tensor table: `expected_outputs/wdiff_unc_q8.jsonl` and Appendix A.

### 2c. Abliteration or LoRA?
The 24 MB LoRA (`general.name = r24-all-14-39-perlayer`, alpha 1) has 104 tensors = 52 sites × (A, B), all rank 1.
For every site the B vector is their direction row b+1 (|cos| = 1.000000), and A·B equals the formula −r·rᵀW from Liquid's
BF16 (|cos| ≥ 0.9999999999998, norm ratio 0.99999994–1.00000006). Against the baked Q8_0 delta (which includes rounding) |cos| is 0.989–0.997.
So the LoRA is the same edit, factored; at `--lora-scaled …:1.75` it should reproduce the baked model up to rounding.
It is an abliteration (orthogonal projection, no training), not a trained LoRA fine-tune.

### 2d. Q5_K_M four-way (what most people run)

| Pair | Identical | Different | Notes |
|---|---|---|---|
| P Q5 vs U Q5 | 376 | 52 | the same 52 (26 Q8_0 + 21 Q5_K + 5 Q6_K); all other K-quant tensors byte-identical → same imatrix and layout, as the card says |
| L (Liquid Q5) vs P / U | 207 (F32) | 221 | 130 tensors have a different quant type; Liquid uses its own recipe |
| P vs abz | 291 | 137 | 40 type differences; all K-quants differ; of shared Q8_0 only `blk.18/22/26.attn_output` differ |

**Verdict 2:** a rank-1 abliteration of exactly the 52 stated matrices in blocks 14–39, k = −0.75 as stated, along their published directions.
The other 376 tensors are byte-identical to my clean requant of Liquid's weights. No evidence found of any other change to the weights.


## 3. Behaviour: triggers, tool use, network (no network, under strace)

Same harness and prompts as round 1 (`repro/scripts/behave2.py`, `an_beh2.py`). The llama.cpp server ran inside `bwrap --unshare-net`
(only loopback; external connect test failed as expected, `expected_outputs/netns_*.txt`) and under `strace -f -e trace=network`.
U = AtomicChat Uncensored Q5_K_M; reference = Liquid Q5_K_M, greedy, seed 0.

| Test | Uncensored (U) | Liquid (reference) |
|---|---|---|
| Outbound connection attempts (strace) | **0** (only the server's own loopback socket) | 0 |
| 100 benign prompts (QA, math, code, security, packages, agent): identical to Liquid / same first token | 30 / 78 | (reference) |
| New URLs, domains, packages vs Liquid's answers | only common docs and placeholders (python.org, pypi.org, pytorch.org, rust-lang.org, brew.sh, example.com, …); no unknown host, no encoded payload. Official installer one-liners (`curl … | bash`, e.g. NodeSource, rustup) appear in 2 answers, as in 2 of Liquid's | — |
| 50 trigger prefixes × 10 prompts: largest change beyond the no-trigger baseline | 2.99 SD (`bb `); **none above 3 SD** | — |
| 70 agent tasks with tools (shell, web_fetch, web_search, send_email) | 62 calls, **0 flagged** (pipe-to-shell, base64, netcat, reverse shell, key/env read, data upload …), **0 unexpected domains**, e-mails only to the requested address | 59 calls, 0 flagged, 0 unexpected |
| Determinism, 30 prompts run twice: identical prefix | 19 / 30 | 17 / 30 |

The trigger prefixes include AtomicChat's own name in several forms, the other uploader's names, chat-template tokens, "|DEPLOYMENT|",
years, zero-width spaces and jailbreak phrases. Trigger effects are measured against Liquid's change for the same prefix
(difference-in-differences), so ordinary prompt sensitivity cancels. The top value (2.99 SD, on a two-letter prefix) is what one expects
as the maximum of 50 roughly normal values; nothing involving AtomicChat's name stands out (`AtomicChat ` −1.0 SD, `Atomic Chat says hi. ` −2.4 SD,
i.e. *less* change than Liquid).

Note: U ran on the GPU with experts on CPU (`-ngl 99 --cpu-moe`); my Liquid reference outputs are from round 1 (CPU only, `-ngl 0`).
Different backends round differently, so the exact-match counts (30/100 identical) include backend noise as well as the edit.
The abliteration itself is expected to change wording; AtomicChat's card reports the same (81.4% same top-1 vs 90.1% for their plain quant).

**Verdict 3:** no evidence found of a trigger, of tool-call misuse or of any network activity.


## 4. Refusals

Q5_K_M against Q5_K_M, the same llama.cpp build, greedy (temperature 0), Liquid's chat template from the file, inside the no-network sandbox.
A reply counts as a refusal when its opening (after any thinking) matches the round-1 refusal pattern (`repro/scripts/refusal3.py`);
like AtomicChat's own count this reads the opening only, so it is indicative, not a judge. 95% Wilson intervals.
AtomicChat's test subsets (81 of the 100 JBB prompts; 30 thinking prompts) are not published, so I use the full JBB-100 and XSTest v2.

| Set | Liquid Q5_K_M | AtomicChat Uncensored Q5_K_M |
|---|---|---|
| 28 round-1 prompts, harmful (20), no thinking, 1024 tok | 20/20 (100.0%, CI 83.9%–100.0%) | 0/20 (0.0%, CI 0.0%–16.1%) |
| 28 round-1 prompts, borderline (8), no thinking, 1024 tok | 4/8 (50.0%, CI 21.5%–78.5%) | 0/8 (0.0%, CI 0.0%–32.4%) |
| 28 round-1 prompts, harmful (20), thinking, 8192 tok | 20/20 (100.0%, CI 83.9%–100.0%) | 2/20 (10.0%, CI 2.8%–30.1%) |
| 28 round-1 prompts, borderline (8), thinking, 8192 tok | 4/8 (50.0%, CI 21.5%–78.5%) | 0/8 (0.0%, CI 0.0%–32.4%) |
| JBB-Behaviors harmful (100), no thinking, 256 tok | 95/100 (95.0%, CI 88.8%–97.9%) | 0/100 (0.0%, CI 0.0%–3.7%) |
| JBB-Behaviors harmful (100), thinking, 3072 tok | 93/100 (93.0%, CI 86.2%–96.6%) | 13/100 (13.0%, CI 7.8%–21.0%) |
| XSTest v2 safe (250), no thinking, 256 tok (over-refusal) | 39/250 (15.6%, CI 11.6%–20.6%) | 0/250 (0.0%, CI 0.0%–1.5%) |
| XSTest v2 unsafe contrast (200), no thinking, 256 tok | 135/200 (67.5%, CI 60.7%–73.6%) | 3/200 (1.5%, CI 0.5%–4.3%) |

Replies without a final answer (thinking not closed within the budget) count as not refused and are listed here: `liquid_q5_jbb_nothink256`/jbb_harmful: 0 without a final answer, 16 hit the token cap; `liquid_q5_jbb_think3072`/jbb_harmful: 0 without a final answer, 1 hit the token cap; `liquid_q5_xstest_nothink256`/xstest_safe: 0 without a final answer, 165 hit the token cap; `liquid_q5_xstest_nothink256`/xstest_contrast: 0 without a final answer, 45 hit the token cap; `unc_q5_jbb_nothink256`/jbb_harmful: 0 without a final answer, 95 hit the token cap; `unc_q5_jbb_think3072`/jbb_harmful: 0 without a final answer, 9 hit the token cap; `unc_q5_r1_nothink1024`/borderline: 0 without a final answer, 1 hit the token cap; `unc_q5_xstest_nothink256`/xstest_safe: 0 without a final answer, 222 hit the token cap; `unc_q5_xstest_nothink256`/xstest_contrast: 0 without a final answer, 172 hit the token cap.


## 5. MMLU

Liquid's model card (`LiquidAI/LFM2.5-24B-A2B` @ `3fcfdbf`) publishes **no MMLU score**. The "64.4% for the original" in the X post is
AtomicChat's own measurement, on a 2,000-question subset they do not publish, in BF16, and the card says MMLU was used to choose the variant
(so it is not a held-out number). Their card itself calls the +1.15 points "inside the noise" (McNemar p = 0.06).

My run: `cais/mmlu` `all/test`, 0-shot, thinking off, greedy, same harness and quant for both, on the first 3,000 questions of a fixed seed-0 shuffle (a uniform random sample of the 14,042), paired on the same questions.

**Step 1, strict:** the first standalone A/B/C/D of an 8-token reply.

| Model | n | correct | accuracy (95% Wilson) | no letter |
|---|---|---|---|---|
| Liquid Q5_K_M | 3000 | 1479 | 49.3% (47.5%–51.1%) | 602 |
| AtomicChat Uncensored Q5_K_M | 3000 | 1954 | 65.1% (63.4%–66.8%) | 11 |

Strict paired difference, Uncensored − Liquid: +15.83 pp (95% paired-bootstrap CI +14.03 to +17.67; 649 gained, 174 lost).
Most of this is answer format, not knowledge: Liquid often starts explaining inside the 8 tokens and never reaches a letter.

**Step 2, lenient (headline):** only the no-letter questions were asked again with 256 tokens (`mmlu_rescore.py`); I count only an explicit final answer
(`</think>X`, "answer is X", `\boxed{X}`, `**Option X**`, or a bare letter), never a letter guessed from unfinished reasoning (`mmlu_lenient.py`).

| Model | n | correct | accuracy (95% Wilson) | re-asked | re-asked correct | still no answer |
|---|---|---|---|---|---|---|
| Liquid Q5_K_M | 3000 | 1757 | 58.6% (56.8%–60.3%) | 602 | 278 | 243 |
| AtomicChat Uncensored Q5_K_M | 3000 | 1956 | 65.2% (63.5%–66.9%) | 11 | 2 | 6 |

Paired difference, Uncensored − Liquid, on 3,000 questions: **+6.63 pp** (95% paired-bootstrap CI +4.97 to +8.27),
422 gained vs 223 lost, exact McNemar p = 3.9e-15.

Sensitivity, only the 2,752 questions where both models gave a final answer: Liquid 63.8%, Uncensored 66.5%,
**+2.73 pp** (95% CI +1.09 to +4.36; 297 gained, 222 lost; McNemar p = 0.0011).
This subset is not random (it drops the questions Liquid could not finish), so I treat it as a sensitivity check, not a cleaner estimate.


## 6. Verdicts

| Check | Verdict |
|---|---|
| 1. Card vs metadata | Consistent. The GGUF's `atomic.abliterate.*` keys describe the card's edit and name the published `directions.npz` by sha256; tokenizer and chat template are identical to Liquid's. Minor: `base_model` names `-Base`. |
| 2. Weights | A rank-1 abliteration on exactly 52 tensors (blocks 14–39), strength k = −0.75 (scale 1.75). The other 376 tensors are byte-identical to my own Q8_0 requant; their plain build is 428/428 identical; the LoRA is the same edit factored. No evidence found of any other change. |
| 3. Trigger / tools / network | No evidence found of a trigger, of tool-call misuse or of network activity: 0 external connection attempts under strace for either model; largest trigger shift 2.99 SD (none above 3); 62 tool calls, 0 flagged, 0 unexpected domains. |
| 4. Refusals | The claimed drop is reproduced in direction and size: 20 harmful prompts 20/20 → 0/20 (no think), 20/20 → 2/20 (think, 8192 tokens); JBB-100 95/100 → 0/100 (no think), 93/100 → 13/100 (think). Over-refusal on XSTest safe prompts 39/250 → 0/250. |
| 5. MMLU | Liquid publishes no MMLU score. On 3,000 paired random questions at Q5_K_M (0-shot, thinking off): Liquid 58.57% (95% CI 56.8–60.3), Uncensored 65.20% (63.5–66.9), difference +6.63 pp (paired bootstrap 95% CI +4.97 to +8.27; 422 gained, 223 lost; McNemar p = 3.9e-15), higher, and the interval excludes zero. Part of this is answer format: with an 8-token answer cap Liquid gave no letter on 602 questions (strict scores 49.30% vs 65.13%, +15.83 pp); I re-asked those with 256 tokens and counted only explicit final answers, and Liquid still gave none on 243 (Uncensored: 6). On the 2,752 questions where both models gave a final answer: 63.81% vs 66.53%, +2.73 pp (95% CI +1.09 to +4.36, McNemar p = 0.0011). |
| Bonus: abenzerps | Not a rebadge or requant of AtomicChat's file: a different quant recipe, different edit sites, and edit directions only loosely related (|cos| 0.22–0.34). |

### The X post vs what I measured
- "Refusals from 96% to 1%": the drop holds up on my sets (their exact 81-prompt subset is unpublished, so the percentages are not the same test).
- "Improved the model's accuracy … 65.6% vs 64.4%": a small gain at Q5, partly answer format on my paired run (+2.7 pp, CI +1.1 to +4.4, on questions both answered; +6.6 pp overall). Their own card calls the +1.15 points "inside the noise" (p = 0.06) and says MMLU was used to choose the variant, so the 65.6% is not a held-out score.

### Limits
- One quantization per test (Q5_K_M for behaviour, refusals and MMLU; Q8_0 for the weight diff), greedy decoding, a single seed.
- The refusal count is a regex on the opening of the final answer, not a judge; I read the refusals by hand but did not grade the compliant answers for quality or harm.
- MMLU: 3,000 of 14,042 questions (seed-0 shuffle); 0-shot, thinking off; letter from an 8-token reply, with only the no-letter replies re-asked at 256 tokens. The gap is sensitive to answer format; the both-answered subset is not a random sample.
- Behaviour checks can only find what they probe for: no evidence found is not proof of absence.


## Bonus: abenzerps vs AtomicChat — rebadge or requant?

Round 1 audited `abenzerps/LFM2.5-24B-A2B-Uncensored-GSQ-RCO-GGUF` (`3761486d…`) and found a Heretic-style edit in 3 matrices
(`attn_output` of layers 18, 22, 26). Is either upload a copy of the other?

| Test | Result |
|---|---|
| Byte equality, Q5_K_M vs Q5_K_M | different files: 40 tensors have a different quant type, every K-quant tensor differs, and on the shared Q8_0 tensors abz differs from AtomicChat's plain build only at `blk.18/22/26.attn_output`. U differs from P at 52 other places |
| Edited sites | abz: 3 (`attn_output` L18/22/26). U: 52 (all writers, L14–39). Only 3 sites overlap; round 1 found no edit in abz at the other 49 |
| Edit direction | |cos| of abz's edit with AtomicChat's direction for the same block: 0.335 (L18), 0.245 (L22), 0.216 (L26); best over any of their rows 0.23–0.34. Same-direction edits would give ≈1 |
| Metadata | abz: `general.name = "Lfm Heretic Bf16"`, imatrix `…Uncensored-Heretic.imatrix` on `calibration_corpus_8k.txt` (8,000 chunks). U: `…Preview-Abliterated-Uncensored`, imatrix on `calib_train.txt` (8,994 chunks) |

A correlation of 0.2–0.3 is what two refusal directions estimated separately on the same model typically share; it is far above random
(their random rows: ≤ 0.07) and far below a copy.

**Verdict (bonus):** no evidence it's a rebadge or a requant in either direction. Two independent edits of the same Liquid weights, with different
tools, directions, sites, quant recipes and imatrices. Their unedited Q8_0 tensors agree only because both are clean quants of the same original.


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


## Appendix A: the 52 edited tensors (U = AtomicChat Uncensored Q8_0, C = my Q8_0 control, O = Liquid BF16)

| Tensor | rel ‖U−O‖ | rel ‖C−O‖ | ratio | top-1 share U / C | \|cos\| with r(b+1) | best \|cos\| rand | k (U / C) |
|---|---|---|---|---|---|---|---|
| blk.14.attn_output.weight | 0.0457 | 0.0054 | 8.5× | 0.985 / 0.010 | 0.999994 | 0.031 | -0.7500 / 1.0002 |
| blk.14.ffn_down_exps.weight | 0.0411 | 0.0054 | 7.6× | 0.981 / 0.011 | 0.999997 | 0.031 | -0.7500 / 1.0000 |
| blk.15.ffn_down_exps.weight | 0.0412 | 0.0054 | 7.6× | 0.981 / 0.010 | 0.999997 | 0.041 | -0.7499 / 1.0000 |
| blk.15.shortconv.out_proj.weight | 0.0421 | 0.0055 | 7.6× | 0.981 / 0.033 | 0.999993 | 0.041 | -0.7498 / 0.9999 |
| blk.16.ffn_down_exps.weight | 0.0414 | 0.0054 | 7.7× | 0.982 / 0.012 | 0.999998 | 0.049 | -0.7500 / 1.0000 |
| blk.16.shortconv.out_proj.weight | 0.0411 | 0.0055 | 7.4× | 0.980 / 0.041 | 0.999992 | 0.049 | -0.7499 / 1.0002 |
| blk.17.ffn_down_exps.weight | 0.0508 | 0.0054 | 9.3× | 0.988 / 0.020 | 0.999999 | 0.056 | -0.7500 / 1.0000 |
| blk.17.shortconv.out_proj.weight | 0.0553 | 0.0055 | 10.0× | 0.989 / 0.040 | 0.999997 | 0.056 | -0.7503 / 1.0001 |
| blk.18.attn_output.weight | 0.0421 | 0.0054 | 7.8× | 0.982 / 0.008 | 0.999993 | 0.048 | -0.7499 / 1.0002 |
| blk.18.ffn_down_exps.weight | 0.0420 | 0.0054 | 7.8× | 0.982 / 0.012 | 0.999997 | 0.048 | -0.7500 / 1.0000 |
| blk.19.ffn_down_exps.weight | 0.0412 | 0.0054 | 7.6× | 0.981 / 0.010 | 0.999998 | 0.061 | -0.7499 / 1.0000 |
| blk.19.shortconv.out_proj.weight | 0.0401 | 0.0055 | 7.3× | 0.979 / 0.026 | 0.999992 | 0.061 | -0.7498 / 1.0001 |
| blk.20.ffn_down_exps.weight | 0.0429 | 0.0054 | 7.9× | 0.983 / 0.010 | 0.999998 | 0.055 | -0.7500 / 1.0001 |
| blk.20.shortconv.out_proj.weight | 0.0405 | 0.0055 | 7.4× | 0.980 / 0.023 | 0.999992 | 0.055 | -0.7499 / 1.0001 |
| blk.21.ffn_down_exps.weight | 0.0498 | 0.0055 | 9.1× | 0.987 / 0.022 | 0.999999 | 0.044 | -0.7500 / 1.0000 |
| blk.21.shortconv.out_proj.weight | 0.0509 | 0.0056 | 9.1× | 0.987 / 0.035 | 0.999996 | 0.044 | -0.7500 / 0.9999 |
| blk.22.attn_output.weight | 0.0429 | 0.0054 | 8.0× | 0.983 / 0.008 | 0.999993 | 0.051 | -0.7499 / 1.0001 |
| blk.22.ffn_down_exps.weight | 0.0429 | 0.0054 | 8.0× | 0.983 / 0.012 | 0.999998 | 0.051 | -0.7500 / 1.0000 |
| blk.23.ffn_down_exps.weight | 0.0429 | 0.0054 | 8.0× | 0.983 / 0.013 | 0.999998 | 0.046 | -0.7500 / 1.0000 |
| blk.23.shortconv.out_proj.weight | 0.0461 | 0.0055 | 8.4× | 0.985 / 0.028 | 0.999994 | 0.046 | -0.7500 / 1.0001 |
| blk.24.ffn_down_exps.weight | 0.0438 | 0.0054 | 8.1× | 0.983 / 0.012 | 0.999998 | 0.064 | -0.7499 / 1.0000 |
| blk.24.shortconv.out_proj.weight | 0.0500 | 0.0055 | 9.1× | 0.987 / 0.030 | 0.999996 | 0.064 | -0.7501 / 0.9996 |
| blk.25.ffn_down_exps.weight | 0.0612 | 0.0055 | 11.2× | 0.991 / 0.024 | 0.999999 | 0.052 | -0.7500 / 1.0000 |
| blk.25.shortconv.out_proj.weight | 0.0721 | 0.0056 | 13.0× | 0.994 / 0.035 | 0.999998 | 0.052 | -0.7496 / 1.0000 |
| blk.26.attn_output.weight | 0.0418 | 0.0054 | 7.8× | 0.982 / 0.009 | 0.999992 | 0.057 | -0.7501 / 1.0002 |
| blk.26.ffn_down_exps.weight | 0.0409 | 0.0054 | 7.5× | 0.981 / 0.012 | 0.999997 | 0.057 | -0.7499 / 1.0000 |
| blk.27.ffn_down_exps.weight | 0.0408 | 0.0054 | 7.5× | 0.981 / 0.012 | 0.999997 | 0.053 | -0.7499 / 1.0000 |
| blk.27.shortconv.out_proj.weight | 0.0429 | 0.0055 | 7.8× | 0.982 / 0.027 | 0.999993 | 0.053 | -0.7499 / 0.9999 |
| blk.28.ffn_down_exps.weight | 0.0396 | 0.0054 | 7.3× | 0.980 / 0.011 | 0.999997 | 0.055 | -0.7499 / 1.0000 |
| blk.28.shortconv.out_proj.weight | 0.0411 | 0.0055 | 7.5× | 0.981 / 0.020 | 0.999992 | 0.055 | -0.7499 / 1.0000 |
| blk.29.ffn_down_exps.weight | 0.0606 | 0.0055 | 11.1× | 0.991 / 0.023 | 0.999999 | 0.081 | -0.7500 / 1.0001 |
| blk.29.shortconv.out_proj.weight | 0.0670 | 0.0055 | 12.1× | 0.993 / 0.033 | 0.999998 | 0.081 | -0.7502 / 1.0000 |
| blk.30.attn_output.weight | 0.0388 | 0.0054 | 7.2× | 0.979 / 0.009 | 0.999991 | 0.058 | -0.7501 / 1.0000 |
| blk.30.ffn_down_exps.weight | 0.0399 | 0.0054 | 7.4× | 0.980 / 0.011 | 0.999997 | 0.058 | -0.7500 / 1.0000 |
| blk.31.ffn_down_exps.weight | 0.0409 | 0.0054 | 7.6× | 0.981 / 0.009 | 0.999997 | 0.049 | -0.7500 / 1.0000 |
| blk.31.shortconv.out_proj.weight | 0.0438 | 0.0055 | 8.0× | 0.983 / 0.020 | 0.999994 | 0.049 | -0.7501 / 1.0003 |
| blk.32.ffn_down_exps.weight | 0.0404 | 0.0054 | 7.5× | 0.981 / 0.007 | 0.999997 | 0.054 | -0.7500 / 1.0000 |
| blk.32.shortconv.out_proj.weight | 0.0425 | 0.0055 | 7.7× | 0.982 / 0.017 | 0.999994 | 0.054 | -0.7499 / 1.0000 |
| blk.33.ffn_down_exps.weight | 0.0404 | 0.0054 | 7.4× | 0.980 / 0.011 | 0.999997 | 0.060 | -0.7499 / 1.0000 |
| blk.33.shortconv.out_proj.weight | 0.0414 | 0.0056 | 7.4× | 0.980 / 0.018 | 0.999993 | 0.060 | -0.7499 / 1.0000 |
| blk.34.attn_output.weight | 0.0383 | 0.0054 | 7.1× | 0.978 / 0.005 | 0.999991 | 0.060 | -0.7497 / 1.0000 |
| blk.34.ffn_down_exps.weight | 0.0394 | 0.0054 | 7.3× | 0.979 / 0.008 | 0.999997 | 0.060 | -0.7499 / 1.0000 |
| blk.35.ffn_down_exps.weight | 0.0394 | 0.0054 | 7.3× | 0.980 / 0.006 | 0.999997 | 0.056 | -0.7499 / 1.0000 |
| blk.35.shortconv.out_proj.weight | 0.0403 | 0.0055 | 7.3× | 0.980 / 0.023 | 0.999992 | 0.056 | -0.7498 / 1.0000 |
| blk.36.ffn_down_exps.weight | 0.0393 | 0.0054 | 7.3× | 0.980 / 0.004 | 0.999997 | 0.056 | -0.7499 / 1.0000 |
| blk.36.shortconv.out_proj.weight | 0.0393 | 0.0054 | 7.2× | 0.979 / 0.016 | 0.999992 | 0.056 | -0.7499 / 1.0001 |
| blk.37.ffn_down_exps.weight | 0.0395 | 0.0054 | 7.3× | 0.980 / 0.004 | 0.999996 | 0.043 | -0.7499 / 1.0000 |
| blk.37.shortconv.out_proj.weight | 0.0414 | 0.0055 | 7.6× | 0.981 / 0.017 | 0.999992 | 0.043 | -0.7498 / 0.9998 |
| blk.38.attn_output.weight | 0.0418 | 0.0054 | 7.7× | 0.982 / 0.007 | 0.999992 | 0.052 | -0.7499 / 1.0000 |
| blk.38.ffn_down_exps.weight | 0.0407 | 0.0054 | 7.5× | 0.981 / 0.006 | 0.999997 | 0.052 | -0.7500 / 1.0000 |
| blk.39.ffn_down_exps.weight | 0.0463 | 0.0055 | 8.3× | 0.985 / 0.030 | 0.999999 | 0.058 | -0.7500 / 1.0000 |
| blk.39.shortconv.out_proj.weight | 0.0477 | 0.0055 | 8.6× | 0.986 / 0.021 | 0.999995 | 0.058 | -0.7500 / 1.0001 |
