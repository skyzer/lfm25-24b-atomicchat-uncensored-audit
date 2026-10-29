# Round 3 charts. Usage: plots_r3.py r3_summary.json OUT_DIR
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from charts_common import *
import numpy as np
S = json.load(open(sys.argv[1])); O = sys.argv[2]; os.makedirs(O, exist_ok=True)
W = S.get("weightdiff")
if W:
    sites = W["sites"]; blocks = list(range(0, 40))
    mix = {s["block"]: s for s in sites if "ffn_down_exps" not in s["name"]}; exp = {s["block"]: s for s in sites if "ffn_down_exps" in s["name"]}
    # 1 weight diff by block
    f = fig(); title(f, "52 tensors changed, all in blocks 14-39", "Change vs Liquid BF16 ÷ change from my own clean Q8_0 requant (1.0 = quant noise)")
    a = f.add_axes([0.08, 0.17, 0.88, 0.62]); ax_style(a)
    xb = np.arange(40)
    r_m = [mix[b]["ratio"] if b in mix else 1.0 for b in blocks]; r_e = [exp[b]["ratio"] if b in exp else 1.0 for b in blocks]
    a.bar(xb - 0.2, r_m, 0.4, color=[ABZ if b in mix else NOISE for b in blocks], label="mixer writer (attn_output / shortconv.out_proj)")
    a.bar(xb + 0.2, r_e, 0.4, color=[WARN if b in exp else NOISE for b in blocks], label="ffn_down_exps (all 64 experts)")
    a.axhline(1, color=CLEAN, lw=2, ls="--"); a.text(0.3, 1.4, "byte-identical to my requant (ratio 1)", color=CLEAN, fontsize=14)
    a.set_xlabel("block"); a.set_ylabel("ratio over requant noise"); a.set_xticks(range(0, 40, 2))
    from matplotlib.patches import Patch
    a.legend(handles=[Patch(color=ABZ, label="mixer writer (attn_output / shortconv.out_proj)"), Patch(color=WARN, label="ffn_down_exps (all 64 experts)"), Patch(color=NOISE, label="untouched (byte-identical)")], loc="upper left", fontsize=14, frameon=False)
    foot(f, "Source: expected_outputs/wdiff_unc_q8.jsonl, byteeq_unc_q8_vs_ctrl_q8.txt\nUnc AD-Q8_0 @b0f357bb vs my Q8_0 of Liquid BF16 (llama.cpp 19cce691): 376/428 tensors byte-identical")
    save(f, f"{O}/weightdiff_by_layer.png")
    # 2 direction + k
    f = fig(); title(f, "One direction per layer, removed at scale 1.75", "W' = W \u2212 1.75\u00b7r r\u1d40W: along r the output flips to \u22120.75\u00d7, the rest is untouched")
    a = f.add_axes([0.08, 0.17, 0.40, 0.60]); ax_style(a)
    eb = sorted(exp); a.plot(eb, [exp[b]["top1_U"] for b in eb], "o-", color=WARN, label="edited: top-1 share"); a.plot(eb, [exp[b]["top1_C"] for b in eb], "o-", color=NOISE, label="requant noise: top-1")
    a.plot(eb, [exp[b]["cos_row_b1_enru"] for b in eb], "s--", color=ABZ, label="|cos| with published r")
    a.plot(eb, [exp[b]["cos_best_rand"] for b in eb], "^:", color=MUT, label="best random-dir |cos|")
    a.set_ylim(0, 1.08); a.set_xlabel("block"); a.set_title("diff structure (experts)", fontsize=18); a.legend(fontsize=11, frameon=False, loc="center right")
    a2 = f.add_axes([0.57, 0.17, 0.39, 0.60]); ax_style(a2)
    mb = sorted(mix)
    a2.plot(mb, [mix[b]["fit_k_U"] for b in mb], "o", color=ABZ, ms=9, label="AtomicChat (mixer)"); a2.plot(eb, [exp[b]["fit_k_U"] for b in eb], "x", color=WARN, ms=9, label="AtomicChat (experts)")
    a2.plot(mb, [mix[b]["fit_k_C"] for b in mb], "o", color=CLEAN, ms=7, label="my requant")
    a2.axhline(-0.75, color=MUT, ls="--"); a2.axhline(1, color=MUT, ls="--"); a2.set_ylim(-1.1, 1.3); a2.set_xlabel("block"); a2.set_title("fitted k along r  (r\u1d40W' = k\u00b7r\u1d40W)", fontsize=18)
    a2.legend(fontsize=12, frameon=False, loc="center right")
    foot(f, "Source: expected_outputs/wdiff_unc_q8.jsonl. r = row b+1 of AtomicChat's published directions.npz (sha256 9e995555...),\nthe file named in the GGUF atomic.abliterate.* keys. Mixer writers show the same values.")
    save(f, f"{O}/edit_direction.png")
