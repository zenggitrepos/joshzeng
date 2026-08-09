from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel

from src.chat_agent import ADCChatAgent


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Natural-language OpenRouter agent for oncology ADC target discovery"
    )
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--out-dir", default="outputs")
    parser.add_argument(
        "--prompt",
        default=None,
        help="Optional one-shot natural-language prompt. Omit for interactive chat.",
    )
    args = parser.parse_args()

    console = Console()
    agent = ADCChatAgent(data_dir=args.data_dir, out_dir=args.out_dir)

    if not agent.llm.available:
        console.print(
            Panel.fit(
                "OpenRouter API key not found.\n\n"
                "Set it first:\n"
                "  export OPENROUTER_API_KEY='sk-or-v1-...'\n\n"
                "Then run:\n"
                "  python app.py",
                title="Configuration required",
            )
        )
        return

    if args.prompt:
        console.print(agent.ask(args.prompt))
        return

    console.print(
        Panel.fit(
            "Type an oncology ADC discovery request in natural language.\n"
            "Examples:\n"
            "• Rank ADC targets for NSCLC.\n"
            "• Rank ADC targets for NSCLC and create plots for the top target.\n"
            "• Explain the evidence for TROP2 in NSCLC and generate its plots.\n\n"
            "Type 'quit' to exit.",
            title="OpenRouter Multi-Agent ADC Discovery",
        )
    )

    while True:
        try:
            user_message = console.input("\n[bold cyan]You>[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nGoodbye.")
            break

        if user_message.lower() in {"quit", "exit", "q"}:
            console.print("Goodbye.")
            break
        if not user_message:
            continue

        try:
            answer = agent.ask(user_message)
            console.print(f"\n[bold green]Agent>[/bold green] {answer}")
        except Exception as exc:
            console.print(f"\n[bold red]Error:[/bold red] {exc}")


if __name__ == "__main__":
    main()
