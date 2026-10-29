# Thread source. Posts 5-8 take numbers from ../expected_outputs/thread_facts.json (made by make_facts.py).
# usage: python3 thread_src.py          -> print lengths
#        python3 thread_src.py write    -> write post_XX.md + thread.md
import re, sys, json, os, unicodedata
H = os.path.dirname(os.path.abspath(__file__))
FP = os.path.join(H, '..', 'expected_outputs', 'thread_facts.json')
F = json.load(open(FP)) if os.path.exists(FP) else {}
XURL = "https://x.com/atomic_chat_hq/status/2110241691475349854"
P = [
"""On Oct 14 AtomicChat posted about their uncensored LFM2.5-24B-A2B GGUF:

"We cut refusals from 96% to 1% and improved the model's accuracy … 65.6% of MMLU questions right vs 64.4% for the original"

I checked the weights, the behaviour and both numbers 🧵""",
"""1. Card vs file
• The card says it's an abliteration: a refusal direction removed from 52 matrices in blocks 14–39, scale 1.75
• The GGUF metadata says the same, and names their published directions file by hash
• Tokenizer and chat template: identical to Liquid's""",
"""2. Weight diff vs a clean control
• I compressed Liquid's BF16 to Q8_0 myself. Q8_0/F16/F32 are deterministic, so untouched tensors must match byte for byte
• 376 of 428 do. The 52 that don't are exactly the card's list
• Their plain build: 428/428 identical""",
"""3. Shape of the edit
• Each of the 52 changes is rank-1 along their published direction (|cos| ≥ 0.99999)
• The fitted strength is −0.75, i.e. 1 − 1.75, as the card says
• Their LoRA is the same edit, factored

No evidence found of any other change""",
"{P5}", "{P6}", "{P7}", "{P8}",
]
def fill(p):
    return re.sub(r'\{(\w+)\}', lambda m: str(F.get(m.group(1), m.group(0))), p)
def _w(c):
    c = ord(c); return 1 if (c <= 4351 or 8192 <= c <= 8205 or 8208 <= c <= 8223 or 8242 <= c <= 8247) else 2
def n(s):  # X weighted length: URL = 23, most non-Latin symbols (bullets, emoji) = 2
    s = unicodedata.normalize('NFC', re.sub(r'https?://\S+|REPO_URL', 'x' * 23, s)); return sum(_w(c) for c in s)
if __name__ == '__main__':
    posts = [fill(p) for p in P if not fill(p).startswith('{')]
    for i, p in enumerate(posts): print(i + 1, n(p))
    if len(sys.argv) > 1 and sys.argv[1] == 'write':
        assert all(n(p) <= 280 for p in posts)
        md = []
        for i, p in enumerate(posts):
            open(os.path.join(H, f'post_{i+1:02d}.md'), 'w').write(p + '\n')
            md.append(f'### Post {i+1}/{len(posts)} ({n(p)} chars, image: img/post_{i+1:02d}.png)\n\n{p}\n')
        open(os.path.join(H, 'thread.md'), 'w').write('# Thread\n\n' + '\n'.join(md))
