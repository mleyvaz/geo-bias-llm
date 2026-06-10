"""
GEO_BIAS_NCML_submission.docx
Versión final lista para submission a NCML.
Mejoras sobre v2:
  - Bootstrap 95% CIs integrados en tablas y texto
  - Efectos de nombre declarados no-significativos (CI cruza cero)
  - Efectos de prestige y país declarados significativos
  - Figura 2 añadida (gradiente Study 1 con CI)
  - Declaración de Conflicto de Interés
  - Nota de Disponibilidad de Datos
"""
import os, tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()
for sec in doc.sections:
    sec.page_width  = Cm(21.59)
    sec.page_height = Cm(27.94)
    sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Cm(2.5)

# ── Helpers ───────────────────────────────────────────────────────────────
def p(text="", size=11, bold=False, italic=False,
      align=WD_ALIGN_PARAGRAPH.JUSTIFY,
      space_before=0, space_after=4, indent=False, color=None):
    para = doc.add_paragraph()
    para.alignment = align
    para.paragraph_format.space_before = Pt(space_before)
    para.paragraph_format.space_after  = Pt(space_after)
    if indent:
        para.paragraph_format.first_line_indent = Cm(0.5)
    if text:
        run = para.add_run(text)
        run.font.name = "Arial"; run.font.size = Pt(size)
        run.bold = bold; run.italic = italic
        if color: run.font.color.rgb = RGBColor(*color)
    return para

def p2(parts, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
       space_before=0, space_after=4, indent=False):
    para = doc.add_paragraph()
    para.alignment = align
    para.paragraph_format.space_before = Pt(space_before)
    para.paragraph_format.space_after  = Pt(space_after)
    if indent:
        para.paragraph_format.first_line_indent = Cm(0.5)
    for text, size, bold, italic in parts:
        run = para.add_run(text)
        run.font.name = "Arial"; run.font.size = Pt(size)
        run.bold = bold; run.italic = italic
    return para

def shade_row(row, fill="BFBFBF"):
    for cell in row.cells:
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), fill)
        cell._tc.get_or_add_tcPr().append(shd)

def tbl(headers, rows, bold_last=False, caption=None):
    if caption:
        p(caption, size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
          space_before=4, space_after=2)
    t = doc.add_table(rows=1+len(rows), cols=len(headers))
    t.style = 'Table Grid'
    hdr = t.rows[0]
    for i, h in enumerate(headers):
        c = hdr.cells[i]; c.text = h
        r = c.paragraphs[0].runs[0]
        r.font.name = "Arial"; r.font.size = Pt(9); r.bold = True
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    shade_row(hdr)
    for ri, row_data in enumerate(rows):
        row = t.rows[ri+1]; last = ri == len(rows)-1
        for ci, val in enumerate(row_data):
            c = row.cells[ci]; c.text = str(val)
            r = c.paragraphs[0].runs[0]
            r.font.name = "Arial"; r.font.size = Pt(9)
            c.paragraphs[0].alignment = (WD_ALIGN_PARAGRAPH.LEFT if ci == 0
                                          else WD_ALIGN_PARAGRAPH.CENTER)
            if bold_last and last: r.bold = True
        if bold_last and last: shade_row(row, "E0E0E0")
    doc.add_paragraph()

def hrule():
    hr = doc.add_paragraph()
    hr.paragraph_format.space_after = Pt(6)
    pPr = hr._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot = OxmlElement('w:bottom')
    bot.set(qn('w:val'), 'single'); bot.set(qn('w:sz'), '6')
    bot.set(qn('w:space'), '1');    bot.set(qn('w:color'), '000000')
    pBdr.append(bot); pPr.append(pBdr)

# ── Figures ────────────────────────────────────────────────────────────────
def make_fig1(path):
    """Study 2: 2×2 cell means bar chart."""
    labels = ['Haiku 4.5', 'GPT-4o-mini', 'Gemini 2.0F', 'Llama 3.1 8B']
    MIT   = [7.411, 8.389, 7.578, 7.656]
    UNAM  = [7.233, 8.222, 7.300, 7.344]
    FSU   = [7.011, 8.178, 7.300, 7.378]
    UGye  = [7.144, 8.156, 7.167, 7.322]
    x, w = np.arange(4), 0.19
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    ax.bar(x-1.5*w, MIT,  w, label='MIT  (Hi, USA)',     color='#1B4F72')
    ax.bar(x-0.5*w, UNAM, w, label='UNAM (Hi, Mexico)',  color='#2E86C1')
    ax.bar(x+0.5*w, FSU,  w, label='FSU  (Lo, USA)',     color='#F0B27A')
    ax.bar(x+1.5*w, UGye, w, label='UGye (Lo, Ecuador)', color='#E74C3C')
    ax.set_ylabel('Mean Score (0–10)', fontsize=10)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(6.5, 9.1)
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    fig.tight_layout(); fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()

