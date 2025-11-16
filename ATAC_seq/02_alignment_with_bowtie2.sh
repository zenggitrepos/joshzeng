#!/bin/bash

out_dir="/out/dir/clean"
cd  ${out_dir}

### Reference
bowtie2_index=/REF/bowtie2/mm10/mm10

### Cleaned fastq files with file path
fastq_files=$(ls ${out_dir}/*.fq | rev | cut -d '/' -f 1 | rev | cut -d'_' -f 1 | uniq)
n_files=$(echo $fastq_files | wc -w)

### fastq files without file path
fastq=$(echo ${fastq_files} | sed "s%[^ ]* *%$out_dir/&%g")

### Aling the read to reference
# Due to memory limit, run 1 sample each time
# parallel --verbose -j ${n_files} bowtie2  -p 5  --very-sensitive -X 2000 -x  $bowtie2_index -1 {}_1_val_1.fq -2 {}_1_val_1.fq ::: ${fastq}
parallel --verbose -j 1 bowtie2  -p 5  --very-sensitive -X 2000 -x  $bowtie2_index -1 {}_val_1.fq -2 {}_val_2.fq -S {}.sam ::: ${fastq}
wait

# Convert to bam format
parallel --verbose -j ${n_files} echo {}.sam ">" {}.bam ::: ${fastq}
parallel --verbose -j ${n_files} samtools view -bS {}.sam ">" {}.bam ::: ${fastq}
wait

# Sort and index the bam files
parallel --verbose -j ${n_files} samtools sort {}.bam -o {}.sorted.bam ::: ${fastq}
wait
#
parallel --verbose -j ${n_files} samtools index {}.sorted.bam ::: ${fastq}
wait
parallel --verbose -j ${n_files} bedtools bamtobed -i {}.sorted.bam  ">" {}.bed ::: ${fastq}
wait
parallel --verbose -j ${n_files} samtools flagstat {}.sorted.bam ">" {}.stat ::: ${fastq}
wait


# # https://github.com/biod/sambamba/issues/177
# install sambamba: brew install brewsci/bio/sambamba

parallel --verbose -j ${n_files} sambamba markdup --overflow-list-size 600000  --tmpdir='./'  -r {}.sorted.bam  {}.rmdup.bam ::: ${fastq}
wait
parallel --verbose -j ${n_files} samtools index {}.rmdup.bam ::: ${fastq}
wait
#
# ## Calculate %mtDNA:
mtReads=$(parallel --verbose -j ${n_files} samtools idxstats  {}.rmdup.bam ::: ${fastq} "|" grep 'chrM' "|" cut -f 3)
totalReads=$(parallel --verbose -j ${n_files} samtools idxstats  {}.rmdup.bam ::: ${fastq} "|" awk '{SUM += $3} END {print SUM}')
echo '==> mtDNA Content:' $(bc <<< "scale=2;100*$mtReads/$totalReads")'%'

parallel --verbose -j ${n_files} samtools flagstat  {}.rmdup.bam ">" {}.rmdup.stat ::: ${fastq}
parallel --verbose -j ${n_files} samtools view  -h  -f 2 -q 30    {}.rmdup.bam   "|" grep -v chrM "|" samtools sort  -O bam  -@ 5 -o - ">" {}.last.bam ::: ${fastq}
parallel --verbose -j ${n_files} samtools index   {}.last.bam ::: ${fastq}
parallel --verbose -j ${n_files} samtools flagstat  {}.last.bam ">" {}.last.stat ::: ${fastq}
parallel --verbose -j ${n_files} bedtools bamtobed -i {}.last.bam  ">" {}.bed ::: ${fastq}
