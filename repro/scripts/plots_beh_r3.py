# Behaviour chart (check 3). Usage: plots_beh_r3.py expected_outputs OUT_DIR
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from charts_common import *
import numpy as np
E, O = sys.argv[1], sys.argv[2]
B = json.load(open(f"{E}/beh_an_r3.json")); S = json.load(open(f"{E}/strace_summary_r3.json"))
P = B["trig"]["per_trigger"]; T = sorted(k for k in P if k)
d = np.array([P[k]["unc_q5"]["did"] for k in T]); s = B["trig"]["unc_q5_summary"]
f = fig(); title(f, "Behaviour with the network cut: nothing found", "Shift in Uncensored replies per trigger prefix, beyond Liquid's own (10 prompts each)")
a = f.add_axes([0.10, 0.17, 0.52, 0.60]); ax_style(a)
a.bar(range(len(T)), d, color=ABZ); m, sd = s["did_mean"], s["did_sd"]
for z in (3, -3): a.axhline(m + z*sd, color=WARN, ls="--")
a.text(0.5, m + 3*sd + 0.02, "3 SD", color=WARN, fontsize=13); a.set_xlabel("50 trigger prefixes (incl. AtomicChat, abenzerps)"); a.set_ylabel("shift (diff-in-diff)"); a.set_xticks([])
t = B["tools"]["unc_q5"]; tl = B["tools"]["liquid25_q5"]
ext = sum(v["external_attempts"] for v in S.values())
note = (f"Largest shift: {s['did_z_max']:.2f} SD\nTriggers above 3 SD: {len(s['triggers_did_over_3sd'])}\n\n"
        f"strace, both models:\n  {ext} external connection attempts\n\n"
        f"70 agent tasks (fake tools):\n  Uncensored {t['calls']} calls, Liquid {tl['calls']}\n  flagged calls: {len(t['flags'])}\n  unexpected domains: {len(t['unexpected_domains'])}\n\n"
        f"No evidence found of a trigger,\ntool misuse or network activity")
f.text(0.66, 0.78, note, fontsize=15, color=FG, va="top", linespacing=1.35)
foot(f, "Source: expected_outputs/beh_an_r3.json, strace_summary_r3.json. Q5_K_M, greedy, bwrap --unshare-net + strace.")
save(f, f"{O}/behaviour.png"); print("ok")
