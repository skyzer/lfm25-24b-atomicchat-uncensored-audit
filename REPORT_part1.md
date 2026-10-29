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
