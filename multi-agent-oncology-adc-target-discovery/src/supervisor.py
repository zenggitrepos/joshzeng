from __future__ import annotations

import json

from src.llm import OpenRouterFreeLLM
from src.models import SupervisorPlan, SupervisorReview


class LLMSupervisor:
    def __init__(self, llm=None):
        self.llm = llm or OpenRouterFreeLLM()

    def plan(self, cancer_type, genes):
        if self.llm.available:
            try:
                return self.llm.complete_json(
                    "You supervise an oncology ADC discovery multi-agent system.",
                    (
                        f"Cancer: {cancer_type}; genes: {genes}. Plan the workflow using exactly "
                        "these agent names: literature, single_cell, tumor_normal_selectivity, "
                        "crispr_dependency, protein_language_model."
                    ),
                    SupervisorPlan,
                )
            except Exception:
                pass
        return SupervisorPlan(
            goal=f"Rank ADC targets for {cancer_type}",
            ordered_agents=[
                "literature",
                "single_cell",
                "tumor_normal_selectivity",
                "crispr_dependency",
                "protein_language_model",
            ],
            notes="Use CRISPR as supportive rather than decisive evidence.",
        )

    def review(self, cancer_type, gene, results, score):
        if self.llm.available:
            try:
                return self.llm.complete_json(
                    "You are a conservative translational oncology supervisor.",
                    "Review this ADC target evidence. Identify strengths, liabilities, contradictions and priority.\n"
                    + json.dumps({k: v.model_dump() for k, v in results.items()}),
                    SupervisorReview,
                )
            except Exception:
                pass
        return self._fallback_review(cancer_type, gene, results, score)

    @staticmethod
    def _fallback_review(cancer_type, gene, results, score):
        sc = results["single_cell"]
        sel = results["tumor_normal_selectivity"]
        crispr = results["crispr_dependency"]
        protein = results["protein_language_model"]
        strengths = []
        liabilities = []
        contradictions = []

        if sel.score >= 0.6:
            strengths.append("Favorable tumor-normal selectivity.")
        else:
            liabilities.append("Selectivity may constrain therapeutic window.")
        if protein.score >= 0.85:
            strengths.append("Strong ADC-oriented protein features.")
        if sc.features["pct_tumor_cells_positive"] < 0.65:
            liabilities.append("Tumor-cell positivity is incomplete.")
        if crispr.score < 0.2:
            liabilities.append("CRISPR dependency support is weak.")
        if sc.score > 0.7 and sel.score < 0.45:
            contradictions.append(
                "Strong tumor-cell expression conflicts with weaker tumor-normal selectivity."
            )

        priority = "High" if score >= 0.72 else "Medium" if score >= 0.58 else "Low"
        return SupervisorReview(
            priority_call=priority,
            strengths=strengths or ["No dominant strength."],
            liabilities=liabilities or ["No major liability."],
            contradictions=contradictions,
            final_summary=(
                f"{gene} in {cancer_type}: {priority} priority with composite ADC score {score:.2f}."
            ),
        )
