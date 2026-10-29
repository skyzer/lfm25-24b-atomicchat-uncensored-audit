import shutil, json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
BG, FG, MUT, A = "#0f1418", "#e8edf2", "#8a98a8", "#4cc9f0"
def card(path, title, lines, foot):
    f = plt.figure(figsize=(10.24, 5.76), dpi=100, facecolor=BG)
    f.text(0.04, 0.88, title, fontsize=26, weight="bold", color=FG)
    y = 0.74
    for l, c in lines:
        f.text(0.05, y, l, fontsize=16, color=c, va="top"); y -= 0.095
    f.text(0.04, 0.04, foot, fontsize=10.5, color=MUT)
    f.savefig(path, facecolor=BG); plt.close(f)
F = json.load(open("expected_outputs/thread_facts_raw.json")) if False else None
card("thread/img/post_01.png", "LFM2.5-24B-A2B Uncensored: an audit", [
 ("Claims: refusals 96% → 1%; MMLU 64.4% → 65.6%", FG),
 ("1  Card vs GGUF metadata", A), ("2  Weight diff vs my own requant control", A),
 ("3  Triggers, tool use, network (no network, strace)", A),
 ("4  Refusals: 28 prompts, JBB-100, XSTest, think on/off", A),
 ("5  MMLU, paired, same Q5 quant", A)],
 "Models: AtomicChat/LFM2.5-24B-A2B-Uncensored-GGUF @b0f357bb vs LiquidAI LFM2.5-24B-A2B. llama.cpp 19cce691.")
card("thread/img/post_02.png", "Card vs file metadata", [
 ("Card: abliteration, 52 matrices, blocks 14–39, scale 1.75", FG),
 ("GGUF atomic.abliterate.* keys: same sites, same scale", FG),
 ("Keys name the published directions.npz by sha256 (9e995555…)", FG),
 ("Tokenizer + chat template: identical to Liquid's", FG),
 ("Result: consistent", A)],
 "Source: expected_outputs/meta_unc_q8.json, card_atomic_b0f357b_README.md, tokdiff_unc_q8_vs_liquid_q5.txt")
for n, p in [(3, "weightdiff_by_layer"), (4, "edit_direction"), (5, "behaviour"), (6, "refusals"), (7, "mmlu")]:
    shutil.copy(f"plots/{p}.png", f"thread/img/post_{n:02d}.png")
fx = json.load(open("expected_outputs/thread_facts.json"))
mm = [l for l in fx["P8"].split("\n") if "Improved accuracy" in l][0].split(": ", 1)[1]
card("thread/img/post_08.png", "Verdict", [
 ("Card vs file: consistent", FG),
 ("Weights: rank-1 abliteration on the 52 listed sites; no evidence found of other changes", FG),
 ("Behaviour: no evidence found of triggers, odd tool use or network calls", FG),
 ("Refusals: the drop is real", A),
 (f"\"Improved accuracy\": {mm}", A),
 ("Limits: one quant, regex refusal count, 3,000 of 14,042 MMLU Qs, 0-shot", MUT)],
 "Scripts, data hashes and expected outputs: lfm25_atomic_audit_kit (REPORT.md, SHA256SUMS)")
print("ok")
