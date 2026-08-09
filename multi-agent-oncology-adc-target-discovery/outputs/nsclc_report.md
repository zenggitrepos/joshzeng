# ADC target discovery report — NSCLC

## 1. TROP2
- ADC score: 0.761
- Priority: High
- Summary: TROP2 in NSCLC shows compelling ADC‑targetable features (high expression, selectivity, favorable surface/internalization signals) but is hampered by limited clinical data, low CRISPR dependency, and modest off‑tumor expression. Given the strong preclinical ADC relevance and biomarker support, it merits high priority for further ADC development, while addressing the evidential gaps.
- Strengths:
  - High ADC relevance (score 0.85) and biomarker relevance (score 0.85)
  - Strong tumor epithelial expression (mean 8.60) and high selectivity ratio (5.1)
  - Favorable protein language model scores: surfaceability/internalization >0.88, extracellular domain 0.92
  - Single-cell data shows 79% tumor cells positive
  - Limited but relevant literature (2 papers) supporting TROP2 in NSCLC
- Liabilities:
  - Low CRISPR dependency (score 0.12, fraction dependent 0.0) indicating limited essentiality
  - Only 2 supporting papers, limiting clinical evidence
  - Off‑tumor expression detected (max 0.90) though low
  - Modest immune cell expression (mean 0.6) may affect specificity
- Contradictions:
  - High expression and PLM scores contrast with low CRISPR dependency suggesting non‑essential target
  - Strong ADC relevance despite minimal clinical literature
  - High tumor selectivity ratio coexisting with detectable off‑tumor expression

## 2. CEACAM5
- ADC score: 0.722
- Priority: High
- Summary: CEACAM5 in NSCLC demonstrates compelling tumor-selective expression, strong surfaceability and internalization signals, and moderate literature support, but the paucity of independent validation, low CRISPR dependency, and limited biomarker data keep the evidence from being definitive. Given the high selectivity and favorable protein‑level features, CEACAM5 merits high priority for ADC development, pending further clinical and functional validation.
- Strengths:
  - High tumor-normal selectivity ratio (7.5) with strong median tumor expression (22.9 TPM)
  - Robust single-cell tumor epithelial signal (mean 7.9) and 59% positive tumor cells
  - Favorable protein language model scores for surfaceability (0.9) and internalization (0.8)
  - Literature shows ADC relevance of 0.85 and biomarker relevance of 0.70 despite limited data
  - Positive protein-level features (signal peptide probability 0.97, extracellular domain score 0.95)
- Liabilities:
  - Only one supporting literature paper, limiting evidence breadth
  - Biomarker relevance modest (0.70) and ADC relevance not fully validated in vivo
  - CRISPR dependency score zero indicates lack of dependency, which may not be a liability for an ADC target but reflects limited functional validation
  - Off-tumor maximum expression low (0.60) but insufficient to guarantee safety without more normal tissue data
- Contradictions:
  - High selectivity and expression coexist with zero CRISPR dependency, which is unexpected for a functional target
  - Strong PLM surfaceability scores contrast with limited clinical‑grade ADC evidence

## 3. MET
- ADC score: 0.687
- Priority: Medium
- Summary: MET in NSCLC presents a biologically compelling but clinically risky ADC target. The target is functionally essential (strong CRISPR dependency) and possesses ideal biophysical characteristics for ADC engagement. However, the low tumor-to-normal selectivity ratio (2.85), heterogeneous tumor expression (62% positive), and known normal tissue expression collectively pose significant safety and efficacy liabilities. Priority is Medium: further work should focus on defining the therapeutic window via in vivo models, assessing payload potency requirements, and exploring conditional activation strategies (e.g., protease-cleavable linkers) to mitigate on-target off-tumor toxicity. Progression to IND-enabling studies is not recommended without improved selectivity data.
- Strengths:
  - Strong CRISPR dependency across all NSCLC cell lines tested (median Chronos -0.59, 100% dependent fraction), indicating MET is a core fitness gene in this context.
  - Excellent protein-level developability features: high probability of signal peptide (0.96), transmembrane domain (0.98), robust extracellular domain score (0.88), and favorable surfaceability (0.84) and internalization (0.82) scores, supporting efficient ADC targeting and payload delivery.
  - Detectable tumor epithelial expression in single-cell data (mean 6.90) with low off-tumor expression in immune (0.8) and stromal (1.3) compartments, suggesting tumor-restricted expression at the cellular level.
