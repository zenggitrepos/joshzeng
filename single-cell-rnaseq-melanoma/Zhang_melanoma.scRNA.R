

############## Melanoma single cell analysis    ##########

# Reference: https://www.nature.com/articles/s41467-022-34877-3
# 
# data source: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE215121
# 
# https://ftp.ncbi.nlm.nih.gov/geo/series/GSE215nnn/GSE215121/
#   
#   CHETAH tumor reference and input data: https://figshare.com/ndownloader/articles/6994007?private_link=aaf026376912366f81b6
# 
# https://nbisweden.github.io/excelerate-scRNAseq/session-celltypeid/celltypeid.html
# Set up

###########  R packages ###################
required.packages <- c("Seurat", "dplyr", "SingleR", "celldex", "SingleCellExperiment",
                       "glue", 'readxl', 'cowplot', 'ggplot2', 'viridis', 'tidyr', 
                       'harmony', 'Azimuth', 'SeuratData', 'rio', 'Matrix', 'celldex', 'SingleR', 'scuttle', 'GEOquery') 

# if(!requireNamespace('remotes', quietly = TRUE)){
#   install.packages('remotes')}
#   
# remotes::install_github('satijalab/azimuth', ref = 'master')
# devtools::install_github('satijalab/seurat-data')
# devtools::install_github("navinlabcode/copykat")
# devtools::install_github("satijalab/azimuth", "seurat5")

new.packages <- required.packages[!(required.packages %in% installed.packages()[,"Package"])]

if (!require("BiocManager", quietly = TRUE))
  install.packages("BiocManager")


if(length(new.packages) > 0 ) BiocManager::install(new.packages)

lapply(required.packages, function(pkg){suppressPackageStartupMessages(require(pkg, character.only = TRUE))})

########## Directories   ####################

data.dir <- "/media/josh/seagate/data/perm/scRNA_seq/Zhang_melanoma"

if(!dir.exists(data.dir)){
  dir.create(data.dir, recursive = T)
}

date.str <- "05132023"

project = 'melanoma'

nFeature_lower <- 250
nFeature_upper <- 10000
nCount_lower <- 1000
nCount_upper <- 100000
pMT_lower <- 0
pMT_upper <- 25
pHB_lower <- 0
pHB_upper <- 5


###### Download the data   ######
URL <- 'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE215nnn/GSE215121/suppl/GSE215121_RAW.tar'
file_name <- basename(URL)

if(!file.exists(glue('{data.dir}/{file_name}'))){
  system(sprintf("wget '%s' -P %s", URL, data.dir))
  system(sprintf('tar -xvf %s/%s -C %s', data.dir, file_name, data.dir))
  # system(glue('rm {data.dir}/{file_name}'))
}



URL <- 'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE215nnn/GSE215121/matrix/GSE215121-GPL20795_series_matrix.txt.gz'
file_name <- basename(URL)

if(!file.exists(glue('{data.dir}/{file_name}'))){
  system(sprintf("wget '%s' -P %s", URL, data.dir))
  # system(sprintf('tar -xvf %s/%s -C %s', data.dir, file_name, data.dir))
  # system(glue('rm {data.dir}/{file_name}'))
}

# Download skin single RNA-sea reference
URL <- 'https://figshare.com/ndownloader/files/34702012'
dest_path <- '/media/josh/seagate/data/perm/scRNA_seq/human_refs/TS_Skin.h5ad.zip'
file_dir <- dirname(dest_path)
if(!dir.exists(file_dir)){
  dir.create(file_dir, recursive = T)
}
file_name <- gsub('.zip', '', basename(dest_path))
if(!file.exists(glue('{file_dir}/{file_name}'))){
  download.file(URL, dest_path, method = 'wget')
  unzip(dest_path,exdir=file_dir)
  system(glue('rm {dest_path}'))
}


############ Create Seurat Object if not present   ######
#########################################################

