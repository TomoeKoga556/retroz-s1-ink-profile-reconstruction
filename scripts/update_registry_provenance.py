#!/usr/bin/env python3
"""Refresh candidate source hashes and packaged registry copies."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "configs/candidate_registry.json"
PUBLIC_FILES = {
    "A": ("src/retroz_s1/synthetic.py",),
    "B": (
        "src/retroz_s1/candidates/b_runtime.py",
        "src/retroz_s1/public_masks.py",
    ),
    "C": ("src/retroz_s1/synthetic.py",),
    "D3": (
        "src/retroz_s1/geometry/contour_estimator.py",
        "src/retroz_s1/candidates/d3_renderer.py",
        "src/retroz_s1/public_masks.py",
    ),
    "ORACLE": (
        "src/retroz_s1/candidates/oracle_core.py",
        "src/retroz_s1/candidates/oracle_renderer.py",
        "src/retroz_s1/candidates/oracle_exclusion.py",
    ),
}


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def inline_yaml(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if value == []:
        return "[]"
    if value == {}:
        return "{}"
    raise TypeError(f"cannot render {type(value).__name__} inline")


def is_inline(value: Any) -> bool:
    if value is None or isinstance(value, (bool, int, float, str)):
        return True
    return isinstance(value, (list, dict)) and not value


def yaml_lines(value: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if is_inline(item):
                lines.append(f"{prefix}{key}: {inline_yaml(item)}")
            else:
                lines.append(f"{prefix}{key}:")
                lines.extend(yaml_lines(item, indent + 2))
        return lines
    if isinstance(value, list):
        lines = []
        for item in value:
            if is_inline(item):
                lines.append(f"{prefix}- {inline_yaml(item)}")
            else:
                lines.append(f"{prefix}-")
                lines.extend(yaml_lines(item, indent + 2))
        return lines
    return [f"{prefix}{inline_yaml(value)}"]


def write_registry(payload: dict[str, Any], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    yaml_text = "\n".join(yaml_lines(payload)) + "\n"
    (directory / "candidate_registry.json").write_text(json_text, encoding="utf-8")
    (directory / "candidate_registry.yaml").write_text(yaml_text, encoding="utf-8")


def main() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    rows = payload.get("candidates")
    if not isinstance(rows, list):
        raise SystemExit("candidate registry has no candidates list")

    actual_ids = [row.get("candidate_id") for row in rows]
    expected_ids = list(PUBLIC_FILES)
    if actual_ids != expected_ids:
        raise SystemExit(
            f"candidate order differs: expected {expected_ids}, received {actual_ids}"
        )

    for row in rows:
        candidate_id = row["candidate_id"]
        expected_paths = PUBLIC_FILES[candidate_id]
        declared_paths = tuple(row.get("public_files", ()))
        if declared_paths != expected_paths:
            raise SystemExit(
                f"{candidate_id} public_files differ: "
                f"expected {expected_paths}, received {declared_paths}"
            )

        provenance = []
        for relative in expected_paths:
            path = ROOT / relative
            if not path.is_file():
                raise SystemExit(f"missing public source for {candidate_id}: {relative}")
            provenance.append({"path": relative, "sha256": sha256(path)})
        row["provenance_hashes"] = provenance

    write_registry(payload, ROOT / "configs")
    write_registry(payload, ROOT / "src/retroz_s1/configs")
    print(
        json.dumps(
            {
                "status": "updated",
                "candidates": expected_ids,
                "hashed_files": sum(len(paths) for paths in PUBLIC_FILES.values()),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
