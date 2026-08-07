# ATAC-seq Analysis Pipeline

## Overview

This repository contains a shell/R-based workflow for processing ATAC-seq data and evaluating chromatin accessibility profiles. The pipeline includes quality control, read alignment, peak calling, reproducibility assessment, FRiP score calculation, and visualization preparation.


## Workflow

1. Perform sequencing quality control
2. Align ATAC-seq reads to the reference genome using Bowtie2
3. Call open-chromatin peaks using MACS2
4. Calculate FRiP scores to assess library quality
5. Check peak overlap across samples or replicates
6. Evaluate reproducible peaks using IDR
7. Generate signal tracks for visualization in IGV

## Tools

- Shell scripting
- R
- Bowtie2
- MACS2
- deepTools
- IDR
- IGV
- Standard Unix command-line tools
