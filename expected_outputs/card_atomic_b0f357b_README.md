---
license: other
license_name: lfm1.0
license_link: LICENSE
base_model:
- LiquidAI/LFM2.5-24B-A2B
base_model_relation: finetune
quantized_by: AtomicChat
pipeline_tag: text-generation
library_name: gguf
language:
- en
- ar
- zh
- fr
- de
- ja
- ko
- es
- pt
- it
tags:
- atomic-chat
- liquid
- lfm2.5
- lfm2moe
- moe
- gguf
- imatrix
- llama.cpp
- lora
- abliteration
- refusal-direction
---

# How to Run LFM2.5-24B-A2B Without Refusals Locally
<p style="margin-top: 0; margin-bottom: 0;">
  <em>Liquid's refusal behaviour projected out of the original weights, in the second two thirds of the network only. Shipped two ways: six baked GGUF builds, and a 24 MB LoRA adapter for the LFM2.5-24B-A2B quants you already have. The <a href="https://huggingface.co/datasets/AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF-metrics">measurements</a> behind this card are public.</em>
</p>
<div style="display: flex; gap: 8px; align-items: center; margin-top: 10px; margin-bottom: 10px;">
  <a href="https://atomic.chat/?utm_source=huggingface&utm_medium=referral&utm_campaign=hf_lfm2_5_24b_a2b_abliterate&utm_content=btn_atomic"><img src="https://huggingface.co/AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF/resolve/main/btn_atomic.png" width="162" alt="Atomic Chat"></a>
  <a href="https://discord.gg/8wGSsvmg4V"><img src="https://huggingface.co/AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF/resolve/main/btn_discord.png" width="119" alt="Discord"></a>
  <a href="https://github.com/AtomicBot-ai/Atomic-Chat"><img src="https://huggingface.co/AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF/resolve/main/btn_github.png" width="115" alt="GitHub"></a>
  <a href="https://x.com/atomic_chat_hq"><img src="https://huggingface.co/AtomicChat/Qwen3.8-27B-GGUF/resolve/main/btn_x.png" width="108" alt="X"></a>
</div>
<ul style="margin: 0 0 12px 0;">
  <li>Built by the team behind <a href="https://atomic.chat/?utm_source=huggingface&utm_medium=referral&utm_campaign=hf_lfm2_5_24b_a2b_abliterate&utm_content=bullet_app">Atomic Chat</a>, the app that runs open-weight models locally and offline.</li>
  <li>On held-out prompts, refusals fall from 96.3% to 1.2% in English, and from 30 of 30 to none with thinking. MMLU stays where it was: 64.40% before, 65.55% after (inside the noise). No empty or looping replies.</li>
  <li>Only blocks 14-39 are edited. The same edit across all 40 blocks also removed the refusals, but cost 4 MMLU points; the first 14 blocks carry the damage, not the refusal.</li>
  <li>Already running our <a href="https://huggingface.co/AtomicChat/LFM2.5-24B-A2B-GGUF">LFM2.5-24B-A2B quants</a>? Add the adapter with <code>--lora-scaled</code> instead of downloading a new model.</li>
</ul>
<hr style="margin: 0 0 16px 0;">

## The builds

| Build | On disk | Mean KLD | Same top-1 | Refused: EN / XSTest |
|---|---|---|---|---|
| `AD-Q8_0` | 25.7 GB | 0.229 | 81.4% | 1.2% / 0% |
| `AD-Q6_K` | 20.9 GB | 0.239 | 81.0% | - |
| `AD-Q5_K_M` | 17.3 GB | 0.271 | 80.3% | - |
| **`AD-Q4_K_M`** | **15.4 GB** | **0.274** | **79.6%** | 1.2% / 0% |
| `AD-IQ4_XS` | 14.5 GB | 0.274 | 79.3% | - |
| `AD-IQ3_M` | 12.1 GB | 0.359 | 76.0% | - |

**`AD-Q4_K_M` is the one to take** on a 24 GB machine. With 32 GB, `AD-Q6_K` is
nearly as close to the original as `AD-Q8_0` at 5 GB less; `AD-IQ3_M` is the
smallest build here. Refusals were measured on `AD-Q8_0` and `AD-Q4_K_M`;
neither gave an empty or looping reply. A smaller `AD-IQ3_XXS` (11.1 GB) was
made too and is held back: it matched the original's token choice only 74.5% of
the time and refused 3.7% of English prompts.

