# Merge strict MMLU rows (mmlu.py, 8 tokens) with the lenient rescore of their no-letter rows (mmlu_rescore.py, 256 tokens),
# then paired stats on the same questions. Adds "mmlu_lenient" to r3_summary.json.
# Usage: mmlu_lenient.py RESULTS_DIR SUMMARY_JSON [N=3000]
import json, sys, random, math, re
# Only an explicit final answer counts (a letter guessed from half-finished reasoning does not):
# "</think>X", "answer is X"/"answer: X", "\boxed{X}", "**Option X**", or a reply that is just the letter.
FIN = re.compile(r"(?:</think>\s*\**|answer(?: is)?\s*[:\-]?\s*\**\(?|\\boxed\{|\*\*option\s+)([ABCD])\b", re.I)
def final(r):
    a = r['reply']; m = FIN.findall(a)
    p = m[-1].upper() if m else (a.strip().strip('*').upper() if a.strip().strip('*').upper() in list('ABCD') else None)
    return dict(r, pred=p, correct=p == r['answer'])
R, SJ = sys.argv[1:3]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
def load(f): return [json.loads(l) for l in open(f)]
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d; return [round(c-h, 4), round(c+h, 4)]
def mcnemar(b, c):
    n = b + c; k = min(b, c); p = sum(math.comb(n, i) for i in range(k + 1)) / 2**n; return min(1.0, 2*p)
out = {}; C = {}; A = {}
for m in ['liquid_q5', 'unc_q5']:
    strict = load(f'{R}/mmlu_{m}.jsonl')[:N]; rs = {r['i']: final(r) for r in load(f'{R}/mmlu_rescore_{m}.jsonl')}
    rows = {r['i']: (rs[r['i']] if (not r['pred'] and r['i'] in rs) else r) for r in strict}
    C[m] = {i: bool(r['correct']) for i, r in rows.items()}; A[m] = {i for i, r in rows.items() if r['pred']}
    k = sum(C[m].values()); n = len(C[m])
    out[m] = dict(n=n, correct=k, acc=round(k/n, 5), ci95_wilson=wilson(k, n), rescored=len(rs),
                  still_no_letter=sum(1 for r in rows.values() if not r['pred']),
                  rescored_correct=sum(1 for r in rs.values() if r['correct']))
ids = sorted(set(C['liquid_q5']) & set(C['unc_q5'])); a = [C['liquid_q5'][i] for i in ids]; b = [C['unc_q5'][i] for i in ids]
d = [int(y) - int(x) for x, y in zip(a, b)]; rng = random.Random(0); n = len(d)
bs = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(10000))
gained = sum(1 for x in d if x > 0); lost = sum(1 for x in d if x < 0)
out['unc_q5_minus_liquid_q5'] = dict(n=n, delta_pp=round(100*sum(d)/n, 3), ci95_pp_paired_bootstrap=[round(100*bs[249], 3), round(100*bs[9749], 3)],
    b_gained=gained, b_lost=lost, mcnemar_exact_p=mcnemar(gained, lost))
# Sensitivity: only questions where BOTH models gave a final answer (removes the leftover format penalty).
ids2 = sorted(A['liquid_q5'] & A['unc_q5']); d2 = [int(C['unc_q5'][i]) - int(C['liquid_q5'][i]) for i in ids2]; n2 = len(d2); rng = random.Random(0)
bs2 = sorted(sum(d2[rng.randrange(n2)] for _ in range(n2)) / n2 for _ in range(10000))
g2 = sum(1 for x in d2 if x > 0); l2 = sum(1 for x in d2 if x < 0)
out['both_answered'] = dict(n=n2, liquid_acc=round(sum(C['liquid_q5'][i] for i in ids2)/n2, 5), unc_acc=round(sum(C['unc_q5'][i] for i in ids2)/n2, 5),
    delta_pp=round(100*sum(d2)/n2, 3), ci95_pp_paired_bootstrap=[round(100*bs2[249], 3), round(100*bs2[9749], 3)], b_gained=g2, b_lost=l2, mcnemar_exact_p=mcnemar(g2, l2))
S = json.load(open(SJ)); S['mmlu_lenient'] = out; json.dump(S, open(SJ, 'w'), indent=1)
print(json.dumps(out, indent=1))
