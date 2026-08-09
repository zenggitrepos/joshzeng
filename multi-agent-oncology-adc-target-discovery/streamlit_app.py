from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src.chat_agent import ADCChatAgent


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def configure_openrouter_from_streamlit_secrets() -> None:
    """Allow Streamlit Cloud secrets or ordinary server environment variables."""
    try:
        secrets = st.secrets
    except Exception:
        return

    mappings = {
        "OPENROUTER_API_KEY": "OPENROUTER_API_KEY",
        "OPENROUTER_MODEL": "OPENROUTER_MODEL",
        "OPENROUTER_BASE_URL": "OPENROUTER_BASE_URL",
        "OPENROUTER_APP_NAME": "OPENROUTER_APP_NAME",
        "OPENROUTER_SITE_URL": "OPENROUTER_SITE_URL",
    }
    for secret_name, env_name in mappings.items():
        try:
            value = secrets.get(secret_name)
        except Exception:
            value = None
        if value and not os.getenv(env_name):
            os.environ[env_name] = str(value)


def get_agent() -> ADCChatAgent:
    if "adc_agent" not in st.session_state:
        st.session_state.adc_agent = ADCChatAgent(
            data_dir=str(DATA_DIR),
            out_dir=str(OUTPUT_DIR),
        )
    return st.session_state.adc_agent


def render_tool_result(record: dict[str, Any]) -> None:
    tool = record.get("tool")
    result = record.get("result", {})

    if "error" in result:
        st.error(f"{tool}: {result['error']}")
        return

    if tool == "rank_adc_targets":
        ranking = result.get("ranking", [])
        if ranking:
            st.subheader(f"ADC target ranking — {result.get('cancer_type', '')}")
            frame = pd.DataFrame(ranking)
            preferred = [
                "rank",
                "gene",
                "adc_score",
                "priority",
                "literature",
                "single_cell",
                "tumor_normal_selectivity",
                "crispr_dependency",
                "protein_language_model",
            ]
            cols = [c for c in preferred if c in frame.columns]
            st.dataframe(frame[cols], use_container_width=True, hide_index=True)

            csv_path = Path(result["ranking_csv"])
            if csv_path.exists():
                st.download_button(
                    "Download ranking CSV",
                    data=csv_path.read_bytes(),
                    file_name=csv_path.name,
                    mime="text/csv",
                    key=f"csv-{csv_path.name}-{len(st.session_state.messages)}",
                )

            report_path = Path(result["report_md"])
            if report_path.exists():
                st.download_button(
                    "Download analysis report",
                    data=report_path.read_bytes(),
                    file_name=report_path.name,
                    mime="text/markdown",
                    key=f"report-{report_path.name}-{len(st.session_state.messages)}",
                )
        return

    if tool == "generate_target_plots":
        st.subheader(f"Target visualizations — {result.get('gene', '')}")
        plots = [
            ("Tumor vs normal expression", result.get("expression_boxplot")),
            ("Expression by cell type", result.get("cell_type_pie_chart")),
            ("CRISPR Chronos scores across cancer types", result.get("crispr_chronos_boxplot")),
        ]
        for title, path_string in plots:
            if not path_string:
                continue
            path = Path(path_string)
            if path.exists():
                st.markdown(f"**{title}**")
                st.image(str(path), use_container_width=True)
                st.download_button(
                    f"Download {title.lower()}",
                    data=path.read_bytes(),
                    file_name=path.name,
                    mime="image/png",
                    key=f"plot-{path.name}-{len(st.session_state.messages)}",
                )
        return

    if tool == "inspect_target":
        st.subheader(f"Evidence details — {result.get('gene', '')} / {result.get('cancer_type', '')}")
        st.metric("Composite ADC score", f"{result.get('adc_score', 0):.3f}")
        agents = result.get("agents", {})
        for agent_name, evidence in agents.items():
            with st.expander(agent_name.replace("_", " ").title()):
                st.write(evidence.get("rationale", ""))
                st.write("**Score:**", round(float(evidence.get("score", 0)), 3))
                st.json(evidence.get("features", {}))
        return

    with st.expander(f"Tool result: {tool}"):
        st.json(result)


def main() -> None:
    st.set_page_config(
        page_title="Multi-Agent Oncology ADC Discovery",
        page_icon="🧬",
        layout="wide",
    )
    configure_openrouter_from_streamlit_secrets()

    st.title("Multi-Agent Oncology ADC Target Discovery")
    st.caption(
        "OpenRouter-powered conversational orchestration over literature, single-cell, "
        "tumor-normal selectivity, CRISPR dependency, and protein/PLM agents."
    )

    with st.sidebar:
        st.header("Platform")
        st.write("**LLM:** OpenRouter Free Models Router")
        st.code(os.getenv("OPENROUTER_MODEL", "openrouter/free"), language=None)
        st.write("**Cancer types:** NSCLC, CRC")
        if st.button("New conversation", use_container_width=True):
            if "adc_agent" in st.session_state:
                st.session_state.adc_agent.reset()
            st.session_state.messages = []
            st.rerun()

    agent = get_agent()

    if not agent.llm.available:
        st.error(
            "OpenRouter is not configured on this server. Set the server-side "
            "`OPENROUTER_API_KEY` environment variable or add it to Streamlit secrets."
        )
        st.code(
            'OPENROUTER_API_KEY="sk-or-v1-..."\n'
            'OPENROUTER_MODEL="openrouter/free"\n'
            'OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"',
            language="bash",
        )
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.write(
                "Ask me to rank ADC targets, inspect a target, or generate plots. "
                "For example: **Rank ADC targets for NSCLC and create plots for the top target.**"
            )

    # Keep the chat input near the middle/top of the page instead of pinned to the bottom.
    left, chat_col, right = st.columns([1, 2, 1])
    with chat_col:
        prompt = st.chat_input(
            "Ask an ADC target-discovery question",
            key="adc_chat_input",
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            for record in message.get("tool_results", []):
                render_tool_result(record)

    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Running the multi-agent analysis..."):
            try:
                answer = agent.ask(prompt)
                tool_results = list(agent.last_tool_results)
                st.markdown(answer)
                for record in tool_results:
                    render_tool_result(record)
            except Exception as exc:
                answer = f"Analysis failed: {exc}"
                tool_results = []
                st.error(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "tool_results": tool_results,
        }
    )


if __name__ == "__main__":
    main()
