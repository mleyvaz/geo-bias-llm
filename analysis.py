"""
Geo Bias LLM — Reproduce all tables from the paper.
Usage: python analysis.py
"""
import json, statistics
from pathlib import Path

DATA = Path(__file__).parent / "data" / "pilot_results_v3.json"

with open(DATA, encoding="utf-8") as f:
    d = json.load(f)

models   = d["models"]
profiles = ["Anglo_T1", "Latino_T1", "Anglo_T5", "Latino_T5"]
domains  = d["domains"]

def sep(n=70): print("-" * n)

# ── Table 1: Mean scores ──────────────────────────────────────────────────
print("\nTABLE 1 — Mean Scores by Profile and Model (10-point scale)")
sep()
header = f"{'Profile':12s}" + "".join(f" {m[:10]:>11s}" for m in models) + f" {'Overall':>9s}"
print(header)
sep()
for p in profiles:
    scores = [d["global"][m][p]["mean_score"] for m in models]
    row = f"{p:12s}" + "".join(f" {s:11.3f}" for s in scores) + f" {statistics.mean(scores):9.3f}"
    print(row)

# ── Table 2: Factorial effects ────────────────────────────────────────────
print("\nTABLE 2 — Factorial Effects by Model")
sep()
print(f"{'Model':22s} | {'Inst. Effect (T1-T5)':22s} | {'Name Effect (Ang-Lat)':22s}")
sep()
inst_all, name_all = [], []
for m in models:
    ang_t1 = d["global"][m]["Anglo_T1"]["mean_score"]
    lat_t1 = d["global"][m]["Latino_T1"]["mean_score"]
    ang_t5 = d["global"][m]["Anglo_T5"]["mean_score"]
    lat_t5 = d["global"][m]["Latino_T5"]["mean_score"]
    inst = ((ang_t1 - ang_t5) + (lat_t1 - lat_t5)) / 2
    name = ((ang_t1 - lat_t1) + (ang_t5 - lat_t5)) / 2
    inst_all.append(inst); name_all.append(name)
    print(f"{m:22s} | {inst:+22.3f} | {name:+22.3f}")
sep()
print(f"{'Cross-model mean':22s} | {statistics.mean(inst_all):+22.3f} | {statistics.mean(name_all):+22.3f}")

# ── Table 3: Domain breakdown ─────────────────────────────────────────────
print("\nTABLE 3 — Domain Gap: Anglo_T1 vs Latino_T5 (cross-model mean)")
sep()
print(f"{'Domain':18s} | {'Anglo_T1':10s} | {'Latino_T5':10s} | {'Gap':8s} | Interpretation")
sep()
for dom in domains:
    t1_scores = [d["per_domain"][m]["Anglo_T1"][dom]["mean"] for m in models]
    t5_scores = [d["per_domain"][m]["Latino_T5"][dom]["mean"] for m in models]
    t1m = statistics.mean(t1_scores)
    t5m = statistics.mean(t5_scores)
    gap = t1m - t5m
    flag = "** largest bias **" if gap == max(
        statistics.mean([d["per_domain"][m]["Anglo_T1"][x]["mean"] for m in models]) -
        statistics.mean([d["per_domain"][m]["Latino_T5"][x]["mean"] for m in models])
        for x in domains) else ""
    print(f"{dom:18s} | {t1m:10.3f} | {t5m:10.3f} | {gap:+8.3f} | {flag}")

# ── Table 4: NBI values ───────────────────────────────────────────────────
print("\nTABLE 4 — NBI <T, I, F> by Model and Profile")
sep()
print(f"{'Model':22s} | {'Profile':12s} | {'T':8s} | {'I':8s} | {'F (bias)':10s}")
sep()
for m in models:
    for p in ["Anglo_T1", "Latino_T5"]:
        nbi = d["global"][m][p]["NBI"]
        print(f"{m:22s} | {p:12s} | {nbi['T']:8.4f} | {nbi['I']:8.4f} | {nbi['F']:10.4f}")
    print()
