"""
Bootstrap confidence intervals para Study 1 y Study 2.
Añade rigor estadístico sin costo de API adicional.
Output: bootstrap_results.json con CIs para todas las comparaciones clave.
"""
import json, numpy as np, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

np.random.seed(42)
N_BOOT = 10_000

# ── Load data ─────────────────────────────────────────────────────────────
with open('C:/Users/HP/Documents/sesgo_geografico_llm/full_results_v1.json') as f:
    d1 = json.load(f)
with open('C:/Users/HP/Documents/sesgo_geografico_llm/study2_results.json') as f:
    d2 = json.load(f)

raw1 = d1['raw']   # 1440 records: model, name_origin, inst_tier, domain, score
raw2 = d2['raw']   # 1440 records: model, name_label, inst_label, prestige, country_dev, domain, score

def scores(records, **filters):
    """Return score array for records matching all filter key=value pairs."""
    out = []
    for r in records:
        if all(r.get(k) == v for k, v in filters.items()):
            out.append(r['score'])
    return np.array(out)

def boot_diff(a, b, n=N_BOOT):
    """Bootstrap 95% CI for mean(a) - mean(b). Returns (obs, lo, hi)."""
    obs = np.mean(a) - np.mean(b)
    diffs = np.array([
        np.mean(np.random.choice(a, len(a))) - np.mean(np.random.choice(b, len(b)))
        for _ in range(n)
    ])
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return float(obs), float(lo), float(hi)

def boot_mean(a, n=N_BOOT):
    """Bootstrap 95% CI for mean(a). Returns (obs, lo, hi)."""
    obs = np.mean(a)
    means = np.array([np.mean(np.random.choice(a, len(a))) for _ in range(n)])
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(obs), float(lo), float(hi)

results = {}

# ══════════════════════════════════════════════════════════════════════════
# STUDY 1: Institution-tier gradient
# ══════════════════════════════════════════════════════════════════════════
print("=== STUDY 1: Institution-Tier Gradient ===")
models1 = ["Claude Haiku 4.5", "GPT-4o-mini", "Gemini 2.0 Flash", "Llama 3.1 8B"]
tiers   = [1, 2, 3, 5]

tier_means = {}
for model in models1:
    tier_means[model] = {}
    for t in tiers:
        s = scores(raw1, model=model, inst_tier=t)
        tier_means[model][t] = s

# Cross-model gradient T1 - T5
all_T1 = scores(raw1, inst_tier=1)
all_T5 = scores(raw1, inst_tier=5)
obs, lo, hi = boot_diff(all_T1, all_T5)
print(f"  Cross-model T1-T5 gradient: {obs:+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]")
results['s1_gradient_T1_T5'] = {'obs': obs, 'ci95_lo': lo, 'ci95_hi': hi,
    'n_T1': len(all_T1), 'n_T5': len(all_T5)}

# Per-model gradients
results['s1_gradient_by_model'] = {}
for model in models1:
    a = tier_means[model][1]
    b = tier_means[model][5]
    obs, lo, hi = boot_diff(a, b)
    print(f"  {model:<22} T1-T5: {obs:+.3f}  [{lo:+.3f}, {hi:+.3f}]")
    results['s1_gradient_by_model'][model] = {'obs': obs, 'ci95_lo': lo, 'ci95_hi': hi}

# T1 vs T2 (is the jump significant?)
a = scores(raw1, inst_tier=1)
b = scores(raw1, inst_tier=2)
obs, lo, hi = boot_diff(a, b)
print(f"  T1 vs T2: {obs:+.3f}  [{lo:+.3f}, {hi:+.3f}]")
results['s1_T1_vs_T2'] = {'obs': obs, 'ci95_lo': lo, 'ci95_hi': hi}

# T2 vs T3 (practically the same?)
a = scores(raw1, inst_tier=2)
b = scores(raw1, inst_tier=3)
obs, lo, hi = boot_diff(a, b)
print(f"  T2 vs T3: {obs:+.3f}  [{lo:+.3f}, {hi:+.3f}]  (expect near-zero)")
results['s1_T2_vs_T3'] = {'obs': obs, 'ci95_lo': lo, 'ci95_hi': hi}

# ══════════════════════════════════════════════════════════════════════════
# STUDY 1: Name-origin effect
# ══════════════════════════════════════════════════════════════════════════
print("\n=== STUDY 1: Name-Origin Effect ===")
names = ['Anglo', 'Latino', 'Arabic']
name_scores = {n: scores(raw1, name_origin=n) for n in names}

# Anglo vs Arabic (largest gap)
obs, lo, hi = boot_diff(name_scores['Arabic'], name_scores['Anglo'])
print(f"  Arabic - Anglo: {obs:+.3f}  [{lo:+.3f}, {hi:+.3f}]")
results['s1_name_arabic_vs_anglo'] = {'obs': obs, 'ci95_lo': lo, 'ci95_hi': hi}

obs, lo, hi = boot_diff(name_scores['Latino'], name_scores['Anglo'])
print(f"  Latino - Anglo: {obs:+.3f}  [{lo:+.3f}, {hi:+.3f}]")
results['s1_name_latino_vs_anglo'] = {'obs': obs, 'ci95_lo': lo, 'ci95_hi': hi}

# ══════════════════════════════════════════════════════════════════════════
# STUDY 2: Prestige vs Country effects
# ══════════════════════════════════════════════════════════════════════════
print("\n=== STUDY 2: Prestige vs Country Effects ===")

