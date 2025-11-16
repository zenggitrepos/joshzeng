#!/bin/bash

out_dir="/out/dir/clean"
cd  ${out_dir}

fastq_files=$(ls ${out_dir}/*.fq | rev | cut -d '/' -f 1 | rev | cut -d'_' -f 1 | uniq)
n_files=$(echo $fastq_files | wc -w)

fastq=$(echo ${fastq_files} | sed "s%[^ ]* *%$out_dir/&%g")

### Call peaks using MACS2
### Ref: https://biohpc.cornell.edu/doc/epigenomics_2020_exercise2.pdf
parallel --verbose -j 4 macs2 callpeak -t {}.bed  -g mm -B -q 0.05 --nomodel --shift -75 --extsize 150 --SPMR --keep-dup all --call-summits -n {}_2 ::: ${fastq}
### Ref: https://bioinformaticsworkbook.org/list.html#gsc.tab=0
### Ref: https://bioinformaticsworkbook.org/dataAnalysis/ATAC-seq/ATAC_tutorial.html#gsc.tab=0

#### Input parameters
# -t : treatment group
# -c : control group
# -f : file format (bam, sam, bed)
# -g : the genome size (hs = 2.7e9; mm = 1.87e9; ce = 9e7; dm = 1.2e8)
##### Output parameters
# --outdir : output path
# -n : prefix of output file names
# -B/-bdg : befgraph output format
##### Peak calling parameters
# --braod : narrow or broad

##### Shift model paramters:
# --nomodel : before extsize and Shift
# --extsize : 200 bp
# --shift : if negative = move from 3' end to 5' end
