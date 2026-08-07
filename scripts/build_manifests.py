#!/usr/bin/env python3
"""Build the three public SHA-256 manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "manifests"
SKIP_PARTS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "manifests",
    "release",
    "site-preview",
}

def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return path.is_file() and not any(part in SKIP_PARTS for part in relative.parts)


def entries(paths: list[Path]) -> list[dict[str, object]]:
    return [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": digest(path),
            "size_bytes": path.stat().st_size,
        }
        for path in sorted(set(paths))
        if included(path)
    ]


def store(name: str, scope: str, rows: list[dict[str, object]]) -> None:
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    payload = {"schema": 1, "scope": scope, "entries": rows}
    (MANIFESTS / name).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    MANIFESTS.mkdir(parents=True, exist_ok=True)

    source_files = [
        path
        for prefix in ("src", "scripts", "tests", "configs")
        for path in (ROOT / prefix).rglob("*")
        if path.is_file()
    ]
    evidence_files = [
        path
        for prefix in ("docs", "reports")
        for path in (ROOT / prefix).rglob("*")
        if path.is_file()
    ]
    repository_files = [path for path in ROOT.rglob("*") if path.is_file()]

    source_rows = entries(source_files)
    evidence_rows = entries(evidence_files)
    repository_rows = entries(repository_files)

    store(
        "SOURCE_MANIFEST_SHA256.json",
        "public_source_tests_and_configuration",
        source_rows,
    )
    store(
        "EVIDENCE_MANIFEST_SHA256.json",
        "public_documentation_and_generated_reports",
        evidence_rows,
    )
    store(
        "ROOT_MANIFEST_SHA256.json",
        "public_repository_excluding_generated_manifests",
        repository_rows,
    )

    print(
        json.dumps(
            {
                "root_files": len(repository_rows),
                "source_files": len(source_rows),
                "evidence_files": len(evidence_rows),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
