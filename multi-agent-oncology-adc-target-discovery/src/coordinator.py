from pathlib import Path
from src.models import RankedTarget
from src.agents.literature import LiteratureAgent
from src.agents.single_cell import SingleCellAgent
from src.agents.selectivity import SelectivityAgent
from src.agents.crispr import CrisprAgent
from src.agents.protein import ProteinAgent
from src.supervisor import LLMSupervisor
class Coordinator:
 W={"literature":.15,"single_cell":.25,"tumor_normal_selectivity":.25,"crispr_dependency":.10,"protein_language_model":.25}
 def __init__(self,d):
  d=Path(d);self.agents={"literature":LiteratureAgent(d/'literature_corpus.csv'),"single_cell":SingleCellAgent(d/'single_cell_summary.csv'),"tumor_normal_selectivity":SelectivityAgent(d/'selectivity.csv',d/'tissue_expression_samples.csv'),"crispr_dependency":CrisprAgent(d/'crispr_summary.csv',d/'crispr_chronos_scores.csv'),"protein_language_model":ProteinAgent(d/'protein_features.csv')};self.supervisor=LLMSupervisor()
 def genes(self,c):return sorted(self.agents["literature"].df.query("cancer_type==@c").gene.unique())
 def rank(self,c):
  plan=self.supervisor.plan(c,self.genes(c)); out=[]
  for g in self.genes(c):
   res={n:self.agents[n].run(c,g) for n in plan.ordered_agents}; score=sum(self.W[n]*r.score for n,r in res.items()); rev=self.supervisor.review(c,g,res,score); out.append(RankedTarget(cancer_type=c,gene=g,adc_score=round(score,4),component_scores={n:round(r.score,4) for n,r in res.items()},summary=rev.final_summary,priority_call=rev.priority_call,strengths=rev.strengths,liabilities=rev.liabilities,contradictions=rev.contradictions,evidence=res))
  return sorted(out,key=lambda x:x.adc_score,reverse=True),plan
