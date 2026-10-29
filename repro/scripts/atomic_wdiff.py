# Weight-diff analysis of AtomicChat's "Uncensored" LFM2.5-24B-A2B against Liquid's BF16 and an honest requant control.
# Files: O = Liquid BF16 (original), U = AtomicChat Uncensored AD-Q8_0, C = my control (Liquid BF16 -> Q8_0 with U's exact
#        per-tensor types; Q8_0/F16/F32 are deterministic, no imatrix), P = AtomicChat's own plain AD-Q8_0 (optional, "-").
# D = AtomicChat's published refusal directions (directions.npz, 41 x 2048 per set; row L = input of block L).
# Per tensor: byte equality U~C, P~C, U~P; rel ||X-O||/||O||; ratio ||U-O|| / ||C-O|| (1.0 = pure quantisation noise).
# For every tensor whose bytes differ from the control (and every residual writer):
#   output-space Gram of delta = U - O (experts stacked): top-1 energy share, s1/s2, top direction u, |u[557]|
#   cos(u, r_row) for all 41 rows of each direction set -> best row; cos with row b and b+1
#   fit of the card's edit  W' = W - a r r^T W : k = <r^T W', r^T W>/||r^T W||^2  (card: 1 - 1.75 = -0.75),
#   residual ||delta - (-(1-k)) r r^T O|| / ||delta||, the same for the control noise, sign flip fraction of r^T W columns,
#   per-expert consistency (k per expert, share of each expert's delta energy on the shared direction u).
# Usage: atomic_wdiff.py O.gguf U.gguf C.gguf P.gguf|- directions.npz out.jsonl [shard nshards]
import sys, os, re, json, gc, numpy as np, gguf
from gguf.quants import dequantize
fO, fU, fC, fP, fD, out = sys.argv[1:7]; shard, nsh = (int(sys.argv[7]), int(sys.argv[8])) if len(sys.argv) > 8 else (0, 1)
files = dict(O=fO, U=fU, C=fC) | ({} if fP == '-' else dict(P=fP))
R = {k: {t.name: t for t in gguf.GGUFReader(f).tensors} for k, f in files.items()}
Dz = np.load(fD); SETS = [s for s in ('enru', 'en', 'ru', 'rand') if s in Dz.files]
DIRS = {s: Dz[s].astype(np.float64) / np.maximum(np.linalg.norm(Dz[s].astype(np.float64), axis=1, keepdims=True), 1e-30) for s in SETS}
WR = re.compile(r'(attn_output|shortconv\.out_proj|ffn_down|ffn_down_exps|ffn_down_shexp)\.weight$'); CH = 557
def deq(t): return dequantize(t.data, t.tensor_type).astype(np.float32).reshape([int(x) for x in t.shape[::-1]])
def raw(t): return np.asarray(t.data).view(np.uint8)
def beq(a, b): return bool(a.tensor_type == b.tensor_type and np.array_equal(raw(a), raw(b)))
def gram(d):
    D = d.astype(np.float64).reshape(-1, *d.shape[-2:]); G = sum(x @ x.T for x in D)
    ev, V = np.linalg.eigh(G); ev = np.clip(ev[::-1], 0, None); V = V[:, ::-1]
    return ev, V[:, 0]
def blk(n):
    m = re.match(r'blk\.(\d+)\.', n); return int(m.group(1)) if m else None
def fit(r, W, Wp):
    # W, Wp: (..., out, in) -> project output side on r
    a = np.einsum('o,...oi->...i', r, W.astype(np.float64)); b = np.einsum('o,...oi->...i', r, Wp.astype(np.float64))
    k = float((a * b).sum() / max((a * a).sum(), 1e-300))
    d = Wp.astype(np.float64) - W.astype(np.float64); pred = -(1 - k) * np.einsum('o,...i->...oi', r, a)
    res = float(np.linalg.norm(d - pred) / max(np.linalg.norm(d), 1e-300))
    flip = float(np.mean(np.sign(a) != np.sign(b)))
    kexp = [float((a[e] * b[e]).sum() / max((a[e] * a[e]).sum(), 1e-300)) for e in range(a.shape[0])] if a.ndim == 2 else None
    return k, res, flip, kexp
