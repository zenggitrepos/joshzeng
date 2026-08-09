from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.coordinator import Coordinator
from src.visualization import PlotGenerator


class ADCPlatformTools:
    """Deterministic scientific tools exposed to the LLM orchestrator."""

    def __init__(self, data_dir: str | Path = "data", out_dir: str | Path = "outputs"):
        self.data_dir = Path(data_dir)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def rank_adc_targets(self, cancer_type: str) -> dict[str, Any]:
        cancer_type = cancer_type.upper()
        coordinator = Coordinator(self.data_dir)
        ranking, _ = coordinator.rank(cancer_type)

        rows: list[dict[str, Any]] = []
        for i, target in enumerate(ranking, start=1):
            row = {
                "rank": i,
                "gene": target.gene,
                "adc_score": target.adc_score,
                "priority": target.priority_call,
                **target.component_scores,
            }
            rows.append(row)

        csv_path = self.out_dir / f"{cancer_type.lower()}_adc_ranking.csv"
        pd.DataFrame(rows).to_csv(csv_path, index=False)

        report_path = self.out_dir / f"{cancer_type.lower()}_report.md"
        report_lines = [
            f"# ADC target discovery report — {cancer_type}",
            "",
        ]
        for i, target in enumerate(ranking, start=1):
            report_lines.extend(
                [
                    f"## {i}. {target.gene}",
                    f"- ADC score: {target.adc_score:.3f}",
                    f"- Priority: {target.priority_call}",
                    f"- Summary: {target.summary}",
                    "- Strengths:",
                    *[f"  - {x}" for x in target.strengths],
                    "- Liabilities:",
                    *[f"  - {x}" for x in target.liabilities],
                ]
            )
            if target.contradictions:
                report_lines.extend(
                    ["- Contradictions:", *[f"  - {x}" for x in target.contradictions]]
                )
            report_lines.append("")
        report_path.write_text("\n".join(report_lines))

        return {
            "cancer_type": cancer_type,
            "top_target": rows[0]["gene"] if rows else None,
            "ranking": rows,
            "ranking_csv": str(csv_path),
            "report_md": str(report_path),
        }

    def generate_target_plots(self, cancer_type: str, gene: str) -> dict[str, Any]:
        cancer_type = cancer_type.upper()
        gene = gene.upper()
        plotter = PlotGenerator(self.data_dir)

        expression_path = self.out_dir / (
            f"{cancer_type.lower()}_{gene.lower()}_expression_boxplot.png"
        )
        cell_type_path = self.out_dir / (
            f"{cancer_type.lower()}_{gene.lower()}_cell_type_pie.png"
        )
        crispr_path = self.out_dir / f"{gene.lower()}_crispr_chronos_boxplot.png"

        plotter.expression_boxplot(gene, cancer_type, expression_path)
        plotter.cell_type_pie(gene, cancer_type, cell_type_path)
        plotter.crispr_boxplot(gene, crispr_path)

        return {
            "cancer_type": cancer_type,
            "gene": gene,
            "expression_boxplot": str(expression_path),
            "cell_type_pie_chart": str(cell_type_path),
            "crispr_chronos_boxplot": str(crispr_path),
        }

    def inspect_target(self, cancer_type: str, gene: str) -> dict[str, Any]:
        """Return the target's agent-level evidence without requiring the user to know agent names."""
        cancer_type = cancer_type.upper()
        gene = gene.upper()
        coordinator = Coordinator(self.data_dir)
        if gene not in coordinator.genes(cancer_type):
            raise ValueError(f"{gene} is not present in the candidate set for {cancer_type}")

        results = {
            name: agent.run(cancer_type, gene)
            for name, agent in coordinator.agents.items()
        }
        score = sum(coordinator.W[name] * result.score for name, result in results.items())
        return {
            "cancer_type": cancer_type,
            "gene": gene,
            "adc_score": round(float(score), 4),
            "agents": {name: result.model_dump() for name, result in results.items()},
        }


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "rank_adc_targets",
            "description": (
                "Rank candidate antibody-drug-conjugate targets for a supported cancer type "
                "using literature, single-cell expression, tumor-normal selectivity, CRISPR dependency, "
                "and protein/PLM evidence."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "cancer_type": {
                        "type": "string",
                        "enum": ["NSCLC", "CRC"],
                        "description": "Cancer type to analyze.",
                    }
                },
                "required": ["cancer_type"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_target_plots",
            "description": (
                "Generate three visualizations for one target: cancer-vs-normal expression boxplot, "
                "cell-type expression pie chart, and CRISPR Chronos boxplot across cancer types."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "cancer_type": {
                        "type": "string",
                        "enum": ["NSCLC", "CRC"],
                    },
                    "gene": {"type": "string", "description": "Target gene symbol."},
                },
                "required": ["cancer_type", "gene"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "inspect_target",
            "description": (
                "Inspect detailed evidence and component scores for a specific ADC target in a cancer type."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "cancer_type": {
                        "type": "string",
                        "enum": ["NSCLC", "CRC"],
                    },
                    "gene": {"type": "string", "description": "Target gene symbol."},
                },
                "required": ["cancer_type", "gene"],
                "additionalProperties": False,
            },
        },
    },
]
