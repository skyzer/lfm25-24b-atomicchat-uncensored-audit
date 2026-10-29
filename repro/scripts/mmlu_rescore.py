# Lenient MMLU rescore. mmlu.py stops after 8 tokens; a model that starts explaining before giving a letter
# then scores "no letter" (= wrong). This re-asks ONLY the no-letter rows of an mmlu_*.jsonl, same prompt,
# same template (thinking off), greedy, up to 256 tokens, and extracts the letter:
#   1) "answer is/answer: X" (optionally bold or in parentheses), else 2) the LAST standalone A-D in the reply.
# Usage: mmlu_rescore.py PORT data/mmlu_test_shuf.jsonl IN_mmlu.jsonl OUT_rescore.jsonl [NPAR=8]
import json, sys, re, requests
from concurrent.futures import ThreadPoolExecutor
port, fq, fin, out = sys.argv[1:5]; NPAR = int(sys.argv[5]) if len(sys.argv) > 5 else 8
U = f"http://127.0.0.1:{port}"; L = "ABCD"
Q = {q['i']: q for q in map(json.loads, open(fq))}
todo = [r['i'] for r in map(json.loads, open(fin)) if not r['pred']]
done = set()
try: done = {json.loads(l)['i'] for l in open(out)}
except FileNotFoundError: pass
def prompt(q):
    s = q['subject'].replace('_', ' ')
    body = "\n".join(f"{L[k]}. {c}" for k, c in enumerate(q['choices']))
    return (f"The following is a multiple choice question about {s}. Reply with only the letter of the correct answer (A, B, C or D).\n\n"
            f"{q['question']}\n{body}")
AP = re.compile(r"answer(?: is)?\s*[:\-]?\s*\**\(?([ABCD])\b", re.I)
def work(i):
    q = Q[i]
    t = requests.post(U + "/apply-template", json={"messages": [{"role": "user", "content": prompt(q)}]}).json()["prompt"]
    assert t.endswith("<think>"), t[-40:]
    toks = requests.post(U + "/tokenize", json={"content": t + "</think>", "add_special": False, "parse_special": True}).json()["tokens"]
    a = requests.post(U + "/completion", json={"prompt": toks, "temperature": 0, "top_k": 1, "seed": 0, "n_predict": 256, "cache_prompt": False}, timeout=3600).json().get("content", "")
    m = AP.findall(a) or re.findall(r"\b([ABCD])\b", a)
    p = m[-1].upper() if m else None
    return dict(i=i, subject=q['subject'], answer=L[q['answer']], pred=p, correct=p == L[q['answer']], via="answer_is" if AP.search(a) else ("last_letter" if p else "none"), reply=a[-160:])
with open(out, "a") as f, ThreadPoolExecutor(NPAR) as ex:
    for row in ex.map(work, [i for i in todo if i not in done]): f.write(json.dumps(row) + "\n"); f.flush()
print("RESCORE_DONE", out)
