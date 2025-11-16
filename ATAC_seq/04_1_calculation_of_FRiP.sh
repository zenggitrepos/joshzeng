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

ls *narrowPeak |while  read id;
do
echo $id >> FRiP_calcuation.txt
bed=$(basename $id "_peaks.narrowPeak").bed
#ls  -lh $bed
Reads=$(bedtools intersect -a $bed -b $id | wc -l | awk '{print $1}')
totalReads=$(wc -l $bed | awk '{print $1}')
echo "Reads =" $Reads  "totalReads =" $totalReads >> FRiP_calcuation.txt
echo 'FRiP value:' $(bc <<< "scale=2;100*$Reads/$totalReads")'%' >> FRiP_calcuation.txt
done
