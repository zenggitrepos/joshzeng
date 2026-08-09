from pathlib import Path

from src.platform_tools import ADCPlatformTools, TOOL_SCHEMAS


def test_tool_schemas_present():
    names = {x["function"]["name"] for x in TOOL_SCHEMAS}
    assert names == {"rank_adc_targets", "generate_target_plots", "inspect_target"}


def test_rank_tool(tmp_path: Path):
    tools = ADCPlatformTools("data", tmp_path)
    result = tools.rank_adc_targets("NSCLC")
    assert result["top_target"] == "TROP2"
    assert Path(result["ranking_csv"]).exists()
    assert Path(result["report_md"]).exists()


def test_plot_tool(tmp_path: Path):
    tools = ADCPlatformTools("data", tmp_path)
    result = tools.generate_target_plots("NSCLC", "TROP2")
    assert Path(result["expression_boxplot"]).exists()
    assert Path(result["cell_type_pie_chart"]).exists()
    assert Path(result["crispr_chronos_boxplot"]).exists()
