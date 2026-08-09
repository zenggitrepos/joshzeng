import pandas as pd
from src.models import AgentResult
class LiteratureAgent:
 name="literature"
 def __init__(self,p):self.df=pd.read_csv(p)
 def run(self,c,g):
  x=self.df[(self.df.cancer_type==c)&(self.df.gene==g)]; ma=float(x.adc_relevance.mean()); mb=float(x.biomarker_relevance.mean()); score=min(1,.25*min(len(x)/4,1)+.4*ma+.35*mb)
  return AgentResult(gene=g,cancer_type=c,agent=self.name,score=score,rationale=f"Retrieved {len(x)} papers; ADC relevance={ma:.2f}; biomarker relevance={mb:.2f}.",features={"paper_count":len(x),"mean_adc_relevance":ma,"mean_biomarker_relevance":mb},supporting_items=[f"{r.title}: {r.abstract}" for _,r in x.iterrows()])
