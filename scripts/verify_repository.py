#!/usr/bin/env python3
"""Verify manifests, public assets, provenance and generated report state."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {"", ".cff", ".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}
PROTECTED_MEDIA = {".avi", ".mkv", ".mov", ".mp4", ".webm"}
IMAGE_EXTENSIONS = {".gif", ".jpeg", ".jpg", ".png", ".webp"}
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
FORBIDDEN_PATTERNS = [
    re.escape("/" + "home" + "/"),
    re.escape("/" + "mnt" + "/"),
    re.escape("." + "codex" + "/attachments/"),
    re.escape("codex" + "-sessions"),
    re.escape("cursor" + "_s1_"),
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
]
ALLOWED_MANIFEST_FILES = {
    "DOCUMENT_VALIDATION.json",
    "EVIDENCE_MANIFEST_SHA256.json",
    "PUBLIC_REPOSITORY_VERIFICATION.json",
    "ROOT_MANIFEST_SHA256.json",
    "SOURCE_MANIFEST_SHA256.json",
}
FORBIDDEN_PUBLIC_PATHS = {
    "GITHUB_METADATA.md",
    "SOURCE_OWNERSHIP_AUDIT.md",
    "docs/portfolio",
    "docs/research-history",
}

def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def skipped(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts)


def image_allowed(relative: str) -> bool:
    return (
        relative.startswith("examples/synthetic/")
        or relative.startswith("docs/assets/generated/")
        or relative == "docs/figures/github-social-preview.png"
    )


def verify_manifest(name: str) -> list[str]:
    errors: list[str] = []
    manifest_path = ROOT / "manifests" / name
    if not manifest_path.is_file():
        return [f"missing-manifest:{name}"]
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    for row in payload.get("entries", []):
        path = ROOT / row["path"]
        if not path.is_file():
            errors.append(f"missing:{row['path']}")
        elif sha256(path) != row["sha256"]:
            errors.append(f"hash:{row['path']}")
    return errors


def verify_registry() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    registry = json.loads(
        (ROOT / "configs/candidate_registry.json").read_text(encoding="utf-8")
    )
    if registry.get("scientific_status") != "PROVISIONAL_NO_OP":
        errors.append("scientific-status")

    for candidate in registry.get("candidates", []):
        candidate_id = candidate.get("candidate_id", "unknown")
        public_files = candidate.get("public_files", [])
        records = candidate.get("provenance_hashes", [])
        if [record.get("path") for record in records] != public_files:
            errors.append(f"provenance-paths:{candidate_id}")
            continue
        for record in records:
            path = ROOT / record["path"]
            if not path.is_file():
                errors.append(f"provenance-missing:{candidate_id}:{record['path']}")
            elif sha256(path) != record.get("sha256"):
                errors.append(f"provenance-hash:{candidate_id}:{record['path']}")
    return registry, errors


def main() -> int:
    errors: list[str] = []
    path_matches: list[str] = []
    images: list[str] = []
    symlinks: list[str] = []

    for forbidden in sorted(FORBIDDEN_PUBLIC_PATHS):
        if (ROOT / forbidden).exists():
            errors.append(f"public-clutter:{forbidden}")

    manifests = ROOT / "manifests"
    if manifests.is_dir():
        for path in manifests.iterdir():
            if path.is_file() and path.name not in ALLOWED_MANIFEST_FILES:
                errors.append(f"unexpected-manifest:{path.name}")

    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT).as_posix()
        if path.is_symlink():
            symlinks.append(relative)
        if not path.is_file() or skipped(path):
            continue

        suffix = path.suffix.lower()
        if suffix in PROTECTED_MEDIA:
            errors.append(f"protected-media:{relative}")
        if suffix in IMAGE_EXTENSIONS:
            images.append(relative)
            if not image_allowed(relative):
                errors.append(f"unapproved-image:{relative}")

        if suffix in TEXT_EXTENSIONS:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in FORBIDDEN_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    path_matches.append(f"{relative}:{pattern}")

    errors.extend(f"path-disclosure:{match}" for match in path_matches)
    errors.extend(f"symlink:{path}" for path in symlinks)
    for name in (
        "SOURCE_MANIFEST_SHA256.json",
        "EVIDENCE_MANIFEST_SHA256.json",
        "ROOT_MANIFEST_SHA256.json",
    ):
        errors.extend(verify_manifest(name))

    metadata_path = ROOT / "reports/REPORT_BUILD_METADATA.json"
    if not metadata_path.is_file():
        errors.append("missing-report-metadata")
    else:
        report = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not 8 <= int(report.get("pdf_pages", 0)) <= 30:
            errors.append("pdf-page-count")
        if report.get("author") != "Saif Shafique":
            errors.append("report-author")
        if report.get("version") != "0.1.0":
            errors.append("report-version")

    _, registry_errors = verify_registry()
    errors.extend(registry_errors)

    result = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "public_images": sorted(images),
        "protected_images": 0,
        "path_matches": path_matches,
        "symlinks": symlinks,
    }
    target = ROOT / "manifests/PUBLIC_REPOSITORY_VERIFICATION.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
