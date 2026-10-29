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
