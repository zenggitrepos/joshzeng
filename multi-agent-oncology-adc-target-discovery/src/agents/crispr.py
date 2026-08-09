import pandas as pd
from src.models import AgentResult
class CrisprAgent:
 name="crispr_dependency"
 def __init__(self,p,ch):self.df=pd.read_csv(p);self.ch=pd.read_csv(ch)
 def run(self,c,g):
  r=self.df[(self.df.cancer_type==c)&(self.df.gene==g)].iloc[0]; effect=float(r.median_gene_effect); frac=float(r.fraction_dependent); score=.6*max(0,min(1,-effect))+.4*frac; x=self.ch[(self.ch.gene==g)&(self.ch.cancer_type==c)]
  return AgentResult(gene=g,cancer_type=c,agent=self.name,score=score,rationale=f"Median Chronos={effect:.2f}; dependent fraction={frac:.2f}.",features={"median_gene_effect":effect,"fraction_dependent":frac,"n_cell_lines":len(x)})
