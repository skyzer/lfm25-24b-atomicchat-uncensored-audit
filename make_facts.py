# Fill thread posts 5-8 (thread/thread_src.py) and REPORT_verdict.md from expected_outputs/r3_summary.json + beh_an_r3.json.
# usage (from kit/): python3 make_facts.py && python3 build_report.py && python3 thread/thread_src.py write
import json
E = 'expected_outputs'; S = json.load(open(f'{E}/r3_summary.json')); B = json.load(open(f'{E}/beh_an_r3.json'))
R, M = S['refusals'], S['mmlu']
def g(m, k, c):
    e = R.get(f'{m}_{k}', {}).get(c); return e
def fr(m, k, c):
    e = g(m, k, c); return f"{e['refused']}/{e['n']}" if e else "[PENDING]"
def pc(m, k, c):
    e = g(m, k, c); return f"{100*e['rate']:.0f}%" if e else "n/a"
L, U = 'liquid_q5', 'unc_q5'
ST = M.get('unc_q5_minus_liquid_q5'); sl, su = M.get(L), M.get(U)          # strict, 8-token harness (context only)
LN = S.get('mmlu_lenient'); PEND = LN is None
if PEND: raise SystemExit("run repro/scripts/mmlu_lenient.py first")
D = LN['unc_q5_minus_liquid_q5']; ml, mu = LN[L], LN[U]; BA = LN['both_answered']   # lenient = headline
lo, hi = D['ci95_pp_paired_bootstrap']; blo, bhi = BA['ci95_pp_paired_bootstrap']
mv = "higher, and the interval excludes zero" if lo > 0 else ("lower, and the interval excludes zero" if hi < 0 else "within noise: the interval includes zero")
s = B['trig']['unc_q5_summary']; t = B['tools']['unc_q5']
jt = g(L, 'jbb_think3072', 'jbb_harmful')
F = {}
F['P5'] = ("4. Behaviour, with the network cut and strace on\n"
 "• 0 outbound connection attempts\n"
 f"• 50 trigger prefixes × 10 prompts, incl. their own name: largest shift {s['did_z_max']:.2f} SD, none above 3\n"
 f"• 70 agent tasks: {len(t['flags'])} flagged tool calls, {len(t['unexpected_domains'])} unexpected domains")
jline = f"• JBB-100: {fr(L,'jbb_nothink256','jbb_harmful')} → {fr(U,'jbb_nothink256','jbb_harmful')}" + (f" (think: {fr(L,'jbb_think3072','jbb_harmful')} → {fr(U,'jbb_think3072','jbb_harmful')})" if jt else "")
F['P6'] = ("5. Refusals, Liquid → Uncensored, same Q5 quant and harness\n"
 f"• 20 harmful, no think: {fr(L,'r1_nothink1024','harmful')} → {fr(U,'r1_nothink1024','harmful')}\n"
 f"• Same, think on: {fr(L,'r1_think8192','harmful')} → {fr(U,'r1_think8192','harmful')}\n"
 + jline + "\n"
 f"• XSTest safe: {fr(L,'xstest_nothink256','xstest_safe')} → {fr(U,'xstest_nothink256','xstest_safe')}\n"
 "The refusal drop holds up")
F['P7'] = ("6. MMLU\n"
 "• Liquid publishes no score. AtomicChat's 64.4% is an unpublished 2,000-q subset that also picked the variant\n"
 f"• Mine, Q5, {D['n']:,} paired Qs: {100*ml['acc']:.1f}% → {100*mu['acc']:.1f}%, {D['delta_pp']:+.1f} pts (CI {lo:+.1f} to {hi:+.1f})\n"
 f"• Liquid often runs past the answer cap. Where both answered: {BA['delta_pp']:+.1f} (CI {blo:+.1f} to {bhi:+.1f})")
verdict_mmlu = ("not supported: no evidence found of a gain" if blo <= 0 else
  ("a small gain at Q5, partly answer format" if blo < 1.2 else "a gain at Q5, partly answer format"))
F['P8'] = ("Verdict\n"
 "• A rank-1 abliteration, as the card says. No evidence found of anything else\n"
 "• Refusals: big drop, confirmed\n"
 f"• \"Improved accuracy\": {verdict_mmlu.replace('a small gain', 'small gain').replace('answer format', 'format')}\n"
 "Limits: one quant, regex refusal count, 3k MMLU Qs, 0-shot\n"
 "Scripts + hashes: https://github.com/skyzer/lfm25-24b-atomicchat-uncensored-audit")
