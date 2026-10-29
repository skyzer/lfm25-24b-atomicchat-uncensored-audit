# Assemble REPORT.md and thread facts from expected_outputs/r3_summary.json (+ beh_an_r3.json, strace_summary_r3.json).
# usage: python3 build_report.py   (run from kit/)
import json, os, sys
E = 'expected_outputs'
S = json.load(open(f'{E}/r3_summary.json'))
B = json.load(open(f'{E}/beh_an_r3.json'))
R, M = S.get('refusals', {}), S.get('mmlu', {})
def pct(x): return f"{100*x:.1f}%"
def cell(key, cat):
    e = R.get(key, {}).get(cat)
    if not e: return None
    lo, hi = e['ci95']
    return e, f"{e['refused']}/{e['n']} ({pct(e['rate'])}, CI {pct(lo)}–{pct(hi)})"
rows = [("28 round-1 prompts, harmful (20), no thinking, 1024 tok", "r1_nothink1024", "harmful"),
        ("28 round-1 prompts, borderline (8), no thinking, 1024 tok", "r1_nothink1024", "borderline"),
        ("28 round-1 prompts, harmful (20), thinking, 8192 tok", "r1_think8192", "harmful"),
        ("28 round-1 prompts, borderline (8), thinking, 8192 tok", "r1_think8192", "borderline"),
        ("JBB-Behaviors harmful (100), no thinking, 256 tok", "jbb_nothink256", "jbb_harmful"),
        ("JBB-Behaviors harmful (100), thinking, 3072 tok", "jbb_think3072", "jbb_harmful"),
        ("XSTest v2 safe (250), no thinking, 256 tok (over-refusal)", "xstest_nothink256", "xstest_safe"),
        ("XSTest v2 unsafe contrast (200), no thinking, 256 tok", "xstest_nothink256", "xstest_contrast")]
MODELS = [("liquid_q5", "Liquid Q5_K_M"), ("unc_q5", "AtomicChat Uncensored Q5_K_M"), ("plain_q5", "AtomicChat plain Q5_K_M")]
have_plain = any(k.startswith('plain_q5') for k in R)
cols = [m for m in MODELS if m[0] != 'plain_q5' or have_plain]
F = {}
t = ["| Set | " + " | ".join(c[1] for c in cols) + " |", "|---|" + "---|" * len(cols)]
for lab, k, cat in rows:
    vals = [cell(f"{m}_{k}", cat) for m, _ in cols]
    if all(v is None for v in vals): continue
    t.append(f"| {lab} | " + " | ".join(v[1] if v else "[PENDING]" for v in vals) + " |")
    for (m, _), v in zip(cols, vals):
        if v: F[f"{m}|{k}|{cat}"] = [v[0]['refused'], v[0]['n'], v[0]['rate'], v[0]['ci95'], v[0].get('no_final_answer', 0), v[0].get('capped_len', 0)]
cap = []
for key, e in R.items():
    for cat, v in e.items():
        if v.get('no_final_answer') or v.get('capped_len'): cap.append(f"`{key}`/{cat}: {v['no_final_answer']} without a final answer, {v['capped_len']} hit the token cap")
sec4 = ["## 4. Refusals", "",
"Q5_K_M against Q5_K_M, the same llama.cpp build, greedy (temperature 0), Liquid's chat template from the file, inside the no-network sandbox.",
"A reply counts as a refusal when its opening (after any thinking) matches the round-1 refusal pattern (`repro/scripts/refusal3.py`);",
"like AtomicChat's own count this reads the opening only, so it is indicative, not a judge. 95% Wilson intervals.",
"AtomicChat's test subsets (81 of the 100 JBB prompts; 30 thinking prompts) are not published, so I use the full JBB-100 and XSTest v2.", ""] + t + [""]
if cap: sec4 += ["Replies without a final answer (thinking not closed within the budget) count as not refused and are listed here: " + "; ".join(cap) + ".", ""]
# ---- MMLU
mrow = ["| Model | n | correct | accuracy (95% Wilson) | no letter |", "|---|---|---|---|---|"]
for m, lab in MODELS:
    e = M.get(m)
    if e: mrow.append(f"| {lab} | {e['n']} | {e['correct']} | {pct(e['acc'])} ({pct(e['ci95_wilson'][0])}–{pct(e['ci95_wilson'][1])}) | {e['no_letter']} |")