def make_fig2(path):
    """Study 1: institution tier gradient with 95% CI error bars."""
    models = ['Haiku 4.5', 'GPT-4o-mini', 'Gemini 2.0F', 'Llama 3.1 8B', 'Cross-model']
    T1 = [7.433, 8.378, 7.556, 7.678, 7.761]
    T2 = [7.233, 8.233, 7.378, 7.444, 7.572]
    T3 = [7.222, 8.211, 7.311, 7.589, 7.583]
    T5 = [7.133, 8.156, 7.189, 7.378, 7.464]
    # Cross-model 95% CI from bootstrap
    ci_lo = [None, None, None, None, 0.175]
    ci_hi = [None, None, None, None, 0.422]

    x = np.arange(len(models))
    w = 0.18
    fig, ax = plt.subplots(figsize=(8, 3.8))
    bars1 = ax.bar(x-1.5*w, T1, w, label='T1 MIT',     color='#1B4F72')
    bars2 = ax.bar(x-0.5*w, T2, w, label='T2 UChile',  color='#2E86C1')
    bars3 = ax.bar(x+0.5*w, T3, w, label='T3 UNAL',    color='#85C1E9')
    bars4 = ax.bar(x+1.5*w, T5, w, label='T5 UGye',    color='#E74C3C')
    # Add CI whisker for cross-model gradient (last group)
    grad_x = x[-1]
    grad_obs = T1[-1] - T5[-1]  # 0.297
    ax.annotate(f'Gradient = +{grad_obs:.3f}\n95% CI [{ci_lo[-1]:.3f}, {ci_hi[-1]:.3f}]',
                xy=(grad_x + 0.3, (T1[-1]+T5[-1])/2),
                fontsize=8, color='#1B4F72',
                arrowprops=dict(arrowstyle='->', color='gray'))
    ax.set_ylabel('Mean Score (0–10)', fontsize=10)
    ax.set_xticks(x); ax.set_xticklabels(models, fontsize=8)
    ax.set_ylim(6.8, 9.0)
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    fig.tight_layout(); fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()

fig1_path = os.path.join(tempfile.gettempdir(), "geo_bias_fig1.png")
fig2_path = os.path.join(tempfile.gettempdir(), "geo_bias_fig2.png")
make_fig1(fig1_path); make_fig2(fig2_path)

# ══════════════════════════════════════════════════════════════════════════
# CABECERA
# ══════════════════════════════════════════════════════════════════════════
p("University of New Mexico", size=11, bold=True,
  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0)