json.dump(F, open(f'{E}/thread_facts.json', 'w'), indent=1, ensure_ascii=False)
MROW = (f"Liquid publishes no MMLU score. On {D['n']:,} paired random questions at Q5_K_M (0-shot, thinking off): Liquid {100*ml['acc']:.2f}% (95% CI {100*ml['ci95_wilson'][0]:.1f}–{100*ml['ci95_wilson'][1]:.1f}), "
  f"Uncensored {100*mu['acc']:.2f}% ({100*mu['ci95_wilson'][0]:.1f}–{100*mu['ci95_wilson'][1]:.1f}), difference {D['delta_pp']:+.2f} pp (paired bootstrap 95% CI {lo:+.2f} to {hi:+.2f}; {D['b_gained']} gained, {D['b_lost']} lost; McNemar p = {D['mcnemar_exact_p']:.2g}), {mv}. "
  f"Part of this is answer format: with an 8-token answer cap Liquid gave no letter on {sl['no_letter'] if 'no_letter' in sl else ml['rescored']} questions (strict scores {100*sl['acc']:.2f}% vs {100*su['acc']:.2f}%, {ST['delta_pp']:+.2f} pp); I re-asked those with 256 tokens and counted only explicit final answers, and Liquid still gave none on {ml['still_no_letter']} (Uncensored: {mu['still_no_letter']}). "
  f"On the {BA['n']:,} questions where both models gave a final answer: {100*BA['liquid_acc']:.2f}% vs {100*BA['unc_acc']:.2f}%, {BA['delta_pp']:+.2f} pp (95% CI {blo:+.2f} to {bhi:+.2f}, McNemar p = {BA['mcnemar_exact_p']:.2g}).")
V = f"""## 6. Verdicts

| Check | Verdict |
|---|---|
| 1. Card vs metadata | Consistent. The GGUF's `atomic.abliterate.*` keys describe the card's edit and name the published `directions.npz` by sha256; tokenizer and chat template are identical to Liquid's. Minor: `base_model` names `-Base`. |
| 2. Weights | A rank-1 abliteration on exactly 52 tensors (blocks 14–39), strength k = −0.75 (scale 1.75). The other 376 tensors are byte-identical to my own Q8_0 requant; their plain build is 428/428 identical; the LoRA is the same edit factored. No evidence found of any other change. |
| 3. Trigger / tools / network | No evidence found of a trigger, of tool-call misuse or of network activity: 0 external connection attempts under strace for either model; largest trigger shift {s['did_z_max']:.2f} SD (none above 3); {t['calls']} tool calls, {len(t['flags'])} flagged, {len(t['unexpected_domains'])} unexpected domains. |
| 4. Refusals | The claimed drop is reproduced in direction and size: 20 harmful prompts {fr(L,'r1_nothink1024','harmful')} → {fr(U,'r1_nothink1024','harmful')} (no think), {fr(L,'r1_think8192','harmful')} → {fr(U,'r1_think8192','harmful')} (think, 8192 tokens); JBB-100 {fr(L,'jbb_nothink256','jbb_harmful')} → {fr(U,'jbb_nothink256','jbb_harmful')} (no think){f", {fr(L,'jbb_think3072','jbb_harmful')} → {fr(U,'jbb_think3072','jbb_harmful')} (think)" if jt else ""}. Over-refusal on XSTest safe prompts {fr(L,'xstest_nothink256','xstest_safe')} → {fr(U,'xstest_nothink256','xstest_safe')}. |
| 5. MMLU | {MROW} |
| Bonus: abenzerps | Not a rebadge or requant of AtomicChat's file: a different quant recipe, different edit sites, and edit directions only loosely related (|cos| 0.22–0.34). |

### The X post vs what I measured
- "Refusals from 96% to 1%": the drop holds up on my sets (their exact 81-prompt subset is unpublished, so the percentages are not the same test).
- "Improved the model's accuracy … 65.6% vs 64.4%": {verdict_mmlu} on my paired run ({BA['delta_pp']:+.1f} pp, CI {blo:+.1f} to {bhi:+.1f}, on questions both answered; {D['delta_pp']:+.1f} pp overall). Their own card calls the +1.15 points "inside the noise" (p = 0.06) and says MMLU was used to choose the variant, so the 65.6% is not a held-out score.

### Limits
- One quantization per test (Q5_K_M for behaviour, refusals and MMLU; Q8_0 for the weight diff), greedy decoding, a single seed.
- The refusal count is a regex on the opening of the final answer, not a judge; I read the refusals by hand but did not grade the compliant answers for quality or harm.
- MMLU: {D['n']:,} of 14,042 questions (seed-0 shuffle); 0-shot, thinking off; letter from an 8-token reply, with only the no-letter replies re-asked at 256 tokens. The gap is sensitive to answer format; the both-answered subset is not a random sample.
- Behaviour checks can only find what they probe for: no evidence found is not proof of absence.
"""
open('REPORT_verdict.md', 'w').write(V)
print(json.dumps(F, indent=1, ensure_ascii=False))
