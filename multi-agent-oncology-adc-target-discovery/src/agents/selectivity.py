import math,pandas as pd
from src.models import AgentResult
class SelectivityAgent:
 name="tumor_normal_selectivity"
 def __init__(self,p,e):self.df=pd.read_csv(p);self.expr=pd.read_csv(e)
 def run(self,c,g):
  r=self.df[(self.df.cancer_type==c)&(self.df.gene==g)].iloc[0]; ratio=(float(r.tumor_bulk_tpm)+.5)/(float(r.normal_critical_tissue_max_tpm)+.5); x=self.expr[(self.expr.cancer_type==c)&(self.expr.gene==g)]; mt=float(x[x.tissue_group=="Tumor"].expression_tpm.median()); mn=float(x[x.tissue_group=="Normal"].expression_tpm.median()); score=1-math.exp(-ratio/4)
  return AgentResult(gene=g,cancer_type=c,agent=self.name,score=min(1,score),rationale=f"Median tumor={mt:.2f} TPM; normal={mn:.2f} TPM; selectivity ratio={ratio:.2f}.",features={"selectivity_ratio":ratio,"median_tumor_expression":mt,"median_normal_expression":mn})
