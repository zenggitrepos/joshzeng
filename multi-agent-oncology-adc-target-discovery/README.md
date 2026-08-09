# Multi-Agent Oncology ADC Target Discovery

A deployable **LLM-supervised multi-agent platform** for oncology ADC target discovery. Users interact with the analysis through a **Streamlit chat interface**

The conversational orchestrator uses **OpenRouter's hosted Free Models Router** by default and exposes deterministic scientific tools for:

- literature evidence
- single-cell expression
- tumor-versus-normal selectivity
- CRISPR Chronos dependency
- protein / PLM-derived ADC features
- target ranking
- target-level visualizations

## Goal

The goal of this platform is to use **LLM-supervised multi-agent AI to integrate heterogeneous oncology evidence to prioritize ADC targets and biomarkers**. The platform coordinates specialized agents that evaluate literature support, single-cell expression, tumor-versus-normal selectivity, CRISPR dependency, and protein/PLM-derived features, then combines the evidence into an interpretable target ranking with supporting visualizations. It is designed as a reproducible framework that can be connected to larger public or proprietary datasets for translational target discovery.


## User experience

Start the web app with either:

```bash
python app.py
```

or:

```bash
streamlit run streamlit_app.py
```

Then open the URL shown by Streamlit and type requests such as:

```text
Rank ADC targets for NSCLC.
```

```text
Rank ADC targets for NSCLC and create plots for the top target.
```

```text
Explain the evidence for TROP2 in NSCLC and generate its plots.
```

The LLM decides whether to call:

- `rank_adc_targets`
- `inspect_target`
- `generate_target_plots`

The Streamlit UI renders the actual tool outputs as tables, evidence panels, and plots.

## Architecture

```text
Browser / Streamlit chat
          |
          v
OpenRouter Free Models Router
          |
          v
LLM tool-calling orchestrator
     /       |       \
    v        v        v
 Ranking  Inspection  Plots
    |        |         |
    +--------+---------+
             |
             v
    Scientific coordinator
             |
  +----------+-----------+-----------+-----------+
  |          |           |           |           |
Literature Single-cell Selectivity  CRISPR   Protein/PLM
  |          |           |           |           |
  +----------+-----------+-----------+-----------+
             |
             v
       ADC prioritization
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## OpenRouter configuration

Keep the API key on the **server**, not in browser-side code or GitHub.

```bash
export OPENROUTER_API_KEY="sk-or-v1-your-key"
export OPENROUTER_MODEL="openrouter/free"
export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
```

Then run:

```bash
python app.py
```

## Streamlit Community Cloud

Add these values to the app's **Secrets** settings:

```toml
OPENROUTER_API_KEY = "sk-or-v1-your-key"
OPENROUTER_MODEL = "openrouter/free"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_APP_NAME = "Multi-Agent Oncology ADC Target Discovery"
```

## Project layout

```text
.
├── streamlit_app.py          # browser chat UI
├── app.py                    # web-app launcher
├── cli_chat.py               # optional terminal chat client
├── Dockerfile
├── requirements.txt
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── data/
├── outputs/
├── src/
│   ├── chat_agent.py         # LLM tool-calling loop
│   ├── platform_tools.py     # deterministic tool API
│   ├── coordinator.py
│   ├── llm.py
│   ├── supervisor.py
│   ├── visualization.py
│   └── agents/
└── tests/
```
