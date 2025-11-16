#!/bin/bash

# Fraction of reads in peaks (FRiP): fraction of all mapped reads that fall inot the called peak regions,
#  i.e usable reads in significantly enriched peaks divided by all usable reads
# In general, FRiP scores correlate positively with the number of the regions
# (Landt et al., Genome Reseach Sept. 2012, 22(9): 1813 - 1831)

out_dir="/out/dir/clean"
cd  ${out_dir}

fastq_files=$(ls ${out_dir}/*.fq | rev | cut -d '/' -f 1 | rev | cut -d'_' -f 1 | uniq)
n_files=$(echo $fastq_files | wc -w)

fastq=$(echo ${fastq_files} | sed "s%[^ ]* *%$out_dir/&%g")

idr --samples SRR2927016_peaks.narrowPeak SRR3545580_peaks.narrowPeak --plot > SRR2927016_SRR3545580.log
idr --samples SRR2927015_peaks.narrowPeak SRR2927016_peaks.narrowPeak --plot > SRR2927015_SRR2927016.log
idr --samples SRR2927015_peaks.narrowPeak SRR2927018_peaks.narrowPeak --plot > SRR2927015_SRR2927018.log