Q = S.get("q5_4way")
if Q:
    lab = ["Liquid Q5_K_M", "Atomic plain AD-Q5", "Atomic Unc AD-Q5", "abenzerps Q5"]; keys = ["liq", "plain", "unc", "abz"]
    M = np.zeros((4, 4))
    for i in range(4):
        for j in range(4):
            if i == j: M[i, j] = 428
            else:
                k = f"{keys[min(i,j)]}_vs_{keys[max(i,j)]}"; M[i, j] = Q[k]["identical"]
    f = fig(); title(f, "Bonus: abenzerps is not AtomicChat's file", "Byte-identical tensors out of 428 (the 207 F32 norms match everywhere)")
    a = f.add_axes([0.17, 0.12, 0.40, 0.68]); im = a.imshow(M, cmap="magma", vmin=200, vmax=428)
    for i in range(4):
        for j in range(4): a.text(j, i, int(M[i, j]), ha="center", va="center", fontsize=20, color="white" if M[i, j] < 380 else "black")
    a.set_xticks(range(4)); a.set_yticks(range(4)); a.set_xticklabels([l.replace(" ", "\n", 1) for l in lab], fontsize=12); a.set_yticklabels(lab, fontsize=13)
    pa = Q["plain_vs_abz"]["by_type"]
    note = ("plain vs Unc: differ on exactly the 52 edited tensors\n(same imatrix + recipe everywhere else)\n\n"
            f"plain vs abenzerps: Q8_0 equal {pa.get('Q8_0:eq',0)} (deterministic),\n  Q8_0 differ {pa.get('Q8_0:ne',0)} (its L18/22/26 edits),\n"
            f"  K-quants differ {pa.get('Q5_K:ne',0)+pa.get('Q6_K:ne',0)}/{pa.get('Q5_K:ne',0)+pa.get('Q6_K:ne',0)},\n  type recipe differs on {pa.get('type_differs:ne',0)}\n\n"
            "abz edit directions vs Atomic's: |cos| 0.22-0.34\n(random <= 0.07): related, not the same")
    f.text(0.61, 0.78, note, fontsize=12.5, color=FG, va="top", linespacing=1.35)
    foot(f, "Source: expected_outputs/q5_4way.jsonl, bonus_dircos.json")
    save(f, f"{O}/bonus_4way_bytes.png")
R = S.get("refusals")
if R:
    rows = []
    for key, lab in [("r1_nothink1024", "20 harmful, no-think"), ("r1_think8192", "20 harmful, think 8192"), ("jbb_nothink256", "JBB 100, no-think 256"), ("jbb_think3072", "JBB 100, think 3072"), ("xstest_nothink256", "XSTest safe 250 (over-refusal)")]:
        for m in ["liquid_q5", "plain_q5", "unc_q5"]:
            e = R.get(f"{m}_{key}")
            if not e: continue
            cat = {"r1": "harmful", "jbb": "jbb_harmful", "xst": "xstest_safe"}[key[:3] if key[:2] != "r1" else "r1"]
            if cat in e: rows.append((lab, m, e[cat]))
    if rows:
        f = fig(); title(f, "Refusals, same harness for every model", "Share refused (regex on the opening of the final answer), 95% Wilson CI")
        a = f.add_axes([0.30, 0.13, 0.66, 0.68]); ax_style(a); a.grid(axis="x", color=GRID); a.grid(axis="y", visible=False)
        col = {"liquid_q5": ORIG, "plain_q5": CLEAN, "unc_q5": ABZ}; ys = []; yl = []
        for i, (lab, m, e) in enumerate(rows):
            y = len(rows) - i; lo, hi = e["ci95"]
            a.barh(y, 100*e["rate"], color=col[m], height=0.7); a.errorbar(100*e["rate"], y, xerr=[[100*(e["rate"]-lo)], [100*(hi-e["rate"])]], color=FG, capsize=4)
            a.text(max(100*e["rate"], 100*hi)+1.5, y, f"{e['refused']}/{e['n']}", va="center", fontsize=12); ys.append(y); yl.append(f"{lab} \u2014 {m.split('_')[0]}")
        a.set_yticks(ys); a.set_yticklabels(yl, fontsize=11); a.set_xlim(0, 115); a.set_xlabel(""); f.subplots_adjust(bottom=0.2)
        foot(f, "Source: expected_outputs/ref3_*.jsonl, r3_summary.json. liquid = LiquidAI Q5_K_M; plain/unc = AtomicChat AD-Q5_K_M.\nGreedy decoding, llama.cpp 19cce691, no network.")
        save(f, f"{O}/refusals.png")
