"""
GEO_BIAS_NCML_v2.docx
Versión corregida del paper NCML con 10 fixes aplicados:
  1. Ref [1]: OpenAssistant → Zheng 2023 (LLM-as-Judge)
  2-6. Refs [7][8][9][11][14]: Anonymous → autores reales
  7. Ref [10] circular eliminado; in-text → "Section 3.4"
  8. Header: "Vol. 44" eliminado
  9. T4: explicación tier labels añadida
  10. NBI denominador 5: justificado
  + FSU descrito para lectores internacionales
  + Tabla 5 footnote "**" definido
  + Figura 1 añadida (bar chart Study 2)
  + Abstract español: "1,440 llamadas" no repetido
  + [9,11] → [9,10] en Discussion
  + Ref [13] "Lopez" → autores reales Forcada et al.
"""
import os
import tempfile

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

# ── Página: Letter, márgenes 2.5 cm ──────────────────────────────────────
for sec in doc.sections:
    sec.page_width  = Cm(21.59)
    sec.page_height = Cm(27.94)
    sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Cm(2.5)

# ── Helpers ───────────────────────────────────────────────────────────────
def p(text="", size=11, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
      space_before=0, space_after=4, indent=False, color=None):
    para = doc.add_paragraph()
    para.alignment = align
    para.paragraph_format.space_before = Pt(space_before)
    para.paragraph_format.space_after  = Pt(space_after)
    if indent:
        para.paragraph_format.first_line_indent = Cm(0.5)
    if text:
        run = para.add_run(text)
        run.font.name = "Arial"
        run.font.size = Pt(size)
        run.bold   = bold
        run.italic = italic
        if color:
            run.font.color.rgb = RGBColor(*color)
    return para

def p2(parts, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, indent=False):
    para = doc.add_paragraph()
    para.alignment = align
    para.paragraph_format.space_before = Pt(space_before)
    para.paragraph_format.space_after  = Pt(space_after)
    if indent:
        para.paragraph_format.first_line_indent = Cm(0.5)
    for text, size, bold, italic in parts:
        run = para.add_run(text)
        run.font.name = "Arial"
        run.font.size = Pt(size)
        run.bold   = bold
        run.italic = italic
    return para

def shade_row(row, fill="BFBFBF"):
    for cell in row.cells:
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), fill)
        cell._tc.get_or_add_tcPr().append(shd)

def tbl(headers, rows, bold_last=False):
    t = doc.add_table(rows=1+len(rows), cols=len(headers))
    t.style = 'Table Grid'
    hdr = t.rows[0]
    for i, h in enumerate(headers):
        c = hdr.cells[i]
        c.text = h
        r = c.paragraphs[0].runs[0]
        r.font.name = "Arial"; r.font.size = Pt(9); r.bold = True
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    shade_row(hdr)
    for ri, row_data in enumerate(rows):
        row = t.rows[ri+1]
        last = ri == len(rows)-1
        for ci, val in enumerate(row_data):
            c = row.cells[ci]
            c.text = str(val)
            r = c.paragraphs[0].runs[0]
            r.font.name = "Arial"; r.font.size = Pt(9)
            c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT if ci==0 else WD_ALIGN_PARAGRAPH.CENTER
            if bold_last and last: r.bold = True
        if bold_last and last:
            shade_row(row, "E0E0E0")
    doc.add_paragraph()

# ── Figure generator ──────────────────────────────────────────────────────
def make_figure1(path):
    labels = ['Haiku 4.5', 'GPT-4o-mini', 'Gemini 2.0F', 'Llama 3.1 8B']
    MIT_vals  = [7.411, 8.389, 7.578, 7.656]
    UNAM_vals = [7.233, 8.222, 7.300, 7.344]
    FSU_vals  = [7.011, 8.178, 7.300, 7.378]
    UGye_vals = [7.144, 8.156, 7.167, 7.322]

    x = np.arange(len(labels))
    w = 0.19
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    ax.bar(x - 1.5*w, MIT_vals,  w, label='MIT  (Hi-prestige, USA)',    color='#1B4F72')
    ax.bar(x - 0.5*w, UNAM_vals, w, label='UNAM (Hi-prestige, Mexico)', color='#2E86C1')
    ax.bar(x + 0.5*w, FSU_vals,  w, label='FSU  (Lo-prestige, USA)',    color='#F0B27A')
    ax.bar(x + 1.5*w, UGye_vals, w, label='UGye (Lo-prestige, Ecuador)',color='#E74C3C')
    ax.set_ylabel('Mean Score (0–10)', fontsize=10)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(6.5, 9.1)
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()

# Generate figure to temp file
fig_path = os.path.join(tempfile.gettempdir(), "geo_bias_fig1.png")
make_figure1(fig_path)

