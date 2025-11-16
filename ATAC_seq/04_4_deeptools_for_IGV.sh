#!/bin/bash

#
out_dir="/out/dir/clean"
cd  ${out_dir}

REF='/REF/ChIP_ATAC_seq/ucsc_mm10.bed'
fastq_files=$(ls ${out_dir}/*.fq | rev | cut -d '/' -f 1 | rev | cut -d'_' -f 1 | uniq)
n_files=$(echo $fastq_files | wc -w)

fastq=$(echo ${fastq_files} | sed "s%[^ ]* *%$out_dir/&%g")

parallel --verbose -j ${n_files} bamCoverage -p 5 --normalizeUsing CPM -b {}.last.bam -o {}.last.bw ::: ${fastq}
wait
parallel --verbose -j ${n_files} bamCoverage -p 5 --normalizeUsing CPM -b {}.rmdup.bam -o {}.rmdup.bw ::: ${fastq}

parallel --verbose -j ${n_files} computeMatrix reference-point  --referencePoint TSS  -p 5 -b 10000 -a 10000 -R ${REF} -S {}.last.bw --skipZeros  -o matrix_{}_TSS.gz --outFileSortedRegions regions1_{}_genes.bed ::: ${fastq_files}
wait
##     both plotHeatmap and plotProfile will use the output from   computeMatrix

parallel --verbose -j ${n_files} plotHeatmap -m matrix_{}_TSS.gz  -out {}_Heatmap.pdf --plotFileFormat pdf  --dpi 720 ::: ${fastq_files}
wait

parallel --verbose -j ${n_files} plotProfile -m matrix_{}_TSS.gz  -out {}_Profile.pdf --plotFileFormat pdf --perGroup --dpi 720 ::: ${fastq_files}
wait

parallel --verbose -j ${n_files} computeMatrix scale-regions  -p 5  \
-R /media/joshu/seagate/data/perm/REF/ChIP_ATAC_seq/ucsc_mm10.bed  \
-S {}.last.bw  \
-b 10000 -a 10000  \
--skipZeros -o matrix_{}_body.gz ::: ${fastq_files}
wait

parallel --verbose -j ${n_files} plotHeatmap -m matrix_{}_body.gz  -out {}_Heatmap.png ::: ${fastq_files}
wait
parallel --verbose -j ${n_files} plotHeatmap -m matrix_{}_body.gz  -out {}_body_Heatmap.png ::: ${fastq_files}
wait
parallel --verbose -j ${n_files} plotProfile -m matrix_{}_body.gz  -out {}_body_Profile.png ::: ${fastq_files}