if(!file.exists(glue('{data.dir}/Zhang_melanoma.rds'))){
  
  # Read reference data
  raw.data <- Read10X("/media/joshu/seagate/data/perm/scRNA_seq/human_refs/TS_Skin/matrix_files")
  meta <- read.csv("/media/joshu/seagate/data/perm/scRNA_seq/human_refs/TS_Skin/matrix_files/metadata.csv", row.names = 1)
  
  ref.obj <- CreateSeuratObject(raw.data)
  if(all(row.names(ref.obj@meta.data) == row.names(meta))){
    
    ref.obj <- AddMetaData(ref.obj, metadata = meta)
    
  }
  
  # ref.obj <- logNormCounts(ref.obj)
  ref.obj <- as.SingleCellExperiment(DietSeurat(ref.obj))
  
  ref.obj <- logNormCounts(ref.obj)
  
  dat <- GEOquery::getGEO(filename=glue('{data.dir}/GSE215121-GPL20795_series_matrix.txt.gz'),GSEMatrix = FALSE,getGPL = FALSE)
  
  meta <- pData(dat)
  
  pheno <- meta %>% select(title, geo_accession, source_name_ch1,  
                           'supplementary_file_1', 'genotype:ch1', 'tissue:ch1', 'treatment:ch1')
  
  
  pheno <- data.table::setnames(pheno, c('source_name_ch1', 'genotype:ch1', 'tissue:ch1', 'treatment:ch1'), 
                                c('Tissue_type', 'ca_subtypes', 'Tissue', 'Treatment')) %>% unique()
  
  # pheno$sample_name <- paste0(pheno$geo_accession, '_', pheno$title)
  # pheno$patient_id <- sapply(strsplit(pheno$title, '_'), '[', 1)
  # pheno$disease_type[pheno$Diagnosis == 'Lung adenocarcinoma'] <- 'LUAD'
  # pheno$disease_type[pheno$Diagnosis == 'Lung squamous cell carcinoma'] <- 'LUSC'
  # pheno$disease_type[pheno$Tissue_type == 'Adjacent normal'] <- 'Normal'
  # pheno$Tissue_type[pheno$Tissue_type == 'Adjacent normal'] <- 'Normal'
  # pheno$Tissue_type[pheno$Tissue_type == 'tumor'] <- 'Tumor'
  # pheno <- pheno %>% select(patient_id, geo_accession, Tissue_type, Sex, sample_name, disease_type, supplementary_file_1) %>% filter(patient_id == 'P2')
  
  pheno$Treatment <- gsub('with anti-PD1 treatment', 'Anti-PD1', pheno$Treatment)
  pheno$Treatment <- gsub('no-treatment', 'Untreated', pheno$Treatment)
  pheno$ca_subtypes <- gsub(' melanoma', '', pheno$ca_subtypes)
  
  
  
  create_seurat_object <- function(i){
    prj <- pheno$geo_accession[i]
    file_name <- basename(pheno$supplementary_file_1[i])
    # smp <- gsub('_processed_data.txt.gz', '', file_name)
    
    # file_dir <- glue('{data.dir}/{smp}/')
    
    # exp_mtx <- ReadMtx(
    #     mtx = glue("{file_dir}/matrix.mtx.gz"), 
    #     features = glue("{file_dir}/features.tsv.gz"),
    #     cells = glue("{file_dir}/barcodes.tsv.gz"), 
    #     skip.cell = 1, skip.feature = 1)
    # exp_mtx <- Read10X(data.dir = file_dir)
    
    # cnts <- read.table(glue('{data.dir}/{file_name}'), sep = "\t", row.names=1, header=T)
    # cnts <- Matrix(as.matrix(cnts), sparse=T)
    cnts <- Seurat::Read10X_h5(glue('{data.dir}/{file_name}'))
    
    # seurat_obj <- CreateSeuratObject(counts = exp_mtx, project = prj)
    seurat_obj <- CreateSeuratObject(counts = cnts, project = prj)
    
    return(seurat_obj)
    
  }
  
  seu_obj_list <- lapply(seq_along(pheno$geo_accession), create_seurat_object)
  # seu_obj_list <- lapply(1:3, create_seurat_object)
  
  gc()
  # seu_obj <- Reduce(function(x,y) merge(x,y, add.cell.ids = c(x@project.name, y@project.name)) , seu_obj_list )
  seu_obj <- merge(seu_obj_list[[1]], y = c(unlist(seu_obj_list))[2:length(seu_obj_list)], add.cell.ids = pheno$geo_accession, project = project)                        
  
  gc()
  ### calculate mitochondrial, hemoglobin and ribosomal gene counts
  seu_obj <- PercentageFeatureSet(seu_obj, pattern = "^MT-", col.name = "pMT")
  seu_obj <- PercentageFeatureSet(seu_obj, pattern = "^HBA|^HBB", col.name = "pHB")
  seu_obj <- PercentageFeatureSet(seu_obj, pattern = "^RPS|^RPL", col.name = "pRP")
  
  # Data Filtering 
  
  seu_obj_filtered <- subset(seu_obj, subset = nFeature_RNA > nFeature_lower & nFeature_RNA < nFeature_upper & pMT < pMT_upper )
  
  
  seu_obj_filtered
  
  meta_data <- seu_obj_filtered@meta.data
  meta_data$cells <- row.names(meta_data)
  
  pheno$supplementary_file_1 <- NULL
  meta_data <- merge(meta_data, pheno, by.x = 'orig.ident', by.y = 'geo_accession', all.x = T)
  row.names(meta_data) <- meta_data$cells
  meta_data$cells <- NULL
  
  
  if(all(row.names(meta_data) == row.names(seu_obj_filtered@meta.data))){
    
    seu_obj_filtered <- AddMetaData(object = seu_obj_filtered, meta = meta_data)
    
  }
  
  head(seu_obj_filtered@meta.data, 2)
  
  options(repr.plot.width = 15, repr.plot.height = 8)
  VlnPlot(seu_obj_filtered, features = c("nFeature_RNA", "nCount_RNA", "pMT"), ncol = 3)
  
  options(repr.plot.width = 7, repr.plot.height = 7)
  # Data normalization
  gc()
  seu_obj_filtered <- SCTransform(seu_obj_filtered, verbose = FALSE, vars.to.regress = c("nCount_RNA", "pMT"), conserve.memory = T)
  
  gc()
  # Dimensionality reduction
  seu_obj_filtered <- RunPCA(seu_obj_filtered, verbose = FALSE)
  
  seu_obj_filtered <- seu_obj_filtered %>% 
    RunHarmony("orig.ident", plot_convergence = FALSE, assay.use = "SCT", verbose = FALSE)
  
  # seu_obj_filtered <- RunUMAP(seu_obj_filtered, reduction = "harmony")
  seu_obj_filtered <- seu_obj_filtered %>% 
    RunUMAP(reduction = "harmony", dims = 1:20, verbose = FALSE) %>% 
    FindNeighbors(reduction = "harmony", dims = 1:20, verbose = FALSE)
  
  for (i in c(0.2, 0.3, 0.4, 0.5, 1, 2)) {
    seu_obj_filtered <- FindClusters(seu_obj_filtered, resolution = i, verbose = FALSE)
    print(DimPlot(seu_obj_filtered, reduction = "umap") + labs(title = paste0("resolution: ", i)))
  }
  
  rm(seu_obj_list, seu_obj)
  gc()
  
  sce <- as.SingleCellExperiment(DietSeurat(seu_obj_filtered))
  sce
  
  pred <- SingleR(test = sce, 
                  assay.type.test = 1, 
                  ref = ref.obj, 
                  labels = ref.obj$cell_ontology_class, 
                  BPPARAM = BiocParallel::MulticoreParam(parallel::detectCores()))
  
  # Add the annotated cell types to meta data of Seurat object
  seu_obj_filtered@meta.data$cell.type <- pred$pruned.labels
  
  saveRDS(seu_obj_filtered, glue('{data.dir}/Zhang_melanoma.rds'))
  
}else{seu_obj_filtered <- readRDS(glue('{data.dir}/Zhang_melanoma.rds'))
}