hi_p = scores(raw2, prestige='high')
lo_p = scores(raw2, prestige='low')
obs, lo, hi = boot_diff(hi_p, lo_p)
print(f"  Prestige (high-low): {obs:+.3f}  [{lo:+.3f}, {hi:+.3f}]")
results['s2_prestige_effect'] = {'obs': obs, 'ci95_lo': lo, 'ci95_hi': hi}

dev_c = scores(raw2, country_dev='developed')
dvl_c = scores(raw2, country_dev='developing')
obs, lo, hi = boot_diff(dev_c, dvl_c)
print(f"  Country (dev-dvlp):  {obs:+.3f}  [{lo:+.3f}, {hi:+.3f}]")
results['s2_country_effect'] = {'obs': obs, 'ci95_lo': lo, 'ci95_hi': hi}

# UNAM vs FSU (confound-breaking contrast)
unam = scores(raw2, inst_label='UNAM')
fsu  = scores(raw2, inst_label='Framingham')
obs, lo, hi = boot_diff(unam, fsu)
print(f"  UNAM vs FSU:         {obs:+.3f}  [{lo:+.3f}, {hi:+.3f}]  (prestige>country?)")
results['s2_unam_vs_fsu'] = {'obs': obs, 'ci95_lo': lo, 'ci95_hi': hi}

# Per-model prestige and country effects
print("\n  Per-model effects:")
results['s2_by_model'] = {}
for model in models1:
    hi_m = scores(raw2, model=model, prestige='high')
    lo_m = scores(raw2, model=model, prestige='low')
    obs_p, lo_p2, hi_p2 = boot_diff(hi_m, lo_m)
    dev_m = scores(raw2, model=model, country_dev='developed')
    dvl_m = scores(raw2, model=model, country_dev='developing')
    obs_c, lo_c, hi_c = boot_diff(dev_m, dvl_m)
    print(f"  {model:<22}  Prestige: {obs_p:+.3f} [{lo_p2:+.3f},{hi_p2:+.3f}]  "
          f"Country: {obs_c:+.3f} [{lo_c:+.3f},{hi_c:+.3f}]")
    results['s2_by_model'][model] = {
        'prestige': {'obs': obs_p, 'ci95_lo': lo_p2, 'ci95_hi': hi_p2},
        'country':  {'obs': obs_c, 'ci95_lo': lo_c,  'ci95_hi': hi_c},
    }

# ══════════════════════════════════════════════════════════════════════════
# Domain-level Study 2
# ══════════════════════════════════════════════════════════════════════════
print("\n=== STUDY 2: Domain-Level Prestige vs Country ===")
domains = ['scholarship', 'hiring', 'credit', 'health', 'public_policy']
results['s2_by_domain'] = {}
for dom in domains:
    hi_d  = scores(raw2, domain=dom, prestige='high')
    lo_d  = scores(raw2, domain=dom, prestige='low')
    dev_d = scores(raw2, domain=dom, country_dev='developed')
    dvl_d = scores(raw2, domain=dom, country_dev='developing')
    obs_p, lp, hp = boot_diff(hi_d, lo_d)
    obs_c, lc, hc = boot_diff(dev_d, dvl_d)
    print(f"  {dom:<15}  P: {obs_p:+.3f} [{lp:+.3f},{hp:+.3f}]  "
          f"C: {obs_c:+.3f} [{lc:+.3f},{hc:+.3f}]")
    results['s2_by_domain'][dom] = {
        'prestige': {'obs': obs_p, 'ci95_lo': lp, 'ci95_hi': hp},
        'country':  {'obs': obs_c, 'ci95_lo': lc, 'ci95_hi': hc},
    }

# ── Save ──────────────────────────────────────────────────────────────────
out = 'C:/Users/HP/Documents/sesgo_geografico_llm/bootstrap_results.json'
with open(out, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {out}")

# ── Summary interpretation ─────────────────────────────────────────────────
print("\n=== INTERPRETATION SUMMARY ===")
g = results['s1_gradient_T1_T5']
if g['ci95_lo'] > 0:
    print(f"  Institution gradient {g['obs']:+.3f}: CI ENTIRELY POSITIVE [{g['ci95_lo']:+.3f},{g['ci95_hi']:+.3f}] -> significant")
else:
    print(f"  Institution gradient {g['obs']:+.3f}: CI crosses zero -> not significant at 95%")

p = results['s2_prestige_effect']
if p['ci95_lo'] > 0:
    print(f"  Prestige effect {p['obs']:+.3f}: CI ENTIRELY POSITIVE [{p['ci95_lo']:+.3f},{p['ci95_hi']:+.3f}] -> significant")
else:
    print(f"  Prestige effect {p['obs']:+.3f}: CI crosses zero")

c = results['s2_country_effect']
if c['ci95_lo'] > 0:
    print(f"  Country effect {c['obs']:+.3f}: CI ENTIRELY POSITIVE [{c['ci95_lo']:+.3f},{c['ci95_hi']:+.3f}] -> significant")
else:
    print(f"  Country effect {c['obs']:+.3f}: CI crosses zero")

u = results['s2_unam_vs_fsu']
if u['ci95_lo'] > 0:
    print(f"  UNAM>FSU {u['obs']:+.3f}: CI ENTIRELY POSITIVE [{u['ci95_lo']:+.3f},{u['ci95_hi']:+.3f}] -> prestige confirmed")
elif u['ci95_hi'] < 0:
    print(f"  FSU>UNAM: country effect wins")
else:
    print(f"  UNAM vs FSU {u['obs']:+.3f}: CI crosses zero -> ambiguous")
