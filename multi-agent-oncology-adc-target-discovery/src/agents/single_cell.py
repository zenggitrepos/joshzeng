import pandas as pd
from src.models import AgentResult
class SingleCellAgent:
 name="single_cell"
 def __init__(self,p):self.df=pd.read_csv(p)
 def run(self,c,g):
  r=self.df[(self.df.cancer_type==c)&(self.df.gene==g)].iloc[0]; tumor=float(r.tumor_epithelial_mean); off=float(max(r.immune_mean,r.stromal_mean)); pos=float(r.pct_tumor_cells_positive); score=.55*max(0,min(1,(tumor-off)/8))+.45*pos
  return AgentResult(gene=g,cancer_type=c,agent=self.name,score=score,rationale=f"Tumor epithelial={tumor:.2f}; off-tumor max={off:.2f}; positive fraction={pos:.2f}.",features={"tumor_epithelial_mean":tumor,"immune_mean":float(r.immune_mean),"stromal_mean":float(r.stromal_mean),"pct_tumor_cells_positive":pos})
