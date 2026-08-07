#!/usr/bin/env python3
"""Validate structured documents, local links and release metadata."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from urllib.parse import unquote

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "release",
    "site-preview",
}
ALLOWED_STATUS = {
    "HISTORICAL_ONLY",
    "ORACLE_FEASIBILITY_ONLY",
    "ORACLE_NEAR_NO_OP",
    "PROVISIONAL_NO_OP",
    "REAL_EXACT_NO_OP",
    "REAL_NEAR_NO_OP",
    "REAL_STYLE_REJECT",
    "REJECTED_PRE_BINDING",
    "REJECTED_PRE_IMAGE",
    "SYNTHETIC_REJECT",
}
REQUIRED_CANDIDATE_FIELDS = {
    "actual_result",
    "candidate_id",
    "display_name",
    "expected_behavior",
    "known_failure",
    "lineage",
    "private_files",
    "provenance_hashes",
    "public_files",
    "real_image_reproducer_available",
    "requires_oracle_labels",
    "requires_private_data",
    "runnable_on_user_image",
    "scientific_interpretation",
    "status",
    "superseded_by",
    "synthetic_reproducer_available",
    "version",
}
STALE_PUBLIC_PHRASES = {
    "".join(("REPLACE", "_WITH_OWNER")),
    "".join(("cursor", "_s1_")),
    "".join(("0.1.0", "-research")),
}

def skipped(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts)


def local_markdown_targets(text: str) -> list[str]:
    targets = []
    for raw in re.findall(r"!?(?:\[[^\]]*\])\(([^)]+)\)", text):
        target = raw.strip().strip("<>")
        target = target.split(maxsplit=1)[0]
        target = unquote(target.split("#", 1)[0])
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        targets.append(target)
    return targets


def main() -> int:
    errors: list[str] = []
    json_count = 0
    yaml_count = 0
    link_count = 0

    for path in ROOT.rglob("*.json"):
        if skipped(path):
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
            json_count += 1
        except Exception as exc:  # noqa: BLE001 - report the parser error
            errors.append(f"json:{path.relative_to(ROOT)}:{exc}")

    for pattern in ("*.yaml", "*.yml", "*.cff"):
        for path in ROOT.rglob(pattern):
            if skipped(path):
                continue
            try:
                yaml.safe_load(path.read_text(encoding="utf-8"))
                yaml_count += 1
            except Exception as exc:  # noqa: BLE001 - report the parser error
                errors.append(f"yaml:{path.relative_to(ROOT)}:{exc}")

    registry = json.loads(
        (ROOT / "configs/candidate_registry.json").read_text(encoding="utf-8")
    )
    for row in registry["candidates"]:
        missing = REQUIRED_CANDIDATE_FIELDS - set(row)
        if missing:
            errors.append(
                f"registry:{row.get('candidate_id')} missing {sorted(missing)}"
            )
        if row.get("status") not in ALLOWED_STATUS:
            errors.append(f"registry:{row.get('candidate_id')} invalid status")

    for path in ROOT.rglob("*.md"):
        if skipped(path):
            continue
        text = path.read_text(encoding="utf-8")
        for target in local_markdown_targets(text):
            link_count += 1
            if not (path.parent / target).resolve().exists():
                errors.append(f"link:{path.relative_to(ROOT)}->{target}")

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project_version = str(pyproject["project"]["version"])
    package_text = (ROOT / "src/retroz_s1/__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', package_text, re.M)
    package_version = match.group(1) if match else None
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    citation_version = str(citation.get("version"))

    if len({project_version, package_version, citation_version}) != 1:
        errors.append(
            "version-mismatch:"
            f"pyproject={project_version},package={package_version},citation={citation_version}"
        )
    if pyproject["project"].get("authors") != [{"name": "Saif Shafique"}]:
        errors.append("pyproject:authors")
    authors = citation.get("authors")
    if not isinstance(authors, list) or not authors or not isinstance(authors[0], dict):
        errors.append("citation:authors must be a non-empty list of mappings")
    if citation.get("repository-code") != (
        "https://github.com/TomoeKoga556/retroz-s1-ink-profile-reconstruction"
    ):
        errors.append("citation:repository-code")
    if citation.get("license") != "Apache-2.0":
        errors.append("citation:license")

    for path in ROOT.rglob("*"):
        if not path.is_file() or skipped(path):
            continue
        if path.suffix.lower() not in {
            "",
            ".cff",
            ".json",
            ".md",
            ".py",
            ".toml",
            ".txt",
            ".yaml",
            ".yml",
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for phrase in STALE_PUBLIC_PHRASES:
            if phrase.casefold() in text.casefold():
                errors.append(f"stale-public-note:{path.relative_to(ROOT)}:{phrase}")

    result = {
        "status": "PASS" if not errors else "FAIL",
        "json_files": json_count,
        "yaml_files": yaml_count,
        "local_links": link_count,
        "version": project_version,
        "errors": errors,
    }
    target = ROOT / "manifests/DOCUMENT_VALIDATION.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
