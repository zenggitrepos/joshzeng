from typing import Any, Literal
from pydantic import BaseModel, Field
class AgentResult(BaseModel):
    gene:str; cancer_type:str; agent:str; score:float=Field(ge=0,le=1); rationale:str; features:dict[str,Any]; supporting_items:list[str]=[]
class SupervisorPlan(BaseModel):
    goal:str; ordered_agents:list[str]; notes:str
class SupervisorReview(BaseModel):
    priority_call:Literal["High","Medium","Low"]; strengths:list[str]; liabilities:list[str]; contradictions:list[str]; final_summary:str
class RankedTarget(BaseModel):
    cancer_type:str; gene:str; adc_score:float; component_scores:dict[str,float]; summary:str; priority_call:str; strengths:list[str]; liabilities:list[str]; contradictions:list[str]; evidence:dict[str,AgentResult]