names = list(R['O'])[shard::nsh]; dirs = {}
with open(out, 'w') as f:
    for n in names:
        t = {k: R[k][n] for k in R}; o = deq(t['O']); u_ = deq(t['U']); c = deq(t['C'])
        r = dict(name=n, shape=[int(x) for x in o.shape], block=blk(n), writer=bool(WR.search(n)), **{f'type_{k}': t[k].tensor_type.name for k in t},
                 bytes_eq_U_C=beq(t['U'], t['C']))
        if 'P' in t: r['bytes_eq_P_C'] = beq(t['P'], t['C']); r['bytes_eq_U_P'] = beq(t['U'], t['P'])
        no = float(np.linalg.norm(o)) or 1e-30
        r['rel_U_O'] = float(np.linalg.norm(u_ - o) / no); r['rel_C_O'] = float(np.linalg.norm(c - o) / no)
        r['rel_U_C'] = float(np.linalg.norm(u_ - c) / no); r['ratio_U_vs_C'] = r['rel_U_O'] / max(r['rel_C_O'], 1e-30)
        if 'P' in t: p = deq(t['P']); r['rel_P_O'] = float(np.linalg.norm(p - o) / no); del p
        if o.ndim >= 2 and (r['writer'] or not r['bytes_eq_U_C']) and n not in ('token_embd.weight', 'output.weight') and o.shape[-2] == 2048:
            for lab, x in (('U', u_), ('C', c)):
                d = x - o
                if not np.any(d): continue
                ev, u = gram(d); r[f'top1_{lab}'] = float(ev[0] / max(ev.sum(), 1e-300)); r[f's1s2_{lab}'] = float(np.sqrt(ev[0] / max(ev[1], 1e-300)))
                r[f'u_abs557_{lab}'] = float(abs(u[CH])); r[f'u_argmax_{lab}'] = int(np.argmax(np.abs(u)))
                r[f'ch557_share_{lab}'] = float((d[..., CH, :].astype(np.float64) ** 2).sum() / max((d.astype(np.float64) ** 2).sum(), 1e-300))
                if lab == 'U':
                    dirs[n] = u.astype(np.float32); b = r['block']
                    for s in SETS:
                        cs = np.abs(DIRS[s] @ u); r[f'cos_best_{s}'] = float(cs.max()); r[f'row_best_{s}'] = int(cs.argmax())
                        if b is not None: r[f'cos_row_b_{s}'] = float(cs[b]); r[f'cos_row_b1_{s}'] = float(cs[min(b + 1, 40)])
                    rr = r.get('row_best_enru'); rv = DIRS['enru'][rr] if rr is not None else u
                    k, res, flip, kexp = fit(rv, o, u_); r.update(fit_k_U=k, fit_res_U=res, flip_frac_U=flip)
                    kc, resc, flipc, _ = fit(rv, o, c); r.update(fit_k_C=kc, fit_res_C=resc, flip_frac_C=flipc)
                    k2, res2, _, _ = fit(u, o, u_); r.update(fit_k_U_own_u=k2, fit_res_U_own_u=res2)
                    if kexp is not None:
                        r['k_per_expert_min'] = min(kexp); r['k_per_expert_max'] = max(kexp)
                        D = d.astype(np.float64); pu = np.einsum('o,eoi->ei', u, D)
                        ce = (pu ** 2).sum(1) / np.maximum((D ** 2).sum(axis=(1, 2)), 1e-300)  # share of each expert's delta energy on u
                        r['expert_share_u_min'] = float(ce.min()); r['expert_share_u_median'] = float(np.median(ce)); del D, pu
                del d
        f.write(json.dumps(r) + '\n'); f.flush(); print(n, r['bytes_eq_U_C'], round(r['ratio_U_vs_C'], 3), flush=True)
        del o, u_, c; gc.collect()
np.savez(out.replace('.jsonl', '_dirs.npz'), **dirs)
