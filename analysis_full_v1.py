"""
Geo Bias LLM — Full Study v1 Analysis
Reproduces all tables for the FAccT 2027 paper.
Usage: python analysis_full_v1.py
"""
import json, statistics
from pathlib import Path

DATA = Path("C:/Users/HP/Documents/sesgo_geografico_llm/full_results_v1.json")

with open(DATA, encoding="utf-8") as f:
    d = json.load(f)

models   = d["models"]
profiles = d["profiles"]
domains  = d["domains"]
tiers    = [1, 2, 3, 5]
names    = ["Anglo", "Latino", "Arabic"]

def sep(n=90): print("-" * n)

def tier_label(t):
    return {1: "T1-MIT", 2: "T2-UChile", 3: "T3-UNAL", 5: "T5-UGye"}[t]

# ── Table 1: Institution gradient (cross-model mean by tier) ──────────────
print("\nTABLE 1 — Mean Score by Institution Tier (cross-model mean, all name origins)")
sep()
print(f"{'Model':22s}" + "".join(f" {tier_label(t):>10s}" for t in tiers) + "  Gradient T1-T5")
sep()
for m in models:
    row = f"{m:22s}"
    tier_means = []
    for t in tiers:
        ps = [p for p in profiles if d["global"][m][p]["inst_tier"] == t]
        tm = statistics.mean(d["global"][m][p]["mean_score"] for p in ps)
        tier_means.append(tm)
        row += f" {tm:10.3f}"
    row += f"  {tier_means[0]-tier_means[-1]:+.3f}"
    print(row)
sep()
# Cross-model means
row = f"{'Cross-model mean':22s}"
gradients = []
for t in tiers:
    vals = []
    for m in models:
        ps = [p for p in profiles if d["global"][m][p]["inst_tier"] == t]
        vals.append(statistics.mean(d["global"][m][p]["mean_score"] for p in ps))
    row += f" {statistics.mean(vals):10.3f}"
t1_vals = [statistics.mean(d["global"][m][p]["mean_score"]
           for p in profiles if d["global"][m][p]["inst_tier"] == 1) for m in models]
t5_vals = [statistics.mean(d["global"][m][p]["mean_score"]
           for p in profiles if d["global"][m][p]["inst_tier"] == 5) for m in models]
gradient = statistics.mean(t1_vals) - statistics.mean(t5_vals)
row += f"  {gradient:+.3f}"
print(row)

# ── Table 2: Name effect (cross-model mean by name origin) ────────────────
print("\nTABLE 2 — Mean Score by Name Origin (cross-model mean, all tiers)")
sep()
print(f"{'Model':22s}" + "".join(f" {n:>10s}" for n in names) + "  Max gap")
sep()
for m in models:
    row = f"{m:22s}"
    name_means = []
    for name in names:
        ps = [p for p in profiles if d["global"][m][p]["name_origin"] == name]
        nm = statistics.mean(d["global"][m][p]["mean_score"] for p in ps)
        name_means.append(nm)
        row += f" {nm:10.3f}"
    row += f"  {max(name_means)-min(name_means):+.3f}"
    print(row)
sep()
row = f"{'Cross-model mean':22s}"
all_name_means = {}
for name in names:
    vals = []
    for m in models:
        ps = [p for p in profiles if d["global"][m][p]["name_origin"] == name]
        vals.append(statistics.mean(d["global"][m][p]["mean_score"] for p in ps))
    all_name_means[name] = statistics.mean(vals)
    row += f" {all_name_means[name]:10.3f}"
row += f"  {max(all_name_means.values())-min(all_name_means.values()):+.3f}"
print(row)