- Liabilities:
  - Modest tumor-to-normal selectivity ratio of only 2.85 (median tumor 16.8 TPM vs. normal 4.2 TPM), well below the typical >10-fold threshold desired for ADC targets to minimize on-target off-tumor toxicity.
  - Significant intratumoral heterogeneity: only 62% of tumor cells are MET-positive, which may limit efficacy and enable antigen-negative escape.
  - Sparse and synthetic literature evidence (only 2 papers, ADC relevance 0.60), providing limited clinical or mechanistic validation for ADC development.
  - Normal tissue expression of 4.2 TPM is non-negligible; MET is known to be expressed in liver, kidney, and other organs, raising safety concerns for systemic ADC administration.
- Contradictions:
  - High CRISPR dependency suggests MET is essential for NSCLC cell survival, yet the modest tumor-normal selectivity and heterogeneous expression create a narrow therapeutic window for an ADC approach.
  - Outstanding protein biophysical properties (surface expression, internalization) are at odds with the low selectivity ratio, meaning the target is technically 'ADC-amenable' but may not be safely druggable with a cytotoxic payload.
  - Single-cell data shows low off-tumor expression in stromal/immune cells, but bulk tumor-normal comparison reveals appreciable normal tissue expression, indicating that the relevant normal cell types may not be captured in the single-cell dataset.

## 4. EGFR
- ADC score: 0.656
- Priority: High
- Summary: EGFR shows compelling mechanistic and druggability evidence (high PLM score, CRISPR dependency, tumor expression) but is hampered by limited ADC‑specific literature and modest selectivity. Given the strong preclinical signals, a High priority is justified, with focus on improving ADC relevance and validating tumor‑normal selectivity.
- Strengths:
  - High protein language model score (0.92) indicating strong surfaceability and internalization potential
  - Robust CRISPR dependency (median Chronos = -0.57, dependent fraction = 1.0) across 10 cell lines
  - High tumor epithelial mean expression (7.2) and 66% positive fraction in single‑cell data
  - High biomarker relevance (mean 0.95) despite limited literature
  - Moderate tumor‑normal selectivity ratio (1.64) suggesting selective expression in tumor tissue
- Liabilities:
  - Low literature ADC relevance score (0.30) and only two supporting papers
  - Modest tumor‑normal selectivity ratio (1.64) indicating limited differential expression
  - Off‑tumor maximum expression capped at 1.00, suggesting potential on‑target toxicity in some normal tissues
- Contradictions:
  - Literature reports low ADC relevance while protein language model predicts high surfaceability/internalization
  - High biomarker relevance coexists with low ADC relevance, creating uncertainty about translatability
  - Strong CRISPR dependency contrasts with modest tumor‑normal selectivity, raising safety considerations

## 5. HER3
- ADC score: 0.600
- Priority: Medium
- Summary: HER3 in NSCLC shows promising ADC‑friendly biophysical properties but is hampered by limited tumor‑normal selectivity, low genetic dependency, and minimal clinical literature, warranting a medium priority for further investigation.
- Strengths:
  - High predicted surface expression and internalization potential from protein language model (score 0.908)
  - Literature indicates ADC relevance 0.80 and biomarker relevance 0.75
  - Detectable tumor epithelial expression (mean 6.4) with 55% of tumor cells positive in NSCLC
  - Moderate tumor-over-normal expression ratio (~1.8)
- Liabilities:
  - Low tumor-normal selectivity (ratio 1.82) indicating limited therapeutic window
  - Low CRISPR dependency (median Chronos -0.36, only 30% of cell lines dependent)
  - Sparse literature support (only one paper)
  - Off-tumor expression observed in stromal (mean 1.2) and immune (mean 0.6) compartments
- Contradictions:
  - Strong PLM-derived ADC suitability contrasts with low functional dependency and modest selectivity
  - High predicted internalization potential vs low genetic dependency suggests target may not be essential for tumor survival
