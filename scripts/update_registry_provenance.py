#!/usr/bin/env python3
"""Bind public candidate entries to their minimal clean-room source closure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "configs/candidate_registry.json"


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> None:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    closures = {
        "A": ["src/retroz_s1/synthetic.py"],
        "B": ["src/retroz_s1/candidates/b_runtime.py", "src/retroz_s1/public_masks.py"],
        "C": ["src/retroz_s1/synthetic.py"],
        "D3": ["src/retroz_s1/geometry/contour_estimator.py", "src/retroz_s1/candidates/d3_renderer.py", "src/retroz_s1/public_masks.py"],
        "ORACLE": ["src/retroz_s1/candidates/oracle_core.py", "src/retroz_s1/candidates/oracle_renderer.py", "src/retroz_s1/candidates/oracle_exclusion.py"],
    }
    for item in payload["candidates"]:
        item["provenance_hashes"] = [{"path": path, "sha256": sha256(path)} for path in closures[item["candidate_id"]]]
    REGISTRY.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    yaml_text=yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    (ROOT / "configs/candidate_registry.yaml").write_text(yaml_text, encoding="utf-8")
    package_configs=ROOT/"src/retroz_s1/configs"; package_configs.mkdir(parents=True,exist_ok=True)
    (package_configs/"candidate_registry.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (package_configs/"candidate_registry.yaml").write_text(yaml_text, encoding="utf-8")
    print(json.dumps({"candidate_count": len(payload["candidates"]), "bound_files": sum(len(x) for x in closures.values())}, indent=2))


if __name__ == "__main__":
    main()
