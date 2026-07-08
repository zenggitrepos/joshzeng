# Single-cell RNA-seq Analysis of Melanoma

## Overview

This project demonstrates a single-cell RNA-seq analysis workflow for melanoma using publicly available tumor single-cell data. The workflow includes quality control, normalization, batch correction, clustering, cell-type annotation, and exploratory marker-gene analysis.

The goal is to show practical experience with tumor single-cell RNA-seq analysis, melanoma tumor microenvironment characterization, and reproducible bioinformatics workflows using R and Seurat.

## Workflow

1. Load melanoma single-cell RNA-seq data and metadata
2. Create and merge Seurat objects
3. Perform quality control using gene counts, UMI counts, mitochondrial percentage, ribosomal percentage, and hemoglobin percentage
4. Normalize data using SCTransform
5. Correct batch effects using Harmony
6. Perform PCA, UMAP visualization, and graph-based clustering
7. Annotate cell types using SingleR and reference single-cell data
8. Explore melanoma- and immune-related marker genes across cell types and melanoma subtypes

## Marker Genes Explored

- **DLL3**
- **CD5**
- **SASH3**
- **TRBV20-1**
- **TNFSF18**
- **FOXP3**
- **CCR8**
- **KREMEN1**

## Tools

- R
- Seurat
- Harmony
- SingleR
- SingleCellExperiment
- GEOquery
- ggplot2
- dplyr

## Skills Demonstrated

- Single-cell RNA-seq preprocessing and quality control
- Seurat-based analysis workflow
- Batch correction and data integration
- UMAP visualization and clustering
- Reference-based cell-type annotation
- Tumor microenvironment analysis
- Melanoma subtype comparison
- Exploratory biomarker and marker-gene analysis

## Relevance

This project is relevant to computational biology, oncology bioinformatics, translational biomarker discovery, and tumor microenvironment analysis.