sorted_factors <- names(sort(table(seu_obj_filtered@meta.data$cell.type), 
                             decreasing = T))
seu_obj_filtered$cell.type <- factor(seu_obj_filtered$cell.type, levels = sorted_factors)

# options(repr.plot.width = 16, repr.plot.height = 8)

n_colors <- length(unique(seu_obj_filtered@meta.data$cell.type))
colors <- DiscretePalette(n_colors, palette = "glasbey")
DimPlot(seu_obj_filtered, group.by = "cell.type", label = FALSE,  cols = colors)

# options(repr.plot.width = 10, repr.plot.height = 5)

gene <- 'KREMEN1'

FeaturePlot(seu_obj_filtered, features = gene, split.by = 'ca_subtypes', pt.size = 0.5)

# CD5 on DCs brings antitumor T cell responses to life
# CD5 is essential for immune response?
gene <- 'CD5'
FeaturePlot(seu_obj_filtered, features = gene, split.by = 'ca_subtypes', pt.size = 0.5)

gene <- 'TRBV20-1'
FeaturePlot(seu_obj_filtered, features = gene, split.by = 'ca_subtypes', pt.size = 0.5)

gene <- 'SASH3'
FeaturePlot(seu_obj_filtered, features = gene, split.by = 'ca_subtypes', pt.size = 0.5)

