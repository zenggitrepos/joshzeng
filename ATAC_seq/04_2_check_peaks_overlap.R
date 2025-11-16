

##### Find the overlapping peaks between samples

out_dir <- "/out/dir/clean"
setwd(out_dir)

library(ChIPseeker)
library(ChIPpeakAnno)

# p_files <- list.files(out_dir, pattern = ".narrowPeak")
p_files <- list.files(out_dir, pattern = "2_peaks.narrowPeak")
overlaps <- function(i, j){
  if(i != j & i < j){
    f1 <- gsub("_peaks.narrowPeak", "", p_files[i])
    f2 <- gsub("_peaks.narrowPeak", "", p_files[j])
    peak1 <- readPeakFile(p_files[i])
    peak2 <- readPeakFile(p_files[j])
    ol <- findOverlapsOfPeaks(peak1, peak2)
    ol_cnt <- as.numeric(ol$venn_cnt[4, 3])
    cat("OverlapVenn between ", f1, " and", f2, " : ", ol_cnt, "\n",
        file = "overlapVenn_among_samples.txt",
        append = T)
    png(sprintf('overlapVenn_between_%s_and_%s.png', f1, f2))
    makeVennDiagram(ol)
    dev.off()
  }
}

for(I in c(1, 2, 3)){
  for(J in c(2, 3, 4)){
    overlaps(i = I, j = J)
  }
}
