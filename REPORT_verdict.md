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