gene <- 'TNFSF18'
FeaturePlot(seu_obj_filtered, features = gene, split.by = 'ca_subtypes', pt.size = 0.5)

# 
# FeaturePlot(seu_obj_filtered, features = gene, split.by = 'ca_subtypes', pt.size = 0.5)
FeaturePlot(seu_obj_filtered,  features = c("CD5", "SASH3"), pt.size = 0.3, blend = TRUE, blend.threshold = 0.5)


# FeaturePlot(seu_obj_filtered, features = gene, split.by = 'ca_subtypes', pt.size = 0.5)
FeaturePlot(seu_obj_filtered,  features = c("FOXP3", "CCR8"), pt.size = 0.5, blend = TRUE, blend.threshold = 0.5)


# options(repr.plot.width = 10, repr.plot.height = 5)
gene <- 'DLL3'
FeaturePlot(seu_obj_filtered, features = gene, split.by = 'ca_subtypes', pt.size = 0.5)

gene_exp <- GetAssayData(object = seu_obj_filtered, slot = "data")

# options(repr.plot.width = 9, repr.plot.height = 5)
# Idents(seu_obj_filtered)
cell.typs.filtered <- as.data.frame(table(seu_obj_filtered$cell.type), useNA = 'always') %>% filter(Freq > 100) %>% pull(Var1)
Idents(seu_obj_filtered) <- 'cell.type'
RidgePlot(subset(seu_obj_filtered, subset = cell.type %in% cell.typs.filtered), features = 'DLL3') +
  theme(legend.position = 'none')

gene_exp_sub <- gene_exp['DLL3', ] %>% as.data.frame()
names(gene_exp_sub) <- 'Gene_exp'
gene_exp_sub$Gene_cat <- ifelse((gene_exp_sub$Gene_exp > 0), 'Positive', 'Negative')


df = merge(seu_obj_filtered@meta.data, gene_exp_sub, by = 'row.names')
head(df, 3)

# options(repr.plot.width = 15, repr.plot.height = 6)

df.acral <- df %>% filter((ca_subtypes == 'acral') & (Gene_cat == 'Positive') ) %>% {table( .$cell.type, .$Gene_cat)} %>% 
  prop.table() %>% as.data.frame()
df.acral$ca_subtype <- 'Acral'

df.cutaneous <- df %>% filter((ca_subtypes == 'cutaneous') & (Gene_cat == 'Positive')) %>% {table( .$cell.type, .$Gene_cat)} %>% 
  prop.table() %>% as.data.frame() 
df.cutaneous$ca_subtype <- 'Cutaneous'

cell.sorted <- levels(df.cutaneous$cell.type)

plot.df <- rbind(df.acral, df.cutaneous) %>% filter(Var2 == 'Positive') %>% arrange(Freq) 
plot.df$Freq <- plot.df$Freq * 100
cell.sorted <- unique(plot.df$Var1)
plot.df$Var1 <- factor(plot.df$Var1, levels = cell.sorted)

ggplot(plot.df, aes(x = Var1, y = Freq)) +
  geom_bar(stat = 'identity', fill = 'royalblue') + facet_wrap(~ca_subtype) +
  coord_flip() +
  theme_bw() +
  theme(axis.text.x = element_text(size = 16),
        axis.text.y = element_text(size = 16),  
        axis.title.x = element_text( size = 18),
        axis.title.y = element_text(size = 18), 
        legend.position="none") +
  labs(title = 'DLL3 expression in acral and cutaneous melanoma',
       x = "",
       y = "Percentage (%)")

# options(repr.plot.width = 6, repr.plot.height = 5)
# df.melanoma <-
df.m1 <- df %>% filter((cell.type == 'melanocyte') & (ca_subtypes == 'acral')) %>% {table(.$Gene_cat)} %>%
  prop.table() %>% as.data.frame()
df.m1$ca_subtype <- 'Acral'

df.m2 <- df %>% filter((cell.type == 'melanocyte') & (ca_subtypes == 'cutaneous')) %>% {table(.$Gene_cat)} %>% 
  prop.table() %>% as.data.frame()
df.m2$ca_subtype <- 'Cutaneous'
plot.df2 <- rbind(df.m1, df.m2)
plot.df2$Freq <- round(plot.df2$Freq * 100, 0)