KLD and top-1 are against the **original, unmodified** BF16 model, so they hold
the edit and the quantization together. Most of it is the edit: on BF16 weights
the edit alone is 0.204 (82.5% same top-1), and our plain `AD-Q8_0` of the
original is 0.063. The next section shows what that distance is made of.

The builds use the same layout and importance matrix as our
[original quants](https://huggingface.co/AtomicChat/LFM2.5-24B-A2B-GGUF),
so each is the same size as the original build with the same name.

## What changed, and what did not

Original against ablated, both BF16. The refusal sets are held-out prompts never
used to pick anything; MMLU, the same 2,000 questions throughout, was part of
the choice.

| | Original | Ablated |
|---|---|---|
| JBB harmful behaviours (EN, 81), refused | 96.3% | **1.2%** |
| XSTest safe prompts (250), refused | 12.8% | **0%** |
| With thinking (30 prompts, 3072 tokens), refused | 30 of 30 | **0 of 30** |
| Thinking left unclosed at 3072 tokens | 0 of 30 | 0 of 30 |
| Empty or looping replies (431) | 0 | 0 |
| MMLU, 2000 questions | 64.40% | 65.55% (+1.15, McNemar p = 0.06) |
| Tool calls (20) | 20/20 valid | 20/20 valid |
| Needle at 30k tokens (3 depths) | 2/3 | 3/3 |
| Mean KLD to the original, neutral / code | - | 0.204 / 0.179 |

The answers carry the same facts and the same structure; what moves is the
wording. The ablated model tends to open more directly and to say a little less
around the point. That shift in word choice is what the 0.20 of KLD measures,
token by token over general text. For scale, the same edit along random
directions costs 0.035 (neutral) to 0.066 (code), and this model moved by
0.02-0.05 between two ways of doing the same BF16 arithmetic on the preview's
first revision (see the
[original quants'](https://huggingface.co/AtomicChat/LFM2.5-24B-A2B-GGUF)
card). Read by hand, the answers stay on the question and come in the language
asked; none was empty or looping.

Refusal is counted by the opening of the reply, so it is indicative, not a
judge. Empty or degenerate replies count as damage.

## The adapter

`lora/LFM2.5-24B-A2B-Uncensored-LoRA.gguf`: rank 1, 24 MB,
52 sites. It applies to any GGUF of the original LFM2.5-24B-A2B weights
(revision `f772950c`), including our published quants:

```bash
llama-server -m LFM2.5-24B-A2B-AD-Q4_K_M.gguf -ngl 99 -c 32768 --jinja \
  --lora-scaled lora/LFM2.5-24B-A2B-Uncensored-LoRA.gguf:1.75
```

Or load it once and set the strength per request:

```bash
llama-server -m <model> -ngl 99 --jinja \
  --lora lora/LFM2.5-24B-A2B-Uncensored-LoRA.gguf --lora-init-without-apply
```

```bash
curl localhost:8080/v1/chat/completions -H 'Content-Type: application/json' -d '{
  "messages": [{"role": "user", "content": "..."}],
  "lora": [{"id": 0, "scale": 1.75}]
}'
```

**Use scale 1.75.** On validation prompts it left 1% of English refusals; 2.0
and 2.25 removed those too, with MMLU unchanged, but edit the model harder for
that last percent. On our published `AD-Q8_0` the adapter gives the same model
as the baked `AD-Q8_0` here: mean KLD 0.063 without it, 0.229 with it (the baked
build: 0.229); refused with it: 1.2% / 0% (EN / XSTest). The other
published quants were not measured with it.

## Get started

- **[Atomic Chat](https://atomic.chat/?utm_source=huggingface&utm_medium=referral&utm_campaign=hf_lfm2_5_24b_a2b_abliterate&utm_content=get_started):**
  the easiest path. Open the app, search `AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF`,
  pick a build, hit **Use this model**.
- **llama.cpp:**

```bash
hf download AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF \
  LFM2.5-24B-A2B-Uncensored-AD-Q4_K_M.gguf --local-dir .
```

```bash
llama-server -m LFM2.5-24B-A2B-Uncensored-AD-Q4_K_M.gguf -ngl 99 -c 32768 --jinja
```

Pass `--jinja` so the embedded chat template is used; without it llama.cpp falls
back to a generic one. Liquid's recommended sampling: temperature 0.1, top_k 50,
repetition penalty 1.05. Context goes up to 131,072 tokens. Needs a llama.cpp
build with `lfm2moe` and the LFM2.5 tokenizer, which upstream has.

## How it was made

1. **Directions.** Difference of means of the residual stream at the last prompt
   token, chat template applied with an empty thinking block: 544 harmful
   against 544 harmless prompts. The component along the harmless mean is
   removed. One direction per block: the matrices of block *b*
   are edited along the direction measured at the output of block *b*.
2. **Edit.** `W' = W - 1.75 r rᵀW` on the 52 matrices that write into the
   residual stream in blocks 14-39: the output of each block's mixer (short
   convolution or attention) and the down projections of all 64 experts. At
   1.75 the component along `r` is reversed and kept at three quarters of its
   size, not only removed. Blocks 0-13, the two dense blocks, the router and the
   embeddings (tied to the output) are untouched.
3. **Choice.** More than 60 variants screened on validation prompts, with edits
   of the same shape along random directions as the control. The search ran on
   the preview's first revision; the comparison that decided it was repeated on
   the current weights (validation prompts, refused EN, MMLU change):

   | Edited | Refused | MMLU |
   |---|---|---|
   | all 40 blocks, scale 1.75 | 0% | -4.05 |
   | blocks 0-13 only, scale 1.75 | 82% | -4.2 |
   | **blocks 14-39, scale 1.75** (this release) | **1%** | **+1.2** |
   | random directions in the same form, scale 1.75 (the control, test prompts) | unchanged | +0.25 |

   On the first revision the gap was wider: all 40 blocks cost 11.6 MMLU points.
   Editing the mixer outputs alone, as Heretic-style tools would, left 83% of
   English refusals in place there and made the model refuse harmless prompts.
   On this model the refusal lives in the experts too.
4. **Bake.** The same edit applied to the BF16 weights in f32 and rounded once;
   every one of the 52 matrices checked against the intended edit, within
   1.2e-4 after rounding. Then quantized with the importance matrix and layout of our
   [original quants](https://huggingface.co/AtomicChat/LFM2.5-24B-A2B-GGUF).

## Measurement

The reference is the original BF16 model's logits over our held-out neutral set:
93 chunks of 4,096 tokens in 30 languages, BF16 PPL 15.67. The refusal numbers
come from JailbreakBench harmful behaviours (EN) and
XSTest safe prompts, none of them used to estimate the directions or to choose
the variant; MMLU (2,000 questions) was part of the choice. One machine type for everything: 1× H100 PCIe, llama.cpp
`980aef8c`, weights of revision `f772950c`. Logs, the adapter, the research rounds and the final comparison are in the
[metrics repository](https://huggingface.co/datasets/AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF-metrics).

## Limitations

- The refusal count reads the opening of each reply; a soft refusal phrased as
  an answer would be missed.
- The answers are phrased differently from the original's. On general text this
  model is further from the original than our quant of the unmodified model:
  81.4% same top-1 at Q8_0 against 90.1%.
- Thinking was tested on 30 English prompts with a 3072-token budget.
- Refusals are reported for English prompts only.
- Built from the preview's revision `f772950c` (12 October); the public release
  has the same weights, checked file by file.
- Not run yet on a Mac, in LM Studio or in Ollama.

## Responsible use

This model has its learned refusal behaviour removed, so it will answer
requests the original declines. Nothing about it makes the output safe, correct
or lawful, and any deployment needs its own access controls and policy
enforcement.

## License and credits

LFM Open License v1.0, see `LICENSE`. Base model **LFM2.5-24B-A2B** by
[Liquid AI](https://huggingface.co/LiquidAI). Directions, edit, quantization and
evaluation by **AtomicChat**. The method follows Arditi et al., *Refusal in
Language Models Is Mediated by a Single Direction* (2024).
