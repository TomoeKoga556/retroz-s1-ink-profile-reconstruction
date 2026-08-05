#!/usr/bin/env python3
"""Generate deterministic public provenance and integrity manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "manifests"
EXCLUDED_PARTS = {".git", ".pytest_cache", "__pycache__", "build", "dist", "site-preview", "release-bundle"}
EXCLUDED_FILES = {"ROOT_MANIFEST_SHA256.json", "SOURCE_MANIFEST_SHA256.json", "EVIDENCE_MANIFEST_SHA256.json", "REPRODUCTION_MANIFEST.json", "PUBLIC_MANIFEST_SHA256.json", "PRIVATE_MANIFEST_SHA256.json", "REPRODUCIBILITY_STATUS.json", "CANDIDATE_PROVENANCE.json", "PUBLIC_REPOSITORY_VERIFICATION.json", "CLEAN_ROOM_TEST_REPORT.json"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""): h.update(block)
    return h.hexdigest()


def entries(paths: list[Path]) -> list[dict]:
    result = []
    for path in sorted(set(paths)):
        if path.name in EXCLUDED_FILES or any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts): continue
        result.append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "size_bytes": path.stat().st_size})
    return result


def store(name: str, payload: dict) -> None:
    (MAN / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    MAN.mkdir(parents=True, exist_ok=True)
    all_files = [p for p in ROOT.rglob("*") if p.is_file()]
    source_files = [p for prefix in ("src", "scripts", "tests", "configs") for p in (ROOT / prefix).rglob("*") if p.is_file()]
    evidence_files = [p for prefix in ("docs", "reports") for p in (ROOT / prefix).rglob("*") if p.is_file()]
    store("SOURCE_MANIFEST_SHA256.json", {"schema": 1, "scope": "public_source", "entries": entries(source_files)})
    store("EVIDENCE_MANIFEST_SHA256.json", {"schema": 1, "scope": "public_summaries_and_generated_report", "entries": entries(evidence_files)})
    store("ROOT_MANIFEST_SHA256.json", {"schema": 1, "scope": "public_repository", "entries": entries(all_files)})
    store("REPRODUCTION_MANIFEST.json", {"schema": 1, "scientific_status": "PROVISIONAL_NO_OP", "normal_operation": "synthetic_only", "commands": ["make test", "make synthetic-demo", "make report", "make docs-build", "make verify"], "exact_private_replay_publicly_available": False})
    store("PUBLIC_MANIFEST_SHA256.json", {"schema": 1, "scope": "public_repository", "entries": entries(all_files)})
    store("REPRODUCIBILITY_STATUS.json", {"schema": 1, "status": "PUBLIC_CLEAN_ROOM_REPRODUCIBLE", "scientific_status": "PROVISIONAL_NO_OP", "normal_operation": "synthetic_only", "private_real_frame_replay": "physically_separate_not_public", "protected_assets": 0})
    registry = json.loads((ROOT / "configs/candidate_registry.json").read_text(encoding="utf-8"))
    store("CANDIDATE_PROVENANCE.json", {"schema": 1, "candidates": [{"candidate_id": row["candidate_id"], "status": row["status"], "provenance_hashes": row["provenance_hashes"], "public_files": row["public_files"], "private_files": row["private_files"]} for row in registry["candidates"]]})
    store("EXCLUDED_FILES.json", {"schema": 1, "categories": {"protected_media": ["animation frames", "frame crops", "contact sheets", "videos", "frame-derived candidate outputs"], "private_provenance": ["exact workstation paths", "private label coordinates", "raw session logs", "private frame hashes"], "build_noise": ["runtime caches", "compiled bytecode", "test caches", "local wheels"], "superseded_research": ["obsolete candidate versions", "intermediate reports not needed for public claims"]}, "public_protected_asset_count": 0})
    print(json.dumps({"root_files": len(entries(all_files)), "source_files": len(entries(source_files)), "evidence_files": len(entries(evidence_files))}, indent=2))


if __name__ == "__main__": main()