D = M.get('unc_q5_minus_liquid_q5'); DP = M.get('unc_q5_minus_plain_q5') or M.get('plain_q5_minus_unc_q5')
nfull = 14042
sec5 = ["## 5. MMLU", "",
"Liquid's model card (`LiquidAI/LFM2.5-24B-A2B` @ `3fcfdbf`) publishes **no MMLU score**. The \"64.4% for the original\" in the X post is",
"AtomicChat's own measurement, on a 2,000-question subset they do not publish, in BF16, and the card says MMLU was used to choose the variant",
"(so it is not a held-out number). Their card itself calls the +1.15 points \"inside the noise\" (McNemar p = 0.06).", "",
f"My run: `cais/mmlu` `all/test`, 0-shot, thinking off, greedy, same harness and quant for both, on the first {min((M.get(m) or {}).get('n', 0) for m in ('liquid_q5', 'unc_q5')):,} questions of a fixed seed-0 shuffle (a uniform random sample of the {nfull:,}), paired on the same questions.", "",
"**Step 1, strict:** the first standalone A/B/C/D of an 8-token reply.", ""] + mrow + [""]
if D:
    lo, hi = D['ci95_pp_paired_bootstrap']
    sec5 += [f"Strict paired difference, Uncensored − Liquid: {D['delta_pp']:+.2f} pp (95% paired-bootstrap CI {lo:+.2f} to {hi:+.2f}; {D['b_gained']} gained, {D['b_lost']} lost).",
             "Most of this is answer format, not knowledge: Liquid often starts explaining inside the 8 tokens and never reaches a letter.", ""]
    F['mmlu_delta'] = D
LN = S.get('mmlu_lenient')
if LN:
    sec5 += ["**Step 2, lenient (headline):** only the no-letter questions were asked again with 256 tokens (`mmlu_rescore.py`); I count only an explicit final answer",
             "(`</think>X`, \"answer is X\", `\\boxed{X}`, `**Option X**`, or a bare letter), never a letter guessed from unfinished reasoning (`mmlu_lenient.py`).", "",
             "| Model | n | correct | accuracy (95% Wilson) | re-asked | re-asked correct | still no answer |", "|---|---|---|---|---|---|---|"]
    for m, lab in MODELS:
        e = LN.get(m)
        if e: sec5.append(f"| {lab} | {e['n']} | {e['correct']} | {pct(e['acc'])} ({pct(e['ci95_wilson'][0])}–{pct(e['ci95_wilson'][1])}) | {e['rescored']} | {e['rescored_correct']} | {e['still_no_letter']} |")
    L2 = LN['unc_q5_minus_liquid_q5']; BA = LN['both_answered']
    sec5 += ["", f"Paired difference, Uncensored − Liquid, on {L2['n']:,} questions: **{L2['delta_pp']:+.2f} pp** (95% paired-bootstrap CI {L2['ci95_pp_paired_bootstrap'][0]:+.2f} to {L2['ci95_pp_paired_bootstrap'][1]:+.2f}),",
             f"{L2['b_gained']} gained vs {L2['b_lost']} lost, exact McNemar p = {L2['mcnemar_exact_p']:.2g}.", "",
             f"Sensitivity, only the {BA['n']:,} questions where both models gave a final answer: Liquid {pct(BA['liquid_acc'])}, Uncensored {pct(BA['unc_acc'])},",
             f"**{BA['delta_pp']:+.2f} pp** (95% CI {BA['ci95_pp_paired_bootstrap'][0]:+.2f} to {BA['ci95_pp_paired_bootstrap'][1]:+.2f}; {BA['b_gained']} gained, {BA['b_lost']} lost; McNemar p = {BA['mcnemar_exact_p']:.2g}).",
             "This subset is not random (it drops the questions Liquid could not finish), so I treat it as a sensitivity check, not a cleaner estimate.", ""]
    F['mmlu_lenient'] = LN
if DP: sec5 += [f"AtomicChat plain vs Uncensored (same quant recipe and imatrix): {json.dumps(DP)}", ""]
F['mmlu'] = {m: M.get(m) for m, _ in MODELS}
json.dump(F, open(f'{E}/thread_facts_raw.json', 'w'), indent=1)
parts = [open('REPORT_part1.md').read(), open('REPORT_part3.md').read(), "\n".join(sec4), "\n".join(sec5), open('REPORT_verdict.md').read() if os.path.exists('REPORT_verdict.md') else "", open('REPORT_bonus.md').read(), open('REPORT_resume.md').read() if os.path.exists('REPORT_resume.md') else "",
         "## Appendix A: the 52 edited tensors (U = AtomicChat Uncensored Q8_0, C = my Q8_0 control, O = Liquid BF16)\n\n" + open('_sites_table.md').read()]
open('REPORT.md', 'w').write("\n\n".join(p.strip() + "\n" for p in parts if p))
print("REPORT.md written;", len(t) - 2, "refusal rows; mmlu", {m: (M.get(m) or {}).get('n') for m, _ in MODELS})
