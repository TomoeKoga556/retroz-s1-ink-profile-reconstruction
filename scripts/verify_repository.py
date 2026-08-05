#!/usr/bin/env python3
"""Verify manifests, policy, path privacy, and generated report consistency."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_EXT = {".md", ".py", ".json", ".yaml", ".yml", ".toml", ".txt", ".cff", ""}
FORBIDDEN = ["/" + "home" + "/", "/" + "mnt" + "/", "tomo" + "ekoga", r"\.codex/" + "attachments/", "codex-" + "sessions", r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"]
PROTECTED_MEDIA = {".mp4", ".mkv", ".webm", ".avi", ".mov"}
ALLOWED_IMAGES = {"examples/synthetic/original_fixture.png", "examples/synthetic/candidate_b.png", "examples/synthetic/candidate_d3.png", "examples/synthetic/oracle_p1_r0.png", "examples/synthetic/failure_c/source.png", "examples/synthetic/failure_c/psf_output.png", "docs/assets/generated/candidate-comparison.png", "docs/assets/generated/oracle-delta.png", "docs/figures/github-social-preview.png", "github-social-preview.png"}


def sha(path: Path) -> str:
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()


def verify_manifest(name: str) -> list[str]:
    errors=[]; payload=json.loads((ROOT/"manifests"/name).read_text(encoding="utf-8"))
    for row in payload["entries"]:
        path=ROOT/row["path"]
        if not path.is_file(): errors.append(f"missing:{row['path']}")
        elif sha(path)!=row["sha256"]: errors.append(f"hash:{row['path']}")
    return errors


def main() -> int:
    errors=[]; privacy=[]; images=[]; symlinks=[]
    for path in ROOT.rglob("*"):
        rel=path.relative_to(ROOT).as_posix()
        if path.is_symlink(): symlinks.append(rel)
        if not path.is_file() or any(x in path.parts for x in (".pytest_cache", "__pycache__", "site-preview", "release-bundle", "clean-output")): continue
        if path.suffix.lower() in PROTECTED_MEDIA: errors.append(f"protected-media:{rel}")
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}: images.append(rel)
        if path.suffix.lower() in TEXT_EXT:
            try: text=path.read_text(encoding="utf-8")
            except UnicodeDecodeError: continue
            for pattern in FORBIDDEN:
                if re.search(pattern, text, re.I): privacy.append(f"{rel}:{pattern}")
    unexpected=sorted(set(images)-ALLOWED_IMAGES)
    if unexpected: errors.extend(f"unapproved-image:{x}" for x in unexpected)
    errors.extend(f"privacy:{x}" for x in privacy)
    errors.extend(f"symlink:{x}" for x in symlinks)
    for name in ("SOURCE_MANIFEST_SHA256.json", "EVIDENCE_MANIFEST_SHA256.json"):
        errors.extend(verify_manifest(name))
    report=json.loads((ROOT/"reports/REPORT_BUILD_METADATA.json").read_text(encoding="utf-8"))
    if not 35 <= int(report["pdf_pages"]) <= 70: errors.append("pdf-page-count")
    status=json.loads((ROOT/"configs/candidate_registry.json").read_text(encoding="utf-8"))["scientific_status"]
    if status != "PROVISIONAL_NO_OP": errors.append("scientific-status")
    result={"status":"PASS" if not errors else "FAIL", "errors":errors, "public_images":sorted(images), "protected_images":0, "privacy_matches":privacy, "symlinks":symlinks}
    (ROOT/"manifests/PUBLIC_REPOSITORY_VERIFICATION.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2)); return 0 if not errors else 1


if __name__ == "__main__": raise SystemExit(main())