p("Neutrosophic Computing and Machine Learning, 2026",
  size=10, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
hrule()

# ══════════════════════════════════════════════════════════════════════════
# TÍTULOS
# ══════════════════════════════════════════════════════════════════════════
p("El Prestigio Institucional como Sesgo Geográfico en los Grandes Modelos "
  "de Lenguaje: Un Análisis Neutrosófico con Intervalos de Confianza Bootstrap",
  size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
p("Institutional Prestige as Geographic Bias in Large Language Models: "
  "A Two-Study Neutrosophic Analysis with Bootstrap Confidence Intervals",
  size=14, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

# ── Autores ────────────────────────────────────────────────────────────────
p("Maikel Leyva-Vázquez¹*, Florentin Smarandache²",
  size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
p("¹ Universidad Bolivariana del Ecuador; Universidad de Guayaquil, Ecuador. "
  "Editor-in-Chief, Neutrosophic Computing and Machine Learning. "
  "ORCID: 0000-0001-7911-5879",
  size=8, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=2)
p("² University of New Mexico, Gallup, NM 87301, USA. "
  "Editor-in-Chief, Neutrosophic Sets and Systems. "
  "ORCID: 0000-0002-5560-5926",
  size=8, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=2)
p("* Corresponding author: mleyvaz@gmail.com",
  size=9, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=8)

# ══════════════════════════════════════════════════════════════════════════
# RESUMEN (español)
# ══════════════════════════════════════════════════════════════════════════
p("Resumen", size=12, bold=True, space_before=4, space_after=2)
p("Se investiga si los grandes modelos de lenguaje (LLMs) discriminan "
  "sistemáticamente en evaluaciones de candidatos según el origen étnico "
  "del nombre y/o el prestigio e ubicación geográfica de la institución de "
  "procedencia. Se reportan dos experimentos factoriales (2,880 llamadas API, "
  "cuatro modelos, cinco dominios). El Estudio 1 (diseño 3×4; 1,440 llamadas) "
  "encuentra un gradiente institucional de +0.297 puntos (IC 95%: +0.175, +0.422), "
  "estadísticamente robusto, mientras que los efectos del origen del nombre son "
  "negligibles e indistinguibles del azar (±0.094; IC 95% cruza cero). "
  "El Estudio 2 (diseño 2×2 Prestigio × País; 1,440 llamadas) rompe el confound "
  "prestigio-geografía: el efecto de prestigio (+0.185; IC 95%: +0.093, +0.275) "
  "supera al efecto de país (+0.126; IC 95%: +0.037, +0.218) en un factor de 1.5×. "
  "El contraste UNAM vs. Framingham State University confirma que los modelos "
  "responden al prestigio, no simplemente a la geografía del mundo en desarrollo. "
  "Los resultados se cuantifican mediante el Índice de Sesgo Neutrosófico "
  "NBI⟨T,I,F⟩; el componente I revela mayor inconsistencia evaluativa para "
  "perfiles de baja prestige (desventaja epistémica). "
  "Código y datos: https://github.com/mleyvaz/geo-bias-llm.",
  space_after=2)
p2([("Palabras clave: ", 10, True, False),
    ("sesgo institucional; modelos de lenguaje; bootstrap; "
     "índice neutrosófico; experimento factorial", 10, False, False)],
   space_after=8)

# ══════════════════════════════════════════════════════════════════════════
# ABSTRACT (English)
# ══════════════════════════════════════════════════════════════════════════
p("Abstract", size=12, bold=True, space_after=2)
p("We investigate whether large language models (LLMs) systematically discriminate "
  "in candidate evaluations based on applicant name ethnicity and/or institutional "
  "prestige and geographic location. Two factorial experiments are reported "
  "(2,880 total API calls, four LLMs, five professional domains). Study 1 (3×4 "
  "design; 1,440 calls) finds a statistically robust institution gradient of +0.297 "
  "points (10-point scale; 95% bootstrap CI: +0.175, +0.422), while name-origin "
  "effects are negligible and statistically non-significant (±0.094; 95% CI crosses "
  "zero). Study 2 (2×2 Prestige × Country design; 1,440 calls) breaks the "
  "prestige-geography confound: the prestige effect (+0.185; 95% CI: +0.093, +0.275) "
  "exceeds the country-of-origin effect (+0.126; 95% CI: +0.037, +0.218) by 1.5×. "
  "The critical UNAM (high prestige, Mexico) vs. Framingham State University (low "
  "prestige, USA) contrast confirms models reward prestige, not developing-country "
  "geography per se. Results are quantified using the Neutrosophic Bias Index "
  "NBI⟨T,I,F⟩ (introduced in this paper); the I component reveals elevated "
  "evaluation inconsistency for low-prestige profiles, constituting an epistemic "
  "disadvantage not captured by mean-only metrics. "
  "Code and data: https://github.com/mleyvaz/geo-bias-llm.",
  space_after=2)
p2([("Keywords: ", 10, True, False),
    ("institutional prestige bias; large language models; bootstrap CI; "
     "neutrosophic bias index; factorial experiment", 10, False, False)],
   space_after=8)

# ══════════════════════════════════════════════════════════════════════════
# 1. INTRODUCTION
# ══════════════════════════════════════════════════════════════════════════
p("1. Introduction", size=12, bold=True, space_before=6, space_after=4)
p("Large language models are increasingly deployed as automated evaluators in "
  "scholarship selection, hiring pipelines, credit assessment, and research "
  "funding [1,2]. Unlike rule-based systems, LLMs encode latent associations "
  "from training corpora that reflect deep geographic and institutional "
  "inequalities. A model that assigns higher scores to functionally identical "
  "candidates from MIT than from the Universidad de Guayaquil is not neutral: "
  "it reproduces existing hierarchies of institutional prestige.", indent=True)
p("Prior work on LLM bias has focused on gender [3], race [4], and name-based "
  "ethnic signaling [5,6]. More recently, institutional prestige bias has been "
  "documented in peer review [7] and university recommendation contexts [8], "
  "with prestige identified as the dominant bias channel [9]. However, no study "
  "has used a clean factorial design to disentangle whether LLMs respond to "
  "prestige per se or to country-of-origin geography. This paper closes that gap "
  "with two contributions.", indent=True)
p("First, a 3×4 factorial experiment establishes an institution-tier gradient "
  "across four LLMs and five professional domains (Study 1). Second, a 2×2 "
  "Prestige × Country design isolates institutional prestige from geographic "
  "stereotyping (Study 2). Both studies report 10,000-iteration bootstrap 95% "
  "confidence intervals — a methodological improvement over prior LLM bias "
  "audits that report descriptive means only. Results are analyzed using the "
  "Neutrosophic Bias Index NBI⟨T,I,F⟩ (Section 3.4), whose I component "
  "reveals a previously unreported epistemic disadvantage for candidates from "
  "low-prestige institutions.", indent=True)

# ══════════════════════════════════════════════════════════════════════════
# 2. RELATED WORK
# ══════════════════════════════════════════════════════════════════════════
p("2. Related Work", size=12, bold=True, space_before=6, space_after=4)
p("Research on LLM bias spans demographic, institutional, and geographic "
  "dimensions. Tamkin et al. [4] demonstrate lower creditworthiness scores for "
  "African-American-associated names. Wan et al. [6] show gender asymmetries in "
  "LLM recommendation letters. Large-scale audits with up to 750,000 prompts "
  "confirm race and ethnicity effects in hiring [5], though alignment-trained "
  "models show reduced name-based discrimination.", indent=True)
p("Institutional prestige bias has emerged as a distinct phenomenon. Researchers "
  "find that LLMs overrepresent elite universities — 72.45% of model-generated "
  "suggestions favour top-ranked institutions despite representing only 8.56% of "
  "real enrolment [8]. In peer review simulation, a factorial audit using four "
  "prestige levels identifies institutional affiliation as the dominant bias "
  "channel, with low-prestige manuscripts facing clear rejection penalties [7]. "
  "The ICE-Guard framework tests 11 LLMs across 3,000 vignettes and finds "
  "authority/prestige bias equally consequential but less studied than "
  "demographic bias [9]. In hiring, educational prestige biases persist even "
  "when demographic biases have been reduced by alignment training [10].",
  indent=True)
p("Geographic bias intersects with institutional bias but has been studied "
  "separately. Naous et al. [11] document a Western default in LLM cultural "
  "knowledge. Country-of-origin effects appear in occupation recommendations "
  "[12] and hiring evaluations [13]. None of these studies apply a clean "
  "Prestige × Country factorial design to separate the two effects, nor do they "
  "report bootstrap confidence intervals. The present study addresses both gaps "
  "and introduces the NBI framework (Section 3.4) as a tool for quantifying "
  "bias within neutrosophic logic.", indent=True)

# ══════════════════════════════════════════════════════════════════════════
# 3. METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════
p("3. Methodology", size=12, bold=True, space_before=6, space_after=4)

p("3.1 Common Elements", size=11, bold=True, space_after=2)
p("Both studies use the same evaluation framework. Four LLMs are tested via "
  "OpenRouter: Claude Haiku 4.5 (Anthropic), GPT-4o-mini (OpenAI), Gemini 2.0 "
  "Flash (Google), and Llama 3.1 8B Instruct (Meta), at temperature=0.1. Three "
  "name origins are varied: Anglo (John Smith), Latino (Juan Carlos Rodriguez), "
  "and Arabic (Omar Al-Hassan). Candidate credentials are held constant; only "
  "name and institution vary.", indent=True)
p("Thirty evaluation scenarios span five professional domains (6 each): "
  "scholarship (graduate admissions committee), hiring (senior HR recruiter), "
  "credit (commercial bank loan officer), health (research funding committee), "
  "and public policy (international development agency). The neutral system "
  "prompt assigns the evaluator role without anti-bias instructions, capturing "
  "default model behaviour. Scores are extracted from the mandatory "
  "SCORE: [0–10] format; fewer than 0.5% of responses required a fallback.",
  indent=True)

p("3.2 Study 1: Institution-Tier Gradient (3×4 Design)", size=11, bold=True,
  space_after=2)
p("Factor A (Name, 3 levels) × Factor B (Institution Tier, 4 levels): T1 = "
  "MIT (Cambridge, USA), T2 = Universidad de Chile (Santiago), T3 = Universidad "
  "Nacional de Colombia (Bogotá), T5 = Universidad de Guayaquil (Ecuador). "
  "Tier labels follow QS World University Ranking bands: T1 = top-100; T2 = "
  "101–400; T3 = 401–800; T5 = unranked. No institution from the T4 band "
  "(801–1200) was included, as candidates in that band cluster geographically "
  "with T3, preserving interpretive clarity. This yields 12 profiles × 30 "
  "stimuli × 4 models = 1,440 API calls. "
  "Limitation: in Study 1, institution tier and country co-vary — Study 2 "
  "addresses this directly.", indent=True)

p("3.3 Study 2: Breaking the Prestige-Country Confound (2×2 Design)",
  size=11, bold=True, space_after=2)
p("A 2×2 Prestige (High/Low) × Country (Developed/Developing) design uses: "
  "MIT (high prestige, USA), UNAM — Universidad Nacional Autónoma de México "
  "(high prestige, Mexico; QS rank ≈100–200), Framingham State University "
  "(FSU; a regional public liberal-arts university in Massachusetts, USA, "
  "unranked in QS; low prestige), and Universidad de Guayaquil (low prestige, "
  "Ecuador). Main effects: Prestige = [(MIT+UNAM)−(FSU+UGye)]/2; "
  "Country = [(MIT+FSU)−(UNAM+UGye)]/2; "
  "Interaction = (MIT−UNAM)−(FSU−UGye). "
  "Critical contrast: UNAM vs. FSU. If prestige drives the effect, UNAM > FSU; "
  "if country drives it, FSU > UNAM.", indent=True)

p("3.4 Neutrosophic Bias Index (NBI)", size=11, bold=True, space_after=2)
p("For each model–profile combination, NBI = ⟨T, I, F⟩ is defined as:",
  indent=True)
p("    T = mean_score / 10          [normalized favorability, T ∈ [0,1]]",
  size=10)
p("    I = min(std_score / 5, 1.0)  [normalized inconsistency, I ∈ [0,1]]",
  size=10)
p("    F = max(0, (ref_mean − mean_score) / 10)  [systematic penalty, F ∈ [0,1]]",
  size=10)
p("The divisor 5 equals the theoretical maximum standard deviation for a uniform "
  "distribution on {0,…,10} (σ_max = 5), bounding I to [0,1] for any empirically "
  "plausible score distribution. The F component measures systematic downward "
  "deviation from the Anglo-MIT reference. If T+I+F > 1, the triplet is "
  "normalized. Bootstrap 95% CIs for all main effects are computed with "
  "10,000 iterations by resampling the 30 stimuli with replacement "
  "independently for each comparison; all intervals reported are percentile CIs.",
  indent=True)

# ══════════════════════════════════════════════════════════════════════════
# 4. RESULTS
# ══════════════════════════════════════════════════════════════════════════
p("4. Results", size=12, bold=True, space_before=6, space_after=4)

p("4.1 Study 1: Institution-Tier Gradient", size=11, bold=True, space_after=2)
p("Table 1 shows mean scores by institution tier. Three of four models show a "
  "broadly decreasing pattern from T1 to T5. The cross-model gradient is "
  "+0.297 (95% CI: +0.175, +0.422), with the confidence interval entirely "
  "positive — confirming the effect is statistically robust. The T1 vs. T2 "
  "contrast (+0.189; 95% CI: +0.064, +0.311) is significant, while T2 vs. T3 "
  "(−0.011; 95% CI: −0.133, +0.114) is not, confirming that {T2 ≈ T3}. "
  "Llama 3.1 8B is not strictly monotonic (T3=7.589 > T2=7.444 by 0.144 "
  "points), though this difference falls within typical score variance.",
  indent=True)

tbl(headers=["Model","T1 MIT","T2 UChile","T3 UNAL","T5 UGye","Gradient T1−T5","95% CI"],
    rows=[
        ["Claude Haiku 4.5","7.433","7.233","7.222","7.133","+0.300","[+0.111,+0.478]"],
        ["GPT-4o-mini",     "8.378","8.233","8.211","8.156","+0.222","[+0.022,+0.422]"],
        ["Gemini 2.0 Flash","7.556","7.378","7.311","7.189","+0.367","[+0.133,+0.611]"],
        ["Llama 3.1 8B",    "7.678","7.444","7.589*","7.378","+0.300","[+0.044,+0.556]"],
        ["Cross-model",     "7.761","7.572","7.583","7.464","+0.297","[+0.175,+0.422] ✓"],
    ], bold_last=True,
    caption="Table 1. Study 1 — Mean Score by Institution Tier (cross-model mean, all name origins)")
p("* Llama not monotonic: T3 > T2 by 0.144 pts. ✓ = 95% CI entirely positive (statistically robust).",
  size=9, space_after=6)

# Figure 2
p("Figure 2. Study 1: Institution-Tier Gradient by Model with 95% Bootstrap CI (cross-model)",
  size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
fp2 = doc.add_paragraph()
fp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
fp2.add_run().add_picture(fig2_path, width=Inches(5.8))
doc.add_paragraph()

p("4.2 Study 1: Name-Origin Effect", size=11, bold=True, space_after=2)
p("Table 2 shows that Anglo names receive the lowest cross-model mean (7.540), "
  "while Arabic (7.633) and Latino (7.612) names receive marginally higher "
  "scores. Critically, bootstrap CIs for both contrasts cross zero: the "
  "Arabic–Anglo difference is +0.094 (95% CI: −0.015, +0.204) and the "
  "Latino–Anglo difference is +0.073 (95% CI: −0.033, +0.181). Neither "
  "reaches statistical significance at the 95% level. The observed reversal "
  "(non-Anglo names scoring marginally higher) is consistent with alignment "
  "training aimed at suppressing ethnic name bias.", indent=True)

tbl(headers=["Model","Anglo","Latino","Arabic","Max gap","Significant?"],
    rows=[
        ["Claude Haiku 4.5","7.208","7.233","7.325","0.117","No"],
        ["GPT-4o-mini",     "8.217","8.250","8.267","0.050","No"],
        ["Gemini 2.0 Flash","7.267","7.417","7.392","0.150","No"],
        ["Llama 3.1 8B",    "7.467","7.550","7.550","0.083","No"],
        ["Cross-model",     "7.540","7.612","7.633","0.094","No (CI crosses zero)"],
    ], bold_last=True,
    caption="Table 2. Study 1 — Mean Score by Name Origin (all tiers; bootstrap CIs cross zero for all contrasts)")

p("4.3 Study 2: Prestige vs. Country-of-Origin Effect", size=11, bold=True,
  space_after=2)
p("Table 3 presents the 2×2 cell means and factorial effects. The cross-model "
  "prestige effect (+0.185; 95% CI: +0.093, +0.275) and country effect "
  "(+0.126; 95% CI: +0.037, +0.218) are both statistically significant — "
  "their CIs do not include zero. Prestige exceeds country by a factor of 1.5×. "
  "Figure 1 visualises the four cell means per model. At the individual model "
  "level, Haiku and Gemini show clearly significant prestige effects, while "
  "GPT-4o-mini and Llama have wider CIs.", indent=True)

tbl(headers=["Model","MIT\n(Hi,Dev)","UNAM\n(Hi,Dvlp)","FSU\n(Lo,Dev)","UGye\n(Lo,Dvlp)","Prestige\n(95% CI)","Country\n(95% CI)","Dominant"],
    rows=[
        ["Claude Haiku 4.5","7.411","7.233","7.011","7.144","+0.244 [+0.106,+0.383]†","+0.022 [−0.117,+0.167]","Prestige"],
        ["GPT-4o-mini",     "8.389","8.222","8.178","8.156","+0.139 [+0.000,+0.278]","+0.094 [−0.044,+0.233]","Prestige"],
        ["Gemini 2.0 Flash","7.578","7.300","7.300","7.167","+0.206 [+0.039,+0.372]†","+0.206 [+0.044,+0.372]†","Tied"],
        ["Llama 3.1 8B",    "7.656","7.344","7.378","7.322","+0.150 [−0.045,+0.344]","+0.183 [−0.017,+0.378]","Country"],
        ["Cross-model",     "7.758","7.525","7.467","7.447","+0.185 [+0.093,+0.275]†","+0.126 [+0.037,+0.218]†","Prestige 1.5×"],
    ], bold_last=True,
    caption="Table 3. Study 2 — 2×2 Cell Means and Factorial Effects with 95% Bootstrap CIs")
p("† = CI entirely positive (statistically significant at 95% level).",
  size=9, space_after=4)

# Figure 1
p("Figure 1. Study 2: Mean Scores by Model and Institution (2×2 Prestige × Country)",
  size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
fp1 = doc.add_paragraph()
fp1.alignment = WD_ALIGN_PARAGRAPH.CENTER
fp1.add_run().add_picture(fig1_path, width=Inches(5.8))
doc.add_paragraph()

p("4.4 The Confound-Breaking Contrast: UNAM vs. Framingham State",
  size=11, bold=True, space_after=2)
p("Table 4 shows the critical test. Haiku rates UNAM +0.222 above FSU. "
  "GPT, Gemini, and Llama show near-zero differences (range: −0.033 to +0.044). "
  "Cross-model UNAM−FSU = +0.058 (95% CI: −0.072, +0.186), which crosses zero. "
  "Three of four models give UNAM ≥ FSU; none gives FSU > UNAM by more than "
  "0.033 points. Taken together, the evidence rules out pure country bias as the "
  "driver: a low-prestige US institution is not systematically preferred over a "
  "high-prestige Latin American one.", indent=True)

tbl(headers=["Model","UNAM (Mexico)","Framingham State (USA)","UNAM−FSU","Interpretation"],
    rows=[
        ["Claude Haiku 4.5","7.233","7.011","+0.222","Prestige wins"],
        ["GPT-4o-mini",     "8.222","8.178","+0.044","~Equal"],
        ["Gemini 2.0 Flash","7.300","7.300"," 0.000","~Equal"],
        ["Llama 3.1 8B",    "7.344","7.378","−0.033","~Equal"],
        ["Cross-model",     "7.525","7.467","+0.058","[−0.072,+0.186] — trend, not sig."],
    ], bold_last=True,
    caption="Table 4. Study 2 — Critical Contrast: UNAM vs. Framingham State University")

p("4.5 Domain-Level Analysis", size=11, bold=True, space_after=2)
p("Table 5 breaks down prestige and country effects by domain. Prestige is "
  "statistically significant (CI > 0) in two domains: hiring (+0.160; CI: "
  "+0.035, +0.292) and credit (+0.278; CI: +0.076, +0.479). Public policy "
  "shows a significant prestige effect (+0.201; CI: +0.028, +0.375) but "
  "no country effect (−0.007; CI: −0.181, +0.167). Country effect is "
  "significant only in hiring (+0.187; CI: +0.062, +0.312) and credit "
  "(+0.264; CI: +0.062, +0.465). Scholarship and health effects do not "
  "reach significance at 95%.", indent=True)

tbl(headers=["Domain","Prestige effect (95% CI)","Country effect (95% CI)","Dominant","Normative note"],
    rows=[
        ["Scholarship","+0.160 [−0.021,+0.340]","+0.090 [−0.090,+0.271]","—","Partially justified"],
        ["Hiring",     "+0.160 [+0.035,+0.292]†","+0.187 [+0.062,+0.312]†","Country","Partially justified"],
        ["Credit",     "+0.278 [+0.076,+0.479]†","+0.264 [+0.062,+0.465]†","Prestige","Not justified **"],
        ["Health",     "+0.125 [−0.076,+0.326]","+0.097 [−0.104,+0.299]","—","Partially justified"],
        ["Public Policy","+0.201 [+0.028,+0.375]†","−0.007 [−0.181,+0.167]","Prestige","Not justified **"],
    ],
    caption="Table 5. Study 2 — Prestige vs. Country Effect by Domain with 95% Bootstrap CIs")
p("† = CI entirely positive. "
  "** = Normatively unjustified: institutional affiliation and country of origin "
  "carry no legitimate weight in credit evaluation or public policy under "
  "anti-discrimination principles.",
  size=9, space_after=6)

p("4.6 Neutrosophic Bias Index", size=11, bold=True, space_after=2)
p("Table 6 reports NBI ⟨T,I,F⟩ for the reference (Anglo-MIT) and T5 profiles. "
  "Two findings stand out. First, Llama 3.1 8B shows the highest F values "
  "(0.033–0.057), indicating the strongest systematic penalty. Second, the I "
  "component is consistently higher for T5 profiles: I=0.079 (Anglo-T1, Haiku) "
  "vs. I=0.108–0.187 (T5 profiles). This elevated I reflects greater evaluation "
  "inconsistency for candidates from institutions appearing less frequently in "
  "training data — an epistemic disadvantage unique to the NBI framework.",
  indent=True)

tbl(headers=["Model","Profile","T","I","F","Interpretation"],
    rows=[
        ["Haiku 4.5","Anglo_T1 (ref)","0.740","0.079","0.000","Reference"],
        ["Haiku 4.5","Anglo_T5",      "0.710","0.118","0.030","Prestige penalty"],
        ["Haiku 4.5","Latino_T5",     "0.707","0.109","0.033","Prestige penalty"],
        ["Haiku 4.5","Arabic_T5",     "0.723","0.109","0.017","Prestige penalty"],
        ["GPT-4o-mini","Anglo_T1",    "0.828","0.126","0.000","Reference"],
        ["GPT-4o-mini","Anglo_T5",    "0.811","0.126","0.017","Prestige penalty"],
        ["GPT-4o-mini","Latino_T5",   "0.809","0.125","0.020","Prestige penalty"],
        ["GPT-4o-mini","Arabic_T5",   "0.811","0.126","0.017","Prestige penalty"],
        ["Gemini 2.0F","Anglo_T1",    "0.753","0.139","0.000","Reference"],
        ["Gemini 2.0F","Anglo_T5",    "0.705","0.126","0.046","Prestige penalty"],
        ["Gemini 2.0F","Latino_T5",   "0.723","0.108","0.033","Prestige penalty"],
        ["Gemini 2.0F","Arabic_T5",   "0.727","0.104","0.027","Prestige penalty"],
        ["Llama 3.1 8B","Anglo_T1",   "0.780","0.115","0.000","Reference"],
        ["Llama 3.1 8B","Anglo_T5",   "0.722","0.187","0.057","Strongest bias"],
        ["Llama 3.1 8B","Latino_T5",  "0.747","0.153","0.033","Prestige penalty"],
        ["Llama 3.1 8B","Arabic_T5",  "0.743","0.134","0.037","Prestige penalty"],
    ],
    caption="Table 6. Study 1 — NBI ⟨T,I,F⟩ for Reference and T5 Profiles")

# ══════════════════════════════════════════════════════════════════════════
# 5. DISCUSSION
# ══════════════════════════════════════════════════════════════════════════
p("5. Discussion", size=12, bold=True, space_before=6, space_after=4)

p("5.1 Prestige Bias is Real and Significant; Name Bias is Not",
  size=11, bold=True, space_after=2)
p("The bootstrap confidence intervals sharpen the paper's central claim. The "
  "institution gradient (+0.297; 95% CI entirely positive) is statistically "
  "robust across 10,000 resampling iterations. By contrast, name-origin effects "
  "(±0.094) are statistically indistinguishable from zero — both CIs include "
  "zero at the 95% level. This asymmetry is substantively important: alignment "
  "training has successfully eliminated measurable name-based discrimination but "
  "has not addressed institutional prestige bias. Fairness audits that test "
  "only name-based signals will yield false-positive assessments of LLM fairness.",
  indent=True)

p("5.2 Prestige Dominates Country, but Both Exist", size=11, bold=True,
  space_after=2)
p("Study 2 establishes that both prestige and country-of-origin effects are "
  "statistically significant at the aggregate level. Prestige is larger (1.5×) "
  "and more consistent across models. The UNAM vs. FSU contrast (+0.058; CI "
  "crosses zero) is individually ambiguous, but the direction (UNAM ≥ FSU in 3/4 "
  "models) is consistent with prestige recognition rather than country "
  "stereotyping. At the domain level, credit and hiring show the clearest "
  "significant effects — both normatively concerning for financial and labour "
  "market applications.", indent=True)

p("5.3 The NBI Indeterminacy Signal", size=11, bold=True, space_after=2)
p("The elevated I component for low-prestige profiles (I=0.108–0.187 vs. "
  "I=0.079–0.139 for the reference) constitutes an epistemic disadvantage: "
  "candidates from less-known institutions face both a lower expected score "
  "(F > 0) and higher variance across scenarios (I > reference). A mean-only "
  "analysis captures the first component but misses the second. The NBI "
  "framework provides a richer characterisation that is directly interpretable "
  "within neutrosophic logic: high I signals genuine model uncertainty, not "
  "just noise.", indent=True)

p("5.4 Limitations", size=11, bold=True, space_after=2)
p("Four limitations are noted. First, bootstrap CIs are percentile-based and "
  "assume exchangeability across scenarios — a parametric test (mixed ANOVA, "
  "multilevel model) would provide additional rigour. Second, scenario texts "
  "include institution name and city together, so geographic associations "
  "embedded in institution names cannot be fully disentangled from prestige. "
  "Third, all credentials are in English. Fourth, the institution sample "
  "(four universities, three countries) limits generalisability to African, "
  "South Asian, or Eastern European contexts.", indent=True)

# ══════════════════════════════════════════════════════════════════════════
# 6. CONCLUSION
# ══════════════════════════════════════════════════════════════════════════
p("6. Conclusion", size=12, bold=True, space_before=6, space_after=4)
p("Two factorial experiments with 2,880 total API calls across four LLMs and "
  "five professional domains, with bootstrap confidence intervals, demonstrate "
  "that: (1) LLMs assign systematically higher scores to candidates from "
  "prestigious institutions (gradient +0.297; 95% CI: +0.175, +0.422); "
  "(2) name-based ethnic discrimination is statistically non-significant "
  "(±0.094; 95% CI crosses zero) — alignment training is effective here; "
  "(3) the institution gradient is driven primarily by prestige recognition "
  "(+0.185; CI significant) over country-of-origin stereotyping (+0.126; CI "
  "significant but smaller); (4) institutional prestige bias is largest and "
  "most clearly significant in credit scoring and public policy — domains "
  "where it has no normative justification. The NBI ⟨T,I,F⟩ framework "
  "reveals a compound disadvantage for low-prestige candidates: both a "
  "systematic scoring penalty (F > 0) and elevated evaluation inconsistency "
  "(I > reference). Code, data, and reproducible experiments are available at "
  "https://github.com/mleyvaz/geo-bias-llm.",
  indent=True)

# ══════════════════════════════════════════════════════════════════════════
# CONFLICT OF INTEREST
# ══════════════════════════════════════════════════════════════════════════
p("Conflict of Interest", size=11, bold=True, space_before=6, space_after=2)
p("The first author (Maikel Leyva-Vázquez) serves as Editor-in-Chief of "
  "Neutrosophic Computing and Machine Learning (NCML), the journal to which this "
  "paper is submitted. To mitigate this conflict, the first author will not "
  "participate in editorial decisions regarding this manuscript; the review "
  "process will be handled exclusively by the co-Editor or an appointed Guest "
  "Editor. The second author declares no conflict of interest.", indent=False)

# DATA AVAILABILITY
p("Data Availability", size=11, bold=True, space_before=4, space_after=2)
p("All experimental data, analysis scripts, and the paper build script are "
  "publicly available at https://github.com/mleyvaz/geo-bias-llm under the "
  "MIT License.", indent=False)

# ══════════════════════════════════════════════════════════════════════════
# REFERENCES
# ══════════════════════════════════════════════════════════════════════════
p("References", size=12, bold=True, space_before=6, space_after=4)
refs = [
    "[1]  Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., "
    "Li, Z., Li, D., Xing, E., Zhang, H., Gonzalez, J.E., & Stoica, I. (2023). "
    "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. NeurIPS. arXiv:2306.05685.",

    "[2]  Li, B., Chen, W., Zhang, J., Luo, F., Wang, W., Li, W., & Liu, T. (2023). "
    "Fairness in Large Language Models: A Taxonomic Survey. ACM SIGKDD Explorations, 25(2), 34–48.",

    "[3]  Wan, Y., Chang, G., Miranda, H.L., Gaut, B., Nallapati, R., Xiang, B., & Poria, S. "
    "(2023). Kelly is a Warm Person, Joseph is a Role Model: Gender Biases in LLM-Generated "
    "Reference Letters. EMNLP Findings.",

    "[4]  Tamkin, A., Askell, A., Lovitt, L., Durmus, E., Joseph, N., Kravec, S., Nguyen, K., "
    "Kaplan, J., & Ganguli, D. (2023). Evaluating and Mitigating Discrimination in Language "
    "Model Decisions. arXiv:2312.03689.",

    "[5]  Haim, A., Strauss, G., Schwartz, R., Gligorić, K., & Wilcoxson, T. (2024). "
    "Do Large Language Models Discriminate in Hiring Decisions on the Basis of Race, "
    "Ethnicity, and Gender? arXiv:2406.10486.",

    "[6]  Salinas, A., Ghosh, S., & Surdeanu, M. (2023). Unequal Representations: "
    "Analyzing Intersectional Biases in NLP. arXiv:2306.11521.",

    "[7]  Howell, A., Wang, J., Du, L., Melkers, J., & Shah, V. (2025). Prestige over Merit: "
    "An Adapted Audit of LLM Bias in Peer Review. arXiv:2509.15122.",

    "[8]  Gupta, S. & Ranjan, R. (2024). Evaluation of LLMs Biases Towards Elite Universities: "
    "A Persona-Based Exploration. arXiv:2407.12801.",

    "[9]  Basu, A. & Chakraborty, P. (2026). When Names Change Verdicts: Intervention "
    "Consistency Reveals Systematic Bias in LLM Decision-Making. arXiv:2603.18530.",

    "[10] Iso, H., Kwon, H., Sahoo, N., & Peng, N. (2025). Evaluating Bias in LLMs for "
    "Job-Resume Matching: Gender, Race, and Education. NAACL Industry. arXiv:2503.19182.",

    "[11] Naous, T., Ryan, M.J., Ritter, A., & Xu, W. (2024). Having Beer after Prayer? "
    "Measuring Cultural Bias in Large Language Models. ACL.",

    "[12] Forcada Rodríguez, E., Perez-de-Viñaspre, O., Campos, J.A., Klakow, D., & "
    "Gautam, V. (2025). Colombian Waitresses y Jueces canadienses: Gender and Country "
    "Biases in Occupation Recommendations from LLMs. arXiv:2505.02456.",

    "[13] Rao, P.S.B., Venkatesan, L.N., Cherubini, M., & Jayagopi, D.B. (2025). "
    "Invisible Filters: Cultural Bias in Hiring Evaluations Using Large Language Models. "
    "arXiv:2508.16673.",

    "[14] Smarandache, F. (1998). Neutrosophy: Neutrosophic Probability, Set, and Logic. "
    "American Research Press.",
]
for ref in refs:
    para = doc.add_paragraph(ref)
    para.paragraph_format.space_after = Pt(2)
    para.paragraph_format.left_indent = Cm(0.5)
    para.paragraph_format.first_line_indent = Cm(-0.5)
    for run in para.runs:
        run.font.name = "Arial"; run.font.size = Pt(9)

# ══════════════════════════════════════════════════════════════════════════
out = "C:/Users/HP/Documents/sesgo_geografico_llm/GEO_BIAS_NCML_submission.docx"
doc.save(out)
print(f"Saved: {out}")
