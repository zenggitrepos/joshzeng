#!/bin/bash


out_dir="/out/dir"
cd  ${out_dir}

fastq_files=$(ls ${out_dir}/*.fastq | rev | cut -d '/' -f 1 | rev | cut -d'_' -f 1 | uniq)
n_files=$(echo $fastq_files | wc -w)

fastq=$(echo ${fastq_files} | sed "s%[^ ]* *%$out_dir/&%g")

# fastqc before QC
mkdir -p ${out_dir}/fastqc_preQC
fastqc -t 5 ${out_dir}/*.fastq -o ${out_dir}/fastqc_preQC


parallel --verbose -j 2 trim_galore -q 25 --phred33 --length 35 -e 0.1 --stringency 4 --paired -o clean {}_1.fastq {}_2.fastq ::: ${fastq}
wait
mv clean ${out_dir}

# fastqc after QC

mkdir -p ${out_dir}/clean/fastqc_postQC
fastqc -t 5 ${out_dir}/clean/*val_*.fq -o ${out_dir}/clean/fastqc_postQC
