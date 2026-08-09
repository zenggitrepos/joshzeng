"""Convenience launcher for the Streamlit web application.

Local/server usage:
    python app.py

Equivalent command:
    streamlit run streamlit_app.py
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    port = os.getenv("PORT", "8501")
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(root / "streamlit_app.py"),
        "--server.address=0.0.0.0",
        f"--server.port={port}",
    ]
    try:
        raise_code = subprocess.call(command, cwd=root)
    except KeyboardInterrupt:
        raise_code = 0
    raise SystemExit(raise_code)


if __name__ == "__main__":
    main()