# ── Table 3: 3×4 cell means matrix ───────────────────────────────────────
print("\nTABLE 3 — Cell Means Matrix (cross-model mean): Name × Tier")
sep()
print(f"{'':12s}" + "".join(f" {tier_label(t):>10s}" for t in tiers))
sep()
for name in names:
    row = f"{name:12s}"
    for t in tiers:
        cell_ps = [p for p in profiles
                   if d["global"][models[0]][p]["name_origin"] == name
                   and d["global"][models[0]][p]["inst_tier"] == t]
        cell_label = cell_ps[0] if cell_ps else None
        if cell_label:
            val = statistics.mean(
                d["global"][m][cell_label]["mean_score"] for m in models
            )
            row += f" {val:10.3f}"
        else:
            row += f" {'N/A':>10s}"
    print(row)

# ── Table 4: Domain breakdown — Institution gradient by domain ────────────
print("\nTABLE 4 — Institution Gradient (T1-T5) by Domain (cross-model mean)")
sep()
print(f"{'Domain':18s} | {'T1-MIT':8s} | {'T2-UChile':9s} | {'T3-UNAL':8s} | {'T5-UGye':8s} | {'Gap T1-T5':10s}")
sep()
for dom in domains:
    row_parts = []
    tier_domain_means = []
    for t in tiers:
        ps_labels = [p for p in profiles if d["global"][models[0]][p]["inst_tier"] == t]
        vals = []
        for m in models:
            for pl in ps_labels:
                vals.append(d["per_domain"][m][pl][dom]["mean"])
        tier_domain_means.append(statistics.mean(vals))
    gap = tier_domain_means[0] - tier_domain_means[-1]
    flag = " ** prestige proxy **" if dom in ("credit", "health") and gap > 0.15 else ""
    print(f"{dom:18s} | {tier_domain_means[0]:8.3f} | {tier_domain_means[1]:9.3f} | {tier_domain_means[2]:8.3f} | {tier_domain_means[3]:8.3f} | {gap:+10.3f}{flag}")

# ── Table 5: NBI for worst-case profile (Arabic_T5) ──────────────────────
print("\nTABLE 5 — NBI <T, I, F> for Arabic_T5 vs Anglo_T1 (worst vs best)")
sep()
print(f"{'Model':22s} | {'Profile':12s} | {'T':8s} | {'I':8s} | {'F (bias)':10s}")
sep()
for m in models:
    for p in ["Anglo_T1", "Arabic_T5"]:
        if p in d["global"][m]:
            nbi = d["global"][m][p]["NBI"]
            print(f"{m:22s} | {p:12s} | {nbi['T']:8.4f} | {nbi['I']:8.4f} | {nbi['F']:10.4f}")
    print()

# ── Summary stats for paper ────────────────────────────────────────────────
print("\n=== KEY NUMBERS FOR PAPER ===")
sep()
t1_all = [statistics.mean(d["global"][m][p]["mean_score"]
          for p in profiles if d["global"][m][p]["inst_tier"] == 1) for m in models]
t5_all = [statistics.mean(d["global"][m][p]["mean_score"]
          for p in profiles if d["global"][m][p]["inst_tier"] == 5) for m in models]
print(f"Cross-model institution gradient (T1-T5): {statistics.mean(t1_all)-statistics.mean(t5_all):+.3f}")

anglo_all  = [statistics.mean(d["global"][m][p]["mean_score"]
              for p in profiles if d["global"][m][p]["name_origin"] == "Anglo") for m in models]
arabic_all = [statistics.mean(d["global"][m][p]["mean_score"]
              for p in profiles if d["global"][m][p]["name_origin"] == "Arabic") for m in models]
latino_all = [statistics.mean(d["global"][m][p]["mean_score"]
              for p in profiles if d["global"][m][p]["name_origin"] == "Latino") for m in models]
print(f"Cross-model name gap (Anglo-Arabic):      {statistics.mean(anglo_all)-statistics.mean(arabic_all):+.3f}")
print(f"Cross-model name gap (Anglo-Latino):      {statistics.mean(anglo_all)-statistics.mean(latino_all):+.3f}")
