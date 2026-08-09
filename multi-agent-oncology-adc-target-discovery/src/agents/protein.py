import pandas as pd
from src.models import AgentResult
class ProteinAgent:
 name="protein_language_model"
 def __init__(self,p):self.df=pd.read_csv(p)
 def run(self,c,g):
  r=self.df[self.df.gene==g].iloc[0]; ks=["signal_peptide_prob","transmembrane_prob","extracellular_domain_score","plm_surfaceability_score","internalization_score"]; ws=[.15,.2,.25,.2,.2]; score=sum(w*float(r[k]) for w,k in zip(ws,ks))
  return AgentResult(gene=g,cancer_type=c,agent=self.name,score=score,rationale="ADC-oriented surfaceability/internalization score from PLM-derived features.",features={k:float(r[k]) for k in ks})
