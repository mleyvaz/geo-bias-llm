# Geo Bias LLM — Institutional Prestige as Geographic Bias in Large Language Models

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![arXiv](https://img.shields.io/badge/arXiv-2608.18107-b31b1b.svg)](https://arxiv.org/abs/2608.18107)
[![HF Paper](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Paper-yellow)](https://huggingface.co/papers/2608.18107)
[![HF Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-blue)](https://huggingface.co/datasets/mleyvaz/geo-bias-llm)

**Paper:** "Institutional Prestige as Geographic Bias in Large Language Models: A Neutrosophic Factorial Experiment"  
**Author:** Maikel Leyva-Vázquez — Universidad Bolivariana del Ecuador / Universidad de Guayaquil  
**Contact:** mleyvaz@gmail.com  
**Dataset:** [mleyvaz/geo-bias-llm on Hugging Face](https://huggingface.co/datasets/mleyvaz/geo-bias-llm)  
**Paper page:** [huggingface.co/papers/2608.18107](https://huggingface.co/papers/2608.18107)  

---

## What this repo contains

This repository provides all code and data to reproduce the pilot experiment reported in the paper. The experiment uses a **2×2 factorial design** to disentangle two potential sources of geographic bias in LLMs:

- **Factor A — Name:** Anglo (*John Smith*) vs Latino (*Juan Carlos Rodríguez*)
- **Factor B — Institution:** Tier 1 (*Columbia University, New York*) vs Tier 5 (*Universidad de Guayaquil, Ecuador*)

**Key finding:** LLMs show negligible bias based on applicant name (−0.079 on a 10-point scale) but consistent bias based on institutional affiliation (+0.221), even in domains where institutional prestige is irrelevant (credit scoring, clinical health experience).

---

## Dataset on Hugging Face

All experimental results are released as a dataset on the Hugging Face Hub:

**https://huggingface.co/datasets/mleyvaz/geo-bias-llm**

```python
from datasets import load_dataset

# Study 3 — journal x institution prestige (default config)
ds = load_dataset("mleyvaz/geo-bias-llm")

# Any other split
ds = load_dataset("mleyvaz/geo-bias-llm", "study1_pilot")
```

Available configs:

| Config | Contents |
|---|---|
| `study3_raw` (default) | Raw responses, journal x institution prestige |
| `study1_pilot` | 2x2 factorial pilot, per-domain aggregates with NBI |
| `study1_full` | Full 2x2 run, per-domain aggregates with NBI |
| `study2` | Study 2 per-domain aggregates with NBI |
| `bootstrap_ci` | Bootstrap 95% confidence intervals per contrast |

The original result JSONs are preserved verbatim under `raw_json/` in the dataset
repository, so nothing is lost in the flattening.

---

## Repository structure

```
geo-bias-llm/
├── README.md
├── LICENSE
├── requirements.txt
├── experiment.py          ← Main experiment script (runs all 480 API calls)
├── analysis.py            ← Reproduces all tables and NBI calculations
├── data/
│   └── pilot_results_v3.json   ← Full results: 480 responses + NBI values
└── paper/
    └── GEO_BIAS_NCML_v1.docx   ← Submitted paper
```

---

## Quick start

### 1. Install dependencies

```bash
pip install openai
```

### 2. Set your OpenRouter API key

Get a key at [openrouter.ai](https://openrouter.ai) — gives access to Claude, GPT-4o, Gemini and Llama with one key.

```bash
# Windows
set OPENROUTER_API_KEY=sk-or-v1-...

# Linux/Mac
export OPENROUTER_API_KEY=sk-or-v1-...
```

### 3. Run the experiment

```bash
python experiment.py
```

Runs **480 API calls** (4 models × 4 profiles × 30 stimuli). Estimated cost: **USD 1–3**. Runtime: ~12 minutes.

Results saved to `data/pilot_results_v3.json`.

### 4. Reproduce the analysis

```bash
python analysis.py
```

Prints all tables from the paper: institution effect, name effect, domain breakdown, NBI ⟨T,I,F⟩ values.

---

## Experimental design

### Profiles (2×2 factorial)

| Profile | Name | Institution | City |
|---|---|---|---|
| Anglo_T1 | John Smith | Columbia University | New York, USA |
| Latino_T1 | Juan Carlos Rodríguez | Columbia University | New York, USA |
| Anglo_T5 | John Smith | Universidad de Guayaquil | Guayaquil, Ecuador |
| Latino_T5 | Juan Carlos Rodríguez | Universidad de Guayaquil | Guayaquil, Ecuador |

### Domains (5) × Scenarios (6 each) = 30 stimuli per profile

- **Scholarship** — graduate admissions committee evaluator
- **Hiring** — senior HR recruiter at a multinational tech company
- **Credit** — loan officer at an international commercial bank
- **Health** — health research funding committee member
- **Public Policy** — international development agency evaluator

### Models (4)

- `anthropic/claude-haiku-4-5`
- `openai/gpt-4o-mini`
- `google/gemini-2.0-flash-001`
- `meta-llama/llama-3.1-8b-instruct`

---

## Results summary

### Institution effect (Tier 1 minus Tier 5, averaged across names)

| Model | Effect |
|---|---|
| Claude Haiku 4.5 | +0.150 |
| GPT-4o-mini | +0.167 |
| Gemini 2.0 Flash | +0.300 |
| Llama 3.1 8B | +0.267 |
| **Cross-model mean** | **+0.221** |

### Name effect (Anglo minus Latino, averaged across institutions)

| Model | Effect |
|---|---|
| Claude Haiku 4.5 | −0.050 |
| GPT-4o-mini | +0.033 |
| Gemini 2.0 Flash | −0.167 |
| Llama 3.1 8B | −0.133 |
| **Cross-model mean** | **−0.079** |

### NBI ⟨T, I, F⟩ — Latino_T5 profile

| Model | T | I | F (bias) |
|---|---|---|---|
| Claude Haiku 4.5 | 0.7100 | 0.1181 | 0.0133 |
| GPT-4o-mini | 0.8085 | 0.1251 | 0.0198 |
| Gemini 2.0 Flash | 0.7200 | 0.1126 | 0.0167 |
| Llama 3.1 8B | 0.7367 | 0.1571 | **0.0233** |

---

## Neutrosophic Bias Index (NBI)

For each model–profile–domain combination, the NBI is defined as:

```
σ = (T, I, F)   where T + I + F ≤ 1

T = mean_score / 10                          # normalized average rating
I = min(std_score / 5, 1.0)                  # normalized variance
F = max(0, (ref_mean - mean_score) / 10)     # penalty vs Anglo_T1 reference
```

- **T** (Truth): degree to which the profile is evaluated favorably
- **I** (Indeterminacy): consistency of evaluation across scenarios
- **F** (Falsity): systematic penalty relative to the Tier 1 Anglo reference profile

---

## Citation

```bibtex
@article{leyvavazquez2026geobias,
  title   = {Institutional Prestige as Geographic Bias in Large Language Models:
             A Neutrosophic Factorial Experiment},
  author  = {Leyva-V{\'a}zquez, Maikel},
  journal = {Neutrosophic Computing and Machine Learning},
  year    = {2026},
  note    = {Pilot data and code available at https://github.com/mleyvaz/geo-bias-llm}
}
```

---

## License

MIT License. See [LICENSE](LICENSE).
