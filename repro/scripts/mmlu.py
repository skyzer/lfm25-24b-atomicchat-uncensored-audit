# MMLU (cais/mmlu "all" test, 14,042 questions, pinned revision), zero-shot, chat template, reasoning OFF
# (empty <think></think> block, as AtomicChat's thinking-off evaluation), greedy, up to 8 new tokens.
# The predicted letter is the first standalone A/B/C/D in the reply; no letter = wrong. Same harness for every model.
# Usage: mmlu.py PORT data/mmlu_test.jsonl OUT.jsonl [NPAR=8] [LIMIT]
import json, sys, re, requests
from concurrent.futures import ThreadPoolExecutor
port, fin, out = sys.argv[1:4]; NPAR = int(sys.argv[4]) if len(sys.argv) > 4 else 8; LIM = int(sys.argv[5]) if len(sys.argv) > 5 else None
U = f"http://127.0.0.1:{port}"; L = "ABCD"
Q = [json.loads(l) for l in open(fin)][:LIM]
done = set()
try: done = {json.loads(l)['i'] for l in open(out)}
except FileNotFoundError: pass
def prompt(q):
    s = q['subject'].replace('_', ' ')
    body = "\n".join(f"{L[k]}. {c}" for k, c in enumerate(q['choices']))
    return (f"The following is a multiple choice question about {s}. Reply with only the letter of the correct answer (A, B, C or D).\n\n"
            f"{q['question']}\n{body}")
def work(q):
    t = requests.post(U + "/apply-template", json={"messages": [{"role": "user", "content": prompt(q)}]}).json()["prompt"]
    assert t.endswith("<think>"), t[-40:]
    toks = requests.post(U + "/tokenize", json={"content": t + "</think>", "add_special": False, "parse_special": True}).json()["tokens"]
    r = requests.post(U + "/completion", json={"prompt": toks, "temperature": 0, "top_k": 1, "seed": 0, "n_predict": 8, "cache_prompt": False}, timeout=3600).json()
    a = r.get("content", ""); m = re.search(r"\b([ABCD])\b", a)
    p = m.group(1) if m else None
    return dict(i=q['i'], subject=q['subject'], answer=L[q['answer']], pred=p, correct=p == L[q['answer']], reply=a[:40])
with open(out, "a") as f, ThreadPoolExecutor(NPAR) as ex:
    for row in ex.map(work, [q for q in Q if q['i'] not in done]): f.write(json.dumps(row) + "\n"); f.flush()
print("done", out)