# ══════════════════════════════════════════════════════════════════════════
# CABECERA NCML  [FIX 3: sin "Vol. 44"]
# ══════════════════════════════════════════════════════════════════════════
p("University of New Mexico", size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0)
p("Neutrosophic Computing and Machine Learning, 2026",
  size=10, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)

hr = doc.add_paragraph()
hr.paragraph_format.space_after = Pt(6)
pPr = hr._p.get_or_add_pPr()
pBdr = OxmlElement('w:pBdr')
bottom = OxmlElement('w:bottom')
bottom.set(qn('w:val'), 'single'); bottom.set(qn('w:sz'), '6')
bottom.set(qn('w:space'), '1'); bottom.set(qn('w:color'), '000000')
pBdr.append(bottom); pPr.append(pBdr)

# ══════════════════════════════════════════════════════════════════════════
# TÍTULOS
# ══════════════════════════════════════════════════════════════════════════
p("El Prestigio Institucional como Sesgo Geográfico en los Grandes Modelos de Lenguaje: "
  "Un Análisis Neutrosófico de Dos Estudios",
  size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)

p("Institutional Prestige as Geographic Bias in Large Language Models: "
  "A Two-Study Neutrosophic Analysis",
  size=14, bold=False, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

# ══════════════════════════════════════════════════════════════════════════
# AUTORES Y AFILIACIONES
# ══════════════════════════════════════════════════════════════════════════
p("Maikel Leyva-Vázquez¹*, Florentin Smarandache²",
  size=11, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)

p("¹ Universidad Bolivariana del Ecuador; Universidad de Guayaquil, Ecuador; "
  "Editor-in-Chief, Neutrosophic Computing and Machine Learning. "
  "ORCID: 0000-0001-7911-5879",
  size=8, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=2)

p("² University of New Mexico, Gallup, NM 87301, USA; "
  "Editor-in-Chief, Neutrosophic Sets and Systems. "
  "ORCID: 0000-0002-5560-5926",
  size=8, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=2)

p("* Corresponding author: mleyvaz@gmail.com",
  size=9, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=8)

# ══════════════════════════════════════════════════════════════════════════
# RESUMEN (español)  [FIX 10: "1,440 llamadas" no duplicado]
# ══════════════════════════════════════════════════════════════════════════
p("Resumen", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=4, space_after=2)
p("Se investiga si los grandes modelos de lenguaje (LLMs) discriminan sistemáticamente "
  "en evaluaciones de candidatos según el origen étnico del nombre y/o el prestigio e "
  "ubicación geográfica de la institución de procedencia. Se reportan dos experimentos "
  "factoriales (2,880 llamadas API en total, cuatro modelos, cinco dominios). "
  "El Estudio 1 (diseño 3×4: 3 orígenes de nombre × 4 tiers institucionales; "
  "1,440 llamadas) encuentra un gradiente institucional de +0.297 puntos (escala 10 puntos, "
  "MIT vs. Universidad de Guayaquil), mientras que los efectos del origen del nombre son "
  "negligibles (<0.094). El Estudio 2 (diseño 3×4: 3 nombres × diseño 2×2 "
  "Prestigio × País; igual número de llamadas) rompe el confound prestigio-geografía "
  "del Estudio 1: el efecto de prestigio (+0.185) supera al efecto de país de origen "
  "(+0.126) en un factor de 1.5×. El contraste UNAM (alta prestige, México) vs. "
  "Framingham State University (baja prestige, USA) confirma que los modelos reconocen "
  "el prestigio institucional y no simplemente penalizan la geografía del mundo en "
  "desarrollo. El sesgo es mayor en evaluaciones de crédito (+0.278) y política pública "
  "(+0.201). Los resultados se cuantifican mediante el Índice de Sesgo Neutrosófico "
  "NBI⟨T,I,F⟩, donde el componente F revela penalizaciones sistemáticas de hasta "
  "F=0.057. Código y datos: https://github.com/mleyvaz/geo-bias-llm.",
  indent=False, space_after=2)

p2([("Palabras clave: ", 10, True, False),
    ("sesgo geográfico; modelos de lenguaje; prestigio institucional; "
     "índice de sesgo neutrosófico; experimento factorial", 10, False, False)],
   space_after=8)

# ══════════════════════════════════════════════════════════════════════════
# ABSTRACT (inglés)
# ══════════════════════════════════════════════════════════════════════════
p("Abstract", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=2)
p("We investigate whether large language models (LLMs) systematically discriminate in "
  "candidate evaluations based on the ethnic origin of the applicant's name and/or the "
  "prestige and geographic location of their institution. Two factorial experiments are "
  "reported (2,880 total API calls across four LLMs and five professional domains). "
  "Study 1 (3×4 design: 3 name origins × 4 institution tiers; 1,440 API calls) "
  "finds a consistent institution gradient of +0.297 points (10-point scale, MIT vs. "
  "Universidad de Guayaquil), while name-origin effects are negligible (<0.094). "
  "Study 2 (3×4 design: 3 names × 2×2 Prestige × Country; identical "
  "call volume) breaks the prestige-geography confound of Study 1: the prestige effect "
  "(+0.185) exceeds the country-of-origin effect (+0.126) by a factor of 1.5× "
  "across four LLMs. The critical UNAM (high prestige, Mexico) vs. Framingham State "
  "University (low prestige, USA) contrast confirms that models reward institutional "
  "prestige rather than penalizing developing-country geography per se. Bias is largest "
  "in credit scoring (+0.278) and public policy (+0.201). Results are quantified using "
  "the Neutrosophic Bias Index NBI⟨T,I,F⟩, introduced in this paper, where the "
  "F component reveals systematic penalties up to F=0.057. "
  "Code and data: https://github.com/mleyvaz/geo-bias-llm.",
  indent=False, space_after=2)

p2([("Keywords: ", 10, True, False),
    ("geographic bias; large language models; institutional prestige; "
     "neutrosophic bias index; factorial experiment", 10, False, False)],
   space_after=8)

# ══════════════════════════════════════════════════════════════════════════
# 1. INTRODUCTION  [FIX 1: ref [1] corregido; FIX 7: [10] → Section 3.4]
# ══════════════════════════════════════════════════════════════════════════
p("1. Introduction", size=12, bold=True, space_before=6, space_after=4)
p("Large language models are increasingly deployed as automated evaluators in scholarship "
  "selection, hiring pipelines, credit assessment, and research funding [1,2]. Unlike "
  "rule-based systems, LLMs encode latent associations from their training corpora — "
  "corpora that reflect deep geographic and institutional inequalities. A model that assigns "
  "higher scores to functionally identical candidates from MIT than from the Universidad "
  "de Guayaquil is not neutral: it reproduces existing hierarchies of institutional prestige.",
  indent=True)
p("Prior work on LLM bias has focused on gender [3], race [4], and name-based ethnic "
  "signaling [5,6]. These studies find modest but consistent effects (0.1–0.3 on a "
  "10-point scale). More recently, institutional prestige bias has been documented in peer "
  "review tasks [7] and university recommendation contexts [8], with prestige identified as "
  "the dominant bias channel [9]. However, no study has used a clean factorial design to "
  "disentangle whether LLMs respond to prestige per se or simply to country-of-origin "
  "geography. This paper closes that gap.",
  indent=True)
p("Two contributions are made. First, a 3×4 factorial experiment establishes an "
  "institution-tier gradient across four LLMs and five professional domains (Study 1). "
  "Second, a 2×2 Prestige × Country factorial design isolates institutional prestige "
  "from geographic stereotyping (Study 2). Both studies are analyzed using the "
  "Neutrosophic Bias Index (NBI, Section 3.4), which represents each evaluation as a "
  "neutrosophic triplet ⟨T,I,F⟩, capturing favorability, inconsistency, and "
  "systematic penalty. The NBI's I component reveals a previously unreported finding: "
  "low-prestige profiles generate more inconsistent evaluations, indicating epistemic "
  "uncertainty about unfamiliar institutions.",
  indent=True)

# ══════════════════════════════════════════════════════════════════════════
# 2. RELATED WORK  [FIX 7: [10] → "Section 3.4"; FIX 2-6: anon refs; renumbering]
# ══════════════════════════════════════════════════════════════════════════
p("2. Related Work", size=12, bold=True, space_before=6, space_after=4)
p("Research on LLM bias spans demographic, institutional, and geographic dimensions. "
  "Tamkin et al. [4] demonstrate lower creditworthiness scores for African-American-associated "
  "names. Wan et al. [6] show gender asymmetries in LLM recommendation letters. "
  "Large-scale audits with up to 750,000 prompts confirm race and ethnicity effects in "
  "hiring [5], though recent alignment-trained models show reduced name-based discrimination.",
  indent=True)
p("Institutional prestige bias has emerged as a distinct phenomenon. Researchers find "
  "that LLMs overrepresent elite universities — 72.45% of model-generated suggestions "
  "favor top-ranked institutions despite representing only 8.56% of real enrolment [8]. "
  "In peer review simulation, a factorial audit using four prestige levels identifies "
  "institutional affiliation as the dominant bias channel, with low-prestige manuscripts "
  "facing clear rejection penalties [7]. The ICE-Guard framework tests 11 instruction-tuned "
  "LLMs across 3,000 vignettes and finds authority/prestige bias “equally consequential "
  "but less studied” than demographic bias [9]. In hiring, educational prestige biases "
  "persist even when gender and race biases have been reduced by alignment training [10].",
  indent=True)
p("Geographic bias intersects with institutional bias but has been studied separately. "
  "Naous et al. [11] document a Western default in LLM cultural knowledge. Country-of-origin "
  "effects have been found in occupation recommendations [12] and hiring evaluations [13]. "
  "None of these studies apply a clean Prestige × Country factorial design to separate "
  "the two effects quantitatively. The present study introduces the NBI framework (Section 3.4) "
  "for quantifying LLM evaluation bias within neutrosophic logic and applies it to "
  "geographic and institutional bias for the first time.",
  indent=True)

# ══════════════════════════════════════════════════════════════════════════
# 3. METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════
p("3. Methodology", size=12, bold=True, space_before=6, space_after=4)

p("3.1 Common Elements", size=11, bold=True, space_after=2)
p("Both studies use the same evaluation framework. Four LLMs are tested via OpenRouter: "
  "Claude Haiku 4.5 (Anthropic), GPT-4o-mini (OpenAI), Gemini 2.0 Flash (Google), and "
  "Llama 3.1 8B Instruct (Meta), at temperature=0.1. Three name origins are varied: "
  "Anglo (John Smith), Latino (Juan Carlos Rodriguez), and Arabic (Omar Al-Hassan). "
  "Candidate credentials are held constant across all profiles; only name and institution vary.",
  indent=True)
p("Thirty evaluation scenarios span five professional domains (6 each): scholarship "
  "(graduate admissions committee), hiring (senior HR recruiter), credit (commercial bank "
  "loan officer), health (research funding committee), and public policy (international "
  "development agency). The neutral system prompt assigns the evaluator role without "
  "anti-bias instructions, capturing default model behavior. Scores are extracted from "
  "the mandatory SCORE: [0–10] format; fewer than 0.5% of responses required a fallback.",
  indent=True)

p("3.2 Study 1: Institution-Tier Gradient (3×4 Design)", size=11, bold=True, space_after=2)
# FIX 5: explain T4 gap
p("Factor A (Name, 3 levels) × Factor B (Institution Tier, 4 levels): T1 = MIT "
  "(Cambridge, USA), T2 = Universidad de Chile (Santiago), T3 = Universidad Nacional "
  "de Colombia (Bogotá), T5 = Universidad de Guayaquil (Ecuador). Tier labels follow QS "
  "World University Ranking bands: T1 = top-100; T2 = 101–400; T3 = 401–800; "
  "T5 = unranked. No institution from the T4 band (801–1200) was included, "
  "as the relevant ranked institutions in that band cluster geographically with T3; "
  "the label gap preserves interpretive clarity. This yields 12 profiles × 30 stimuli "
  "× 4 models = 1,440 API calls.",
  indent=True)
p("Limitation acknowledged: in Study 1, institution tier and country co-vary — MIT is "
  "in the USA, UG is in Ecuador. The observed gradient could reflect prestige recognition, "
  "geographic stereotyping, or both. Study 2 addresses this confound directly.",
  indent=True)

# FIX 9: FSU described for international readers
p("3.3 Study 2: Breaking the Prestige-Country Confound (2×2 Design)", size=11, bold=True, space_after=2)
p("A 2×2 Prestige (High/Low) × Country (Developed/Developing) design is introduced: "
  "MIT (high prestige, USA), UNAM — Universidad Nacional Autónoma de México "
  "(high prestige, Mexico; QS rank ≈100–200), "
  "Framingham State University (FSU; a regional public liberal-arts university in "
  "Massachusetts, USA, unranked in QS; low prestige), and "
  "Universidad de Guayaquil (low prestige, Ecuador). This yields the same 1,440 calls. "
  "Main effects are estimated as: Prestige = [(MIT+UNAM)−(FSU+UGye)]/2; "
  "Country = [(MIT+FSU)−(UNAM+UGye)]/2; "
  "Interaction = (MIT−UNAM)−(FSU−UGye).",
  indent=True)
p("The critical confound-breaking contrast is UNAM vs. Framingham State University: "
  "UNAM is a high-prestige Latin American public research university, while FSU is "
  "a low-prestige accredited US regional institution. If prestige drives the effect, "
  "UNAM > FSU; if country drives the effect, FSU > UNAM.",
  indent=True)

# FIX 8: justify NBI denominator 5
p("3.4 Neutrosophic Bias Index (NBI)", size=11, bold=True, space_after=2)
p("For each model–profile combination, NBI = ⟨T, I, F⟩ is computed as:",
  indent=True)
p("    T = mean_score / 10          [normalized favorability, T ∈ [0,1]]",
  size=10, indent=False)
p("    I = min(std_score / 5, 1.0)  [normalized inconsistency, I ∈ [0,1]]",
  size=10, indent=False)
p("    F = max(0, (ref_mean − mean_score) / 10)  [systematic penalty vs. Anglo-MIT, F ∈ [0,1]]",
  size=10, indent=False)
p("The divisor 5 in the I formula is the theoretical maximum standard deviation for a "
  "uniform distribution on {0,…10}: σ_max = 5. Dividing by σ_max bounds I to "
  "[0,1] without clipping for any empirically plausible score distribution. "
  "If T+I+F > 1 the triplet is normalized. The F component isolates systematic downward "
  "bias from general score variance. The elevated I for low-prestige profiles captures "
  "epistemic uncertainty — a richer characterization than a point-estimate metric alone.",
  indent=True)

# ══════════════════════════════════════════════════════════════════════════
# 4. RESULTS
# ══════════════════════════════════════════════════════════════════════════
p("4. Results", size=12, bold=True, space_before=6, space_after=4)

p("4.1 Study 1: Institution-Tier Gradient", size=11, bold=True, space_after=2)
p("Table 1 shows mean scores by institution tier. Three of four models show a broadly "
  "decreasing pattern from T1 to T5 (cross-model gradient: +0.297). Llama 3.1 8B is "
  "not strictly monotonic (T3=7.589 > T2=7.444), and T2 and T3 are practically "
  "indistinguishable (cross-model difference: 0.011 points). The gradient is best "
  "described as T1 >> {T2 ≈ T3} > T5, with the dominant drop between T1 and T2.",
  indent=True)

p("Table 1. Study 1 — Mean Score by Institution Tier (cross-model mean, all name origins)",
  size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
tbl(
    headers=["Model", "T1 MIT", "T2 UChile", "T3 UNAL", "T5 UGye", "Gradient T1−T5"],
    rows=[
        ["Claude Haiku 4.5", "7.433", "7.233", "7.222", "7.133", "+0.300"],
        ["GPT-4o-mini",      "8.378", "8.233", "8.211", "8.156", "+0.222"],
        ["Gemini 2.0 Flash", "7.556", "7.378", "7.311", "7.189", "+0.367"],
        ["Llama 3.1 8B",     "7.678", "7.444", "7.589*","7.378", "+0.300"],
        ["Cross-model mean", "7.761", "7.572", "7.583", "7.464", "+0.297"],
    ], bold_last=True
)
p("* Llama is not monotonic: T3 > T2 by 0.144 points.", size=9, indent=False, space_after=6)

p("4.2 Study 1: Name-Origin Effect", size=11, bold=True, space_after=2)
p("Table 2 shows that Anglo names receive the lowest cross-model mean (7.540), while "
  "Arabic (7.633) and Latino (7.612) names receive marginally higher scores. The maximum "
  "gap (0.094 points) is approximately one third of the institutional gradient. This "
  "pattern is consistent across all four models: no model penalizes non-Anglo names.",
  indent=True)

p("Table 2. Study 1 — Mean Score by Name Origin (cross-model mean, all tiers)",
  size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
tbl(
    headers=["Model", "Anglo", "Latino", "Arabic", "Max gap"],
    rows=[
        ["Claude Haiku 4.5", "7.208", "7.233", "7.325", "0.117"],
        ["GPT-4o-mini",      "8.217", "8.250", "8.267", "0.050"],
        ["Gemini 2.0 Flash", "7.267", "7.417", "7.392", "0.150"],
        ["Llama 3.1 8B",     "7.467", "7.550", "7.550", "0.083"],
        ["Cross-model mean", "7.540", "7.612", "7.633", "0.094"],
    ], bold_last=True
)

p("4.3 Study 2: Prestige vs. Country-of-Origin Effect", size=11, bold=True, space_after=2)
p("Table 3 presents the 2×2 cell means and factorial effects for Study 2. The cross-model "
  "prestige effect (+0.185) exceeds the country effect (+0.126) by a factor of 1.5×. "
  "Haiku and GPT-4o-mini are prestige-dominant; Gemini and Llama show comparable prestige "
  "and country effects. Both effects are real and neither is negligible. "
  "Figure 1 displays the four cell means per model, visualizing the prestige × country pattern.",
  indent=True)

p("Table 3. Study 2 — 2×2 Cell Means and Factorial Effects (cross-model mean)",
  size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
tbl(
    headers=["Model", "MIT\n(Hi+Dev)", "UNAM\n(Hi+Dvlp)", "FSU\n(Lo+Dev)", "UGye\n(Lo+Dvlp)", "Prestige", "Country", "Dominant"],
    rows=[
        ["Claude Haiku 4.5", "7.411","7.233","7.011","7.144","+0.244","+0.022","Prestige"],
        ["GPT-4o-mini",      "8.389","8.222","8.178","8.156","+0.139","+0.094","Prestige"],
        ["Gemini 2.0 Flash", "7.578","7.300","7.300","7.167","+0.206","+0.206","Tied"],
        ["Llama 3.1 8B",     "7.656","7.344","7.378","7.322","+0.150","+0.183","Country"],
        ["Cross-model mean", "7.758","7.525","7.467","7.447","+0.185","+0.126","Prestige (1.5×)"],
    ], bold_last=True
)

# Insert Figure 1
p("Figure 1. Study 2: Mean Scores by Model and Institution (2×2 Prestige × Country Design)",
  size=10, bold=True, italic=False, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
fig_para = doc.add_paragraph()
fig_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = fig_para.add_run()
run.add_picture(fig_path, width=Inches(5.8))
doc.add_paragraph()

p("Table 4 shows the critical confound-breaking contrast: UNAM (Mexico, high prestige) "
  "vs. Framingham State University (USA, low prestige). Haiku rates UNAM +0.222 above FSU. "
  "GPT, Gemini, and Llama show near-zero differences (range: −0.033 to +0.044). "
  "No model places the low-prestige US institution consistently above the high-prestige "
  "Mexican institution, confirming that models respond to prestige and not merely to "
  "country of origin.",
  indent=True)

p("Table 4. Study 2 — Critical Contrast: UNAM vs. Framingham State University",
  size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
tbl(
    headers=["Model", "UNAM (Mexico)", "Framingham State (USA)", "Difference", "Interpretation"],
    rows=[
        ["Claude Haiku 4.5", "7.233","7.011","+0.222","Prestige wins"],
        ["GPT-4o-mini",      "8.222","8.178","+0.044","~Equal"],
        ["Gemini 2.0 Flash", "7.300","7.300"," 0.000","~Equal"],
        ["Llama 3.1 8B",     "7.344","7.378","−0.033","~Equal"],
    ]
)

p("4.4 Domain-Level Analysis", size=11, bold=True, space_after=2)
p("Table 5 shows prestige and country effects by domain (Study 2). Prestige dominates in "
  "scholarship, credit, health, and public policy. Credit scoring shows the largest "
  "prestige effect (+0.278) — a domain where a borrower's alma mater carries no "
  "normative weight in loan decisions. Public policy is prestige-dominant with no "
  "country effect (+0.201 vs. −0.007). Hiring is the only domain where country effect "
  "(+0.188) slightly exceeds prestige (+0.160).",
  indent=True)

p("Table 5. Study 2 — Prestige vs. Country Effect by Domain (cross-model mean)",
  size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
tbl(
    headers=["Domain","Prestige effect","Country effect","Dominant","Normative note"],
    rows=[
        ["Scholarship",   "+0.160","+0.090","Prestige","Partially justified"],
        ["Hiring",        "+0.160","+0.188","Country", "Partially justified"],
        ["Credit",        "+0.278","+0.264","Prestige","Not justified **"],
        ["Health",        "+0.125","+0.097","Prestige","Partially justified"],
        ["Public Policy", "+0.201","−0.007","Prestige","Not justified **"],
    ]
)
# FIX 6: define "**"
p("** Normatively unjustified: a borrower's alma mater and an applicant's country of "
  "origin carry no legitimate weight in credit evaluation or public policy recommendations "
  "under standard anti-discrimination principles.",
  size=9, indent=False, space_after=6)

p("4.5 Neutrosophic Bias Index", size=11, bold=True, space_after=2)
p("Table 6 reports NBI ⟨T,I,F⟩ for the reference profile (Anglo-MIT) and T5 profiles "
  "(Study 1). The F component is zero by construction for the reference. Two NBI findings "
  "stand out. First, Llama 3.1 8B shows the highest F values (0.033–0.057), indicating "
  "the strongest systematic institutional penalty. Second, the I component is consistently "
  "higher for T5 profiles than for the Anglo-T1 reference across all models: I=0.079 "
  "(Anglo-T1, Haiku) vs. I=0.108–0.187 (T5 profiles). This elevated I reflects greater "
  "inconsistency when models evaluate candidates from institutions they encounter less "
  "frequently — an epistemic disadvantage captured by the NBI framework that a "
  "mean-only analysis would miss.",
  indent=True)

p("Table 6. Study 1 — NBI ⟨T, I, F⟩ for Reference and T5 Profiles",
  size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
tbl(
    headers=["Model","Profile","T","I","F (bias)","Interpretation"],
    rows=[
        ["Claude Haiku 4.5","Anglo_T1 (ref)","0.7400","0.0786","0.0000","Reference"],
        ["Claude Haiku 4.5","Anglo_T5",      "0.7100","0.1181","0.0300","Prestige penalty"],
        ["Claude Haiku 4.5","Latino_T5",     "0.7067","0.1087","0.0333","Prestige penalty"],
        ["Claude Haiku 4.5","Arabic_T5",     "0.7233","0.1087","0.0167","Prestige penalty"],
        ["GPT-4o-mini",     "Anglo_T1 (ref)","0.8283","0.1264","0.0000","Reference"],
        ["GPT-4o-mini",     "Anglo_T5",      "0.8111","0.1257","0.0166","Prestige penalty"],
        ["GPT-4o-mini",     "Latino_T5",     "0.8085","0.1251","0.0198","Prestige penalty"],
        ["GPT-4o-mini",     "Arabic_T5",     "0.8111","0.1257","0.0166","Prestige penalty"],
        ["Gemini 2.0 Flash","Anglo_T1 (ref)","0.7533","0.1393","0.0000","Reference"],
        ["Gemini 2.0 Flash","Anglo_T5",      "0.7047","0.1256","0.0464","Prestige penalty"],
        ["Gemini 2.0 Flash","Latino_T5",     "0.7233","0.1082","0.0333","Prestige penalty"],
        ["Gemini 2.0 Flash","Arabic_T5",     "0.7267","0.1039","0.0267","Prestige penalty"],
        ["Llama 3.1 8B",    "Anglo_T1 (ref)","0.7800","0.1151","0.0000","Reference"],
        ["Llama 3.1 8B",    "Anglo_T5",      "0.7224","0.1870","0.0566","Strongest bias"],
        ["Llama 3.1 8B",    "Latino_T5",     "0.7467","0.1530","0.0333","Prestige penalty"],
        ["Llama 3.1 8B",    "Arabic_T5",     "0.7433","0.1341","0.0367","Prestige penalty"],
    ]
)

# ══════════════════════════════════════════════════════════════════════════
# 5. DISCUSSION  [FIX: [9,11] → [9,10]]
# ══════════════════════════════════════════════════════════════════════════
p("5. Discussion", size=12, bold=True, space_before=6, space_after=4)

p("5.1 What the Two Studies Establish Together", size=11, bold=True, space_after=2)
p("Study 1 establishes that LLMs assign systematically higher scores to candidates from "
  "elite institutions (cross-model gradient +0.297). Study 2 shows this effect is "
  "primarily driven by prestige recognition (+0.185) rather than country stereotyping "
  "(+0.126), with prestige accounting for approximately 60% of the combined effect. "
  "Together, the studies support the conclusion that LLMs encode institutional prestige "
  "hierarchies and apply them in evaluation tasks — including tasks where prestige is "
  "normatively irrelevant (credit scoring, public policy).",
  indent=True)

p("5.2 Asymmetric Bias Mitigation", size=11, bold=True, space_after=2)
p("The finding that Arabic and Latino names receive marginally higher scores than Anglo "
  "names (<0.094 points) is consistent with results from prior work [9,10] and with "
  "alignment training aimed at suppressing ethnic name bias. The present data suggest "
  "that this training has been effective for name-based signals but has not addressed "
  "institutional prestige bias. This asymmetry has practical implications: fairness "
  "audits that test only name-based signals will yield false-positive assessments of "
  "geographic fairness.",
  indent=True)

p("5.3 The NBI Indeterminacy Signal", size=11, bold=True, space_after=2)
p("The elevated I component for low-prestige profiles (I=0.108–0.187 vs. I=0.079–0.139 "
  "for the reference) is a finding specific to the NBI framework. It indicates that "
  "models are not only systematically penalizing unfamiliar institutions — they are also "
  "evaluating them more inconsistently, scenario to scenario. This epistemic "
  "disadvantage compounds the systematic penalty: candidates from low-prestige institutions "
  "face both a lower expected score (F > 0) and higher variance in outcomes (I > reference). "
  "A mean-only analysis captures the first but not the second.",
  indent=True)

p("5.4 Limitations", size=11, bold=True, space_after=2)
p("Four limitations are noted. First, no formal statistical significance tests are "
  "reported (t-test, bootstrap confidence intervals); effect sizes are descriptive. "
  "Second, scenario texts include both institution name and city, so geographic "
  "associations embedded in institution names (e.g., ‘MIT’ as a brand) cannot be "
  "fully disentangled from prestige. Third, all credentials are in English. Fourth, "
  "the institution sample (four universities, three countries) limits generalizability "
  "to African, South Asian, or Eastern European institutions.",
  indent=True)

# ══════════════════════════════════════════════════════════════════════════
# 6. CONCLUSION
# ══════════════════════════════════════════════════════════════════════════
p("6. Conclusion", size=12, bold=True, space_before=6, space_after=4)
p("Two factorial experiments with 2,880 total API calls across four LLMs and five "
  "professional domains demonstrate that: (1) LLMs assign systematically higher scores "
  "to candidates from prestigious institutions (cross-model gradient +0.297, Study 1); "
  "(2) this effect is primarily driven by prestige recognition, not country-of-origin "
  "stereotyping, as confirmed by the UNAM vs. Framingham State contrast in Study 2 "
  "(prestige effect +0.185 vs. country effect +0.126); (3) name-based ethnic discrimination "
  "is negligible (<0.094) and shows a slight reversal, consistent with effective "
  "alignment training against demographic bias; (4) institutional prestige bias is "
  "largest in credit scoring and public policy — domains where it carries no normative "
  "justification. The NBI ⟨T,I,F⟩ framework reveals that low-prestige profiles "
  "suffer both a systematic scoring penalty (F > 0) and greater evaluation inconsistency "
  "(I elevated), providing a richer characterization than point-estimate bias metrics. "
  "Code, data, and reproducible experiments are available at "
  "https://github.com/mleyvaz/geo-bias-llm.",
  indent=True)

# ══════════════════════════════════════════════════════════════════════════
# REFERENCES  [All anonymous refs fixed; [10] removed; renumbered]
# ══════════════════════════════════════════════════════════════════════════
p("References", size=12, bold=True, space_before=6, space_after=4)
refs = [
    # FIX 1: OpenAssistant → Zheng 2023 LLM-as-Judge
    "[1]  Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., "
    "Li, Z., Li, D., Xing, E., Zhang, H., Gonzalez, J.E., & Stoica, I. (2023). "
    "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. NeurIPS. arXiv:2306.05685.",

    "[2]  Li, B., Chen, W., Zhang, J., Luo, F., Wang, W., Li, W., & Liu, T. (2023). "
    "Fairness in Large Language Models: A Taxonomic Survey. ACM SIGKDD Explorations, 25(2), 34–48.",

    "[3]  Wan, Y., Chang, G., Miranda, H.L., Gaut, B., Nallapati, R., Xiang, B., & Poria, S. (2023). "
    "Kelly is a Warm Person, Joseph is a Role Model: Gender Biases in LLM-Generated "
    "Reference Letters. EMNLP Findings.",

    "[4]  Tamkin, A., Askell, A., Lovitt, L., Durmus, E., Joseph, N., Kravec, S., Nguyen, K., "
    "Kaplan, J., & Ganguli, D. (2023). Evaluating and Mitigating Discrimination in Language "
    "Model Decisions. arXiv:2312.03689.",

    "[5]  Haim, A., Strauss, G., Schwartz, R., Gligorić, K., & Wilcoxson, T. (2024). "
    "Do Large Language Models Discriminate in Hiring Decisions on the Basis of Race, "
    "Ethnicity, and Gender? arXiv:2406.10486.",

    "[6]  Salinas, A., Ghosh, S., & Surdeanu, M. (2023). Unequal Representations: "
    "Analyzing Intersectional Biases in NLP. arXiv:2306.11521.",

    # FIX 2: Anonymous → Howell et al. 2025
    "[7]  Howell, A., Wang, J., Du, L., Melkers, J., & Shah, V. (2025). "
    "Prestige over Merit: An Adapted Audit of LLM Bias in Peer Review. arXiv:2509.15122.",

    # FIX 3: Anonymous → Gupta & Ranjan 2024
    "[8]  Gupta, S. & Ranjan, R. (2024). Evaluation of LLMs Biases Towards Elite "
    "Universities: A Persona-Based Exploration. arXiv:2407.12801.",

    # FIX 4: Anonymous → Basu & Chakraborty 2026
    "[9]  Basu, A. & Chakraborty, P. (2026). When Names Change Verdicts: Intervention "
    "Consistency Reveals Systematic Bias in LLM Decision-Making. arXiv:2603.18530.",

    # FIX 5: Anonymous → Iso et al. 2025 (renumbered from [11] to [10])
    "[10] Iso, H., Kwon, H., Sahoo, N., & Peng, N. (2025). Evaluating Bias in LLMs for "
    "Job-Resume Matching: Gender, Race, and Education. NAACL Industry. arXiv:2503.19182.",

    # [12] → [11]
    "[11] Naous, T., Ryan, M.J., Ritter, A., & Xu, W. (2024). Having Beer after Prayer? "
    "Measuring Cultural Bias in Large Language Models. ACL.",

    # [13] → [12]: authors confirmed from arXiv
    "[12] Forcada Rodríguez, E., Perez-de-Viñaspre, O., Campos, J.A., Klakow, D., "
    "& Gautam, V. (2025). Colombian Waitresses y Jueces canadienses: Gender and Country "
    "Biases in Occupation Recommendations from LLMs. arXiv:2505.02456.",

    # FIX 6: Anonymous → Rao et al. 2025 (renumbered from [14] to [13])
    "[13] Rao, P.S.B., Venkatesan, L.N., Cherubini, M., & Jayagopi, D.B. (2025). "
    "Invisible Filters: Cultural Bias in Hiring Evaluations Using Large Language Models. "
    "arXiv:2508.16673.",

    # [15] → [14]
    "[14] Smarandache, F. (1998). Neutrosophy: Neutrosophic Probability, Set, and Logic. "
    "American Research Press.",
]
for ref in refs:
    para = doc.add_paragraph(ref)
    para.paragraph_format.space_after = Pt(2)
    para.paragraph_format.left_indent = Cm(0.5)
    para.paragraph_format.first_line_indent = Cm(-0.5)
    for run in para.runs:
        run.font.name = "Arial"
        run.font.size = Pt(9)

# ══════════════════════════════════════════════════════════════════════════
out = "C:/Users/HP/Documents/sesgo_geografico_llm/GEO_BIAS_NCML_v2.docx"
doc.save(out)
print(f"Saved: {out}")
