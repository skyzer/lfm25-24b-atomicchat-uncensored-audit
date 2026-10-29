# Per-tensor raw-byte identity and dequantised rel-diff between several GGUFs, against a reference O (BF16).
# Usage: multi_byteeq.py O.gguf out.jsonl LABEL=file.gguf LABEL=file.gguf ...   (pairwise for all labels)
import sys, json, itertools, numpy as np, gguf
from gguf.quants import dequantize
fO, out = sys.argv[1:3]; F = dict(a.split('=', 1) for a in sys.argv[3:])
O = {t.name: t for t in gguf.GGUFReader(fO).tensors}; R = {k: {t.name: t for t in gguf.GGUFReader(f).tensors} for k, f in F.items()}
def raw(t): return np.asarray(t.data).view(np.uint8)
def deq(t): return dequantize(t.data, t.tensor_type).astype(np.float32).reshape([int(x) for x in t.shape[::-1]])
with open(out, 'w') as f:
    for n in O:
        o = deq(O[n]); no = float(np.linalg.norm(o)) or 1e-30; X = {k: deq(R[k][n]) for k in R}
        r = dict(name=n, **{f'type_{k}': R[k][n].tensor_type.name for k in R}, **{f'rel_{k}_O': float(np.linalg.norm(X[k] - o) / no) for k in R})
        for a, b in itertools.combinations(R, 2):
            ta, tb = R[a][n], R[b][n]
            r[f'eq_{a}_{b}'] = bool(ta.tensor_type == tb.tensor_type and np.array_equal(raw(ta), raw(tb)))
            r[f'rel_{a}_{b}'] = float(np.linalg.norm(X[a] - X[b]) / no)
        f.write(json.dumps(r) + '\n'); f.flush()
