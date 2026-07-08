

############## Melanoma single cell analysis    ##########

# Download Tabula Sapiens Single-Cell Dataset
# https://figshare.com/articles/dataset/Tabula_Sapiens_release_1_0/14267219
# https://tabula-sapiens-portal.ds.czbiohub.org/


###########  R packages ###################
required.packages <- c("Seurat", "dplyr", "SingleR", "celldex", "SingleCellExperiment",
                       "glue", 'readxl', 'cowplot', 'ggplot2', 'viridis', 'tidyr', 
                       'harmony', 'Azimuth', 'SeuratData', 'rio', 'Matrix', 'celldex', 'SingleR', 'scuttle', 'GEOquery') 


new.packages <- required.packages[!(required.packages %in% installed.packages()[,"Package"])]

if (!require("BiocManager", quietly = TRUE))
  install.packages("BiocManager")


if(length(new.packages) > 0 ) BiocManager::install(new.packages)

sapply(required.packages, function(pkg){suppressPackageStartupMessages(require(pkg, character.only = TRUE))})

########## Directories   ####################



############ Create Seurat Object if not present   ######
#########################################################

data.dir <- '/media/joshu/seagate/data/perm/scRNA_seq/human_refs'
  


