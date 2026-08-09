from __future__ import annotations

import json
from typing import Any

from src.llm import OpenRouterFreeLLM
from src.platform_tools import ADCPlatformTools, TOOL_SCHEMAS


SYSTEM_PROMPT = """
You are the LLM orchestrator for an oncology ADC target-discovery platform.
The user speaks in natural language. Decide which scientific platform tools to call.

Supported cancer types: NSCLC and CRC.
Available capabilities:
1. Rank ADC targets for a cancer type.
2. Inspect detailed agent evidence for a target.
3. Generate target plots: tumor-vs-normal expression boxplot, cell-type pie chart,
   and CRISPR Chronos boxplot across cancer types.

Important behavior:
- Use tools whenever the user asks for analysis, ranking, evidence, or plots.
- Do not invent numerical results. Numerical results must come from tools.
- If the user asks for plots for "the top target", call rank_adc_targets first, then use
  the returned top_target in generate_target_plots.
- Keep the final response concise and mention what was analyzed.
""".strip()


class ADCChatAgent:
    """Natural-language OpenRouter agent that chooses and executes platform tools."""

    def __init__(
        self,
        data_dir: str = "data",
        out_dir: str = "outputs",
        llm: OpenRouterFreeLLM | None = None,
        max_tool_rounds: int = 5,
    ):
        self.llm = llm or OpenRouterFreeLLM()
        self.tools = ADCPlatformTools(data_dir=data_dir, out_dir=out_dir)
        self.max_tool_rounds = max_tool_rounds
        self.history: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        # Exposed to the web UI so it can render tables and plots from deterministic
        # tool outputs rather than trying to parse natural-language LLM responses.
        self.last_tool_results: list[dict[str, Any]] = []

    def ask(self, user_message: str) -> str:
        if not self.llm.available:
            raise RuntimeError(
                "OpenRouter API key is not configured on the server. Set OPENROUTER_API_KEY."
            )

        self.last_tool_results = []
        self.history.append({"role": "user", "content": user_message})

        for _ in range(self.max_tool_rounds):
            response = self.llm.chat_with_tools(self.history, TOOL_SCHEMAS)
            message = response.choices[0].message
            self.history.append(self._assistant_message_to_dict(message))

            tool_calls = message.tool_calls or []
            if not tool_calls:
                return message.content or "Analysis completed."

            for tool_call in tool_calls:
                name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                    result = self._execute_tool(name, arguments)
                    record = {"tool": name, "arguments": arguments, "result": result}
                except Exception as exc:
                    result = {"error": str(exc), "tool": name}
                    record = {"tool": name, "arguments": {}, "result": result}

                self.last_tool_results.append(record)
                self.history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": json.dumps(result, default=str),
                    }
                )

        raise RuntimeError("Maximum tool-call rounds reached before a final answer was produced.")

    def reset(self) -> None:
        """Clear conversational memory while preserving the system prompt."""
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.last_tool_results = []

    def _execute_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "rank_adc_targets":
            return self.tools.rank_adc_targets(**arguments)
        if name == "generate_target_plots":
            return self.tools.generate_target_plots(**arguments)
        if name == "inspect_target":
            return self.tools.inspect_target(**arguments)
        raise ValueError(f"Unknown platform tool: {name}")

    @staticmethod
    def _assistant_message_to_dict(message) -> dict[str, Any]:
        data: dict[str, Any] = {
            "role": "assistant",
            "content": message.content,
        }
        if message.tool_calls:
            data["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]
        return data
