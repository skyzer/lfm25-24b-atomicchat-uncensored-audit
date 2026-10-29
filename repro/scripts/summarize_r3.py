# Round 3 summaries: weight diff (52 sites), Q5 four-way bytes, refusals (Wilson CI), MMLU (bootstrap CI + McNemar).
# Usage: summarize_r3.py RESULTS_DIR OUT_DIR
import json, sys, os, glob, math, re, random, collections
R, O = sys.argv[1], sys.argv[2]; os.makedirs(O, exist_ok=True)
def jl(p): return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
def wilson(k, n, z=1.96):
    if n == 0: return [None, None]
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return [round(max(0, c-h), 4), round(min(1, c+h), 4)]
def binom_two_sided(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c); s = sum(math.comb(n, i) for i in range(k+1)) / 2**n
    return min(1.0, 2*s)
out = {}
# ---- weight diff
W = jl(f"{R}/wdiff_unc_q8_0.jsonl") + jl(f"{R}/wdiff_unc_q8_1.jsonl")
if W:
    ed = [w for w in W if not w["bytes_eq_U_C"]]; un = [w for w in W if w["bytes_eq_U_C"]]
    def site(w):
        return dict(name=w["name"], block=w["block"], rel_U_O=w["rel_U_O"], rel_C_O=w["rel_C_O"], ratio=w["rel_U_O"]/w["rel_C_O"] if w["rel_C_O"] else None,
                    top1_U=w.get("top1_U"), top1_C=w.get("top1_C"), cos_row_b1_enru=w.get("cos_row_b1_enru"), cos_best_rand=w.get("cos_best_rand"),
                    fit_k_U=w.get("fit_k_U"), fit_k_C=w.get("fit_k_C"), flip_frac_U=w.get("flip_frac_U"), u_argmax_C=w.get("u_argmax_C"))
    S = sorted([site(w) for w in ed], key=lambda s: (s["block"], s["name"]))
    def rng(k, L): v = [s[k] for s in L if s[k] is not None]; return [min(v), max(v)] if v else None
    mix = [s for s in S if "ffn_down_exps" not in s["name"]]; exp = [s for s in S if "ffn_down_exps" in s["name"]]
    out["weightdiff"] = dict(n_tensors=len(W), n_edited=len(ed), n_bytes_identical=len(un),
        edited_blocks=sorted({s["block"] for s in S}), edited_names_by_kind=collections.Counter(re.sub(r"blk\.\d+\.", "", s["name"]) for s in S),
        unedited_writer_blocks=sorted({w["block"] for w in un if w.get("writer")} - set()),
        mixer=dict(n=len(mix), **{k: rng(k, mix) for k in ["ratio", "top1_U", "top1_C", "cos_row_b1_enru", "cos_best_rand", "fit_k_U", "fit_k_C", "flip_frac_U"]}),
        experts=dict(n=len(exp), **{k: rng(k, exp) for k in ["ratio", "top1_U", "top1_C", "cos_row_b1_enru", "cos_best_rand", "fit_k_U", "fit_k_C", "flip_frac_U"]}),
        sites=S)
# ---- Q5 4-way
Q = jl(f"{R}/q5_4way.jsonl")
if Q:
    d = {}
    for a, b in [("liq","plain"),("liq","unc"),("liq","abz"),("plain","unc"),("plain","abz"),("unc","abz")]:
        c = collections.Counter()
        for r in Q:
            st = r["type_"+a] if r["type_"+a] == r["type_"+b] else "type_differs"
            c[f"{st}:{'eq' if r[f'eq_{a}_{b}'] else 'ne'}"] += 1
        d[f"{a}_vs_{b}"] = dict(identical=sum(r[f"eq_{a}_{b}"] for r in Q), differ=sum(not r[f"eq_{a}_{b}"] for r in Q), by_type=dict(c),
            differing_same_type_Q8_0=[r["name"] for r in Q if not r[f"eq_{a}_{b}"] and r["type_"+a] == r["type_"+b] == "Q8_0"])
    d["type_recipe_counts"] = {"|".join(k): v for k, v in collections.Counter((r["type_liq"], r["type_plain"], r["type_unc"], r["type_abz"]) for r in Q).items()}
    out["q5_4way"] = d
# ---- refusals
ref = {}
for p in sorted(glob.glob(f"{R}/ref3_*.jsonl")):
    rows = jl(p); key = os.path.basename(p)[5:-6]
    cats = collections.defaultdict(list)
    for r in rows: cats[r["cat"]].append(r)
    e = {}
    for c, L in cats.items():
        n = len(L); k = sum(1 for r in L if r["refused"]); k120 = sum(1 for r in L if r["refused_open120"]); none = sum(1 for r in L if r["refused"] is None)
        e[c] = dict(n=n, refused=k, rate=round(k/n, 4), ci95=wilson(k, n), refused_open120=k120, rate_open120=round(k120/n, 4), no_final_answer=none,
                    capped_len=sum(1 for r in L if r["finish"] == "length"))
    ref[key] = e
out["refusals"] = ref
# ---- MMLU
mm = {}
for p in sorted(glob.glob(f"{R}/mmlu_*.jsonl")):
    rows = {r["i"]: r for r in jl(p)}; mm[os.path.basename(p)[5:-6]] = rows
M = {}
for k, rows in mm.items():
    n = len(rows); c = sum(r["correct"] for r in rows.values())
    M[k] = dict(n=n, correct=c, acc=round(c/n, 5) if n else None, ci95_wilson=wilson(c, n), no_letter=sum(r["pred"] is None for r in rows.values()))
names = list(mm)
for i in range(len(names)):
    for j in range(i+1, len(names)):
        a, b = names[i], names[j]; ids = sorted(set(mm[a]) & set(mm[b]))
        if not ids: continue
        xa = [mm[a][t]["correct"] for t in ids]; xb = [mm[b][t]["correct"] for t in ids]
        gain = sum(1 for u, v in zip(xa, xb) if v and not u); lost = sum(1 for u, v in zip(xa, xb) if u and not v)
        dlt = [(v - u) for u, v in zip(xa, xb)]; random.seed(0); n = len(ids); bs = []
        for _ in range(2000):
            s = 0
            for _ in range(n): s += dlt[random.randrange(n)]
            bs.append(s / n)
        bs.sort()
        M[f"{b}_minus_{a}"] = dict(n=n, delta_pp=round(100*sum(dlt)/n, 3), ci95_pp_paired_bootstrap=[round(100*bs[49], 3), round(100*bs[1949], 3)],
                                   b_gained=gain, b_lost=lost, mcnemar_exact_p=round(binom_two_sided(gain, lost), 5))
out["mmlu"] = M
json.dump(out, open(f"{O}/r3_summary.json", "w"), indent=1, default=str)
print(json.dumps({k: (v if k != "weightdiff" else {kk: vv for kk, vv in v.items() if kk != "sites"}) for k, v in out.items()}, indent=1, default=str)[:6000])