ggplot(plot.df2, aes(x = Var1, y = Freq, fill = ca_subtype, label = Freq)) +
  geom_bar(stat = 'identity') + facet_wrap(~ca_subtype) +
  geom_text(size = 5, position = position_stack(vjust = 0.5)) +
  scale_fill_manual(values=c( "tomato", "royalblue"))+
  # coord_flip() +
  theme_bw() +
  theme(axis.text.x = element_text(size = 16),
        axis.text.y = element_text(size = 16),  
        axis.title.x = element_text( size = 18),
        axis.title.y = element_text(size = 18), 
        plot.title = element_text(size=16),
        legend.position="none") +
  labs(title = 'DLL3 expression in acral and cutaneous melanoma',
       x = "DLL3 RNA expression",
       y = "Percentage (%)")

melanoma.dll3 <- df %>% filter((Gene_cat == 'Positive') & (cell.type == 'melanocyte'))
melanoma.dll3 <- melanoma.dll3$Row.names

df.co.exp <- gene_exp[, colnames(gene_exp) %in% melanoma.dll3]
gene_list <- rownames(df.co.exp) %>% unique()
gene_list <- gene_list[!gene_list %in% 'DLL3']

G <- 'CD5'
res.df <- NULL
for(i in 1:length(gene_list)){
  
  G_ <- gene_list[i]
  
  df.analysis <- df.co.exp[c(G, G_), ] %>% t()
  
  corr_test <- tryCatch({
    corr <- cor(df.analysis[, G], df.analysis[, G_], method = 'spearman')
    p <- cor.test(df.analysis[, G], df.analysis[, G_], method = 'spearman', exact = F)
    p <- p$p.value
    res <- data.frame(Gene = G, Gene2 = G_, Correlation = corr, p.Value = p)
    res.df <- rbind(res.df, res)
    
    # }, error = function(e) {})
  }, warning = function(w) {})
  
  
}

res.df %>% arrange(desc(Correlation)) %>% head(50)

# Gene      Gene2 Correlation       p.Value
# 1   CD5        CD5   1.0000000  0.000000e+00
# 2   CD5   TRBV20-1   0.3326734 1.495654e-269
# 3   CD5      SASH3   0.3139482 1.015421e-238
# 4   CD5  LINC02577   0.2716852 5.959460e-177
# 5   CD5  LINC00885   0.2358934 1.226161e-132
# 6   CD5    TNFSF18   0.2354662 3.758508e-132
# 7   CD5  MIR4432HG   0.2354662 3.758508e-132
# 8   CD5 AC095050.1   0.2354662 3.758508e-132
# 9   CD5      TIFAB   0.2354662 3.758508e-132
# 10  CD5     SMIM35   0.2354662 3.758508e-132
# 11  CD5     TRAV16   0.2354662 3.758508e-132
# 12  CD5     CD300C   0.2354662 3.758508e-132
# 13  CD5    PTPRCAP   0.2189069 4.801860e-114
# 14  CD5      GATA3   0.2067812 1.055747e-101
# 15  CD5      PTPRC   0.1986998  6.696780e-94
# 16  CD5       SIT1   0.1951250  1.480270e-90
# 17  CD5    CD200R1   0.1916422  2.322837e-87
# 18  CD5      S1PR4   0.1908650  1.176917e-86
# 19  CD5     CD40LG   0.1878459  6.014002e-84
# 20  CD5       CD3D   0.1734733  1.105871e-71
# 21  CD5   TNFRSF1B   0.1697806  1.067003e-68
# 22  CD5      IL2RG   0.1677779  4.154456e-67
# 23  CD5  TRAV23DV6   0.1662374  6.734691e-66
# 24  CD5      CELF3   0.1662215  6.930098e-66
# 25  CD5 AL031733.2   0.1662215  6.930098e-66
# 26  CD5      GPR25   0.1662215  6.930098e-66
# 27  CD5 AC068544.1   0.1662215  6.930098e-66
# 28  CD5     SUCNR1   0.1662215  6.930098e-66
# 29  CD5  SMAD1-AS1   0.1662215  6.930098e-66
# 30  CD5      S100Z   0.1662215  6.930098e-66
# 31  CD5 AC019155.3   0.1662215  6.930098e-66
# 32  CD5      MTMR7   0.1662215  6.930098e-66