M = S.get("mmlu"); LN = S.get("mmlu_lenient")
if LN: M0, M = M, {k: v for k, v in LN.items() if k != "both_answered"}
if M:
    ms = [k for k in ["liquid_q5", "plain_q5", "unc_q5"] if k in M]
    f = fig(); title(f, f"MMLU: {min(M[k]['n'] for k in ms):,} of 14,042 Qs, same quant", "0-shot, thinking off, greedy, 95% CI. No-letter replies re-asked at 256 tokens." if LN else "0-shot, thinking off, greedy, 95% CI. Liquid publishes no MMLU score for this model.")
    a = f.add_axes([0.1, 0.15, 0.4, 0.64]); ax_style(a)
    col = {"liquid_q5": ORIG, "plain_q5": CLEAN, "unc_q5": ABZ}
    for i, k in enumerate(ms):
        e = M[k]; lo, hi = e["ci95_wilson"]
        a.bar(i, 100*e["acc"], color=col[k], width=0.6); a.errorbar(i, 100*e["acc"], yerr=[[100*(e["acc"]-lo)], [100*(hi-e["acc"])]], color=FG, capsize=6)
        a.text(i + 0.08, 100*hi + 0.3, f"{100*e['acc']:.2f}%", ha="left", fontsize=15)
    lo_all = min(100*M[k]["acc"] for k in ms)
    a.set_xticks(range(len(ms))); a.set_xticklabels([{"liquid_q5": "Liquid Q5_K_M", "plain_q5": "Atomic plain\nAD-Q5", "unc_q5": "Atomic Unc\nAD-Q5"}[k] for k in ms], fontsize=13)
    a.set_ylim(max(0, lo_all-8), max(100*M[k]["ci95_wilson"][1] for k in ms)+3); a.set_ylabel("accuracy %")
    txt = []
    for k, v in M.items():
        if "_minus_" in k: txt.append(f"{'All ' + format(v['n'], ',') + ' Qs' if LN else k.replace('_minus_', ' - ')}:\n  {v['delta_pp']:+.2f} pp  [{v['ci95_pp_paired_bootstrap'][0]:+.2f}, {v['ci95_pp_paired_bootstrap'][1]:+.2f}]\n  McNemar p = {v['mcnemar_exact_p']:.3g}  (+{v['b_gained']} / -{v['b_lost']})")
    if LN:
        BA = LN["both_answered"]; ST = M0["unc_q5_minus_liquid_q5"]
        txt.append(f"Only Qs both answered (n={BA['n']:,}):\n  {BA['delta_pp']:+.2f} pp  [{BA['ci95_pp_paired_bootstrap'][0]:+.2f}, {BA['ci95_pp_paired_bootstrap'][1]:+.2f}]")
        txt.append(f"Strict 8-token answers only:\n  {ST['delta_pp']:+.2f} pp (Liquid: no letter on {M0['liquid_q5']['no_letter']})")
    f.text(0.55, 0.82, "Unc minus Liquid, paired (95% bootstrap CI)\n\n" + ("\n\n".join(txt) or "Liquid Q5 run: [PENDING]\n(still running at freeze)") + "\n\nAtomicChat's own: 2,000-q subset,\n64.40 -> 65.55, p = 0.056", fontsize=12.5, color=FG, va="top", linespacing=1.3)
    foot(f, "Source: expected_outputs/mmlu_*.jsonl, mmlu_rescore_*.jsonl, r3_summary.json (mmlu_lenient); cais/mmlu 'all' test split.")
    save(f, f"{O}/mmlu.png")
print("plots ->", O, sorted(os.listdir(O)))
