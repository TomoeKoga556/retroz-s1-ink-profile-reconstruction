#!/usr/bin/env python3
"""Build the MkDocs site in strict mode."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site-preview"


def main() -> None:
    command = [
        sys.executable,
        "-m",
        "mkdocs",
        "build",
        "--strict",
        "--site-dir",
        str(SITE),
    ]
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
