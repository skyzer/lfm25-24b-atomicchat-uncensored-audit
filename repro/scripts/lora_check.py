# Inspect AtomicChat's published rank-1 LoRA and compare it with (a) their directions.npz, (b) the baked edit (U - O),
# (c) the card's formula  delta = -a r r^T W.
# Usage: lora_check.py lora.gguf O.gguf directions.npz U.gguf|- out.jsonl [scale=1.75]
import sys, re, json, numpy as np, gguf
from gguf.quants import dequantize
fL, fO, fD, fU, out = sys.argv[1:6]; SC = float(sys.argv[6]) if len(sys.argv) > 6 else 1.75
rl = gguf.GGUFReader(fL)
meta = {}
for k, fld in rl.fields.items():
    if k.startswith('adapter') or k.startswith('general'):
        try: meta[k] = fld.contents()
        except Exception: pass
alpha = float(meta.get('adapter.lora.alpha', 0) or 0)
L = {t.name: t for t in rl.tensors}
O = {t.name: t for t in gguf.GGUFReader(fO).tensors}; U = {t.name: t for t in gguf.GGUFReader(fU).tensors} if fU != '-' else None
Dz = np.load(fD); E = Dz['enru'].astype(np.float64); E /= np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-30)
def deq(t): return dequantize(t.data, t.tensor_type).astype(np.float64).reshape([int(x) for x in t.shape[::-1]])
sites = sorted({n[:-len('.lora_a')] for n in L if n.endswith('.lora_a')}, key=lambda s: (int(re.search(r'blk\.(\d+)', s).group(1)), s))
res = dict(meta={k: (v if isinstance(v, (int, float, str)) else str(v)) for k, v in meta.items()}, n_tensors=len(L), n_sites=len(sites), sites=[])
for s in sites:
    A = deq(L[s + '.lora_a']); B = deq(L[s + '.lora_b']); b = int(re.search(r'blk\.(\d+)', s).group(1))
    W = deq(O[s]); rank = A.shape[-2]
    # llama.cpp: delta = scale * (alpha/rank) * B @ A ; B: (..., out, r), A: (..., r, in)
    if A.ndim == 2 and W.ndim == 3: A = np.broadcast_to(A, (W.shape[0],) + A.shape)
    if B.ndim == 2 and W.ndim == 3: B = np.broadcast_to(B, (W.shape[0],) + B.shape)
    f = SC * (alpha / rank if alpha else 1.0)
    dl = f * (B @ A)
    bv = B.reshape(-1, B.shape[-2], B.shape[-1])[..., 0]          # (n, out) output-side vectors
    bn = bv / np.maximum(np.linalg.norm(bv, axis=1, keepdims=True), 1e-30)
    b_consistency = float(np.abs(bn @ bn[0]).min())                 # all experts share one output direction?
    cs = np.abs(E @ bn[0]); r = E[int(cs.argmax())]
    pred = -SC * np.einsum('o,...i->...oi', r, np.einsum('o,...oi->...i', r, W))
    row = dict(site=s, block=b, lora_a_shape=[int(x) for x in L[s + '.lora_a'].shape], lora_b_shape=[int(x) for x in L[s + '.lora_b'].shape], rank=int(rank),
               b_dir_consistency_min=b_consistency, best_row=int(cs.argmax()), cos_best=float(cs.max()), cos_row_b=float(cs[b]), cos_row_b1=float(cs[min(b + 1, 40)]),
               lora_vs_formula_cos=float((dl * pred).sum() / max(np.linalg.norm(dl) * np.linalg.norm(pred), 1e-300)),
               lora_over_formula_norm=float(np.linalg.norm(dl) / max(np.linalg.norm(pred), 1e-300)))
    if U is not None:
        d = deq(U[s]) - W
        row['lora_vs_baked_cos'] = float((dl * d).sum() / max(np.linalg.norm(dl) * np.linalg.norm(d), 1e-300))
        row['lora_over_baked_norm'] = float(np.linalg.norm(dl) / max(np.linalg.norm(d), 1e-300))
        row['formula_vs_baked_cos'] = float((pred * d).sum() / max(np.linalg.norm(pred) * np.linalg.norm(d), 1e-300))
    res['sites'].append(row); print(json.dumps(row), flush=True)
json.dump(res, open(out, 'w'), indent=1)
