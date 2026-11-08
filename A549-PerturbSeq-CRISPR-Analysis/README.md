# A549 Perturb-seq: CRISPR Perturbation Response Profiling

An exploratory, reproducible R/Seurat workflow for two-channel **A549 single-cell Perturb-seq** data, focused on perturbation-response signatures rather than artificially separated UMAP clusters.

**Author:** Joshua (Xuehuo) Zeng, PhD  
**Portfolio:** [zenggitrepos/joshzeng](https://github.com/zenggitrepos/joshzeng)

## Overview

This project demonstrates analysis of a pooled single-cell perturbation screen: AnnData-to-Seurat conversion, channel-aware merging, single-cell quality control, normalization, clustering, differential-expression screening, on-target transcript assessment, pathway interpretation, and similarity of response signatures.

A549 is one cell line; **clearly separated UMAP clusters are not a prerequisite for meaningful perturbation effects**. Channels are treated as distinct capture batches, not assumed to be independent biological replicates.

## Notebook

[`A549_PerturbSeq_Seurat_Analysis.ipynb`](A549_PerturbSeq_Seurat_Analysis.ipynb) — R-kernel notebook; run sequentially from top to bottom.

## Analyses included

1. Load the two `.h5ad` files and validate count-matrix assumptions.
2. Convert expression matrices and metadata into Seurat objects.
3. Merge channels using `add.cell.ids = c("Ch1", "Ch2")` to prevent duplicate cell-barcode names.
4. QC by channel (UMI counts, detected genes, mitochondrial fraction), SCTransform, PCA, clustering and UMAP.
5. Harmonize perturbation labels and detect non-targeting controls (configurable).
6. Summarize target representation, QC distributions and channel balance.
7. Compare target-associated cluster compositions.
8. Perform exploratory perturbation-vs-NTC differential-expression screening, with DEG summaries and volcano plots.
9. Inspect on-target transcript changes and target-specific GO Biological Process enrichment.
10. Compare perturbation log2FC signatures and assess within-channel consistency.
11. Export result tables and session information.

## Data

The notebook expects these **locally prepared** AnnData files (not committed to Git):

```text
perturbseq-a549/
├── README.md
├── A549_PerturbSeq_Seurat_Analysis.ipynb
├── .gitignore
└── data/                           # user-provided, gitignored
    ├── GSE337804_A549_ch_1.RDS.h5ad
    └── GSE337804_A549_ch_2.RDS.h5ad
```
