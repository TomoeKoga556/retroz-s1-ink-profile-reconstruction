#!/usr/bin/env python3
"""Build a deterministic local source archive and report bundle."""

from __future__ import annotations

import gzip
import hashlib
import json
import shutil
import tarfile
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release"
EXCLUDED_PARTS = {
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def version() -> str:
    payload = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(payload["project"]["version"])


def source_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)
    )


def main() -> None:
    project_version = version()
    RELEASE.mkdir(parents=True, exist_ok=True)
    archive = RELEASE / f"retroz-s1-{project_version}-source.tar.gz"
    report_source = ROOT / "reports/RETROZ_S1_INK_PROFILE_RECONSTRUCTION_REPORT.pdf"
    report_target = RELEASE / f"retroz-s1-{project_version}-report.pdf"

    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w") as tar:
                for path in source_files():
                    relative = path.relative_to(ROOT)
                    archive_path = Path(f"retroz-s1-{project_version}") / relative
                    info = tar.gettarinfo(str(path), str(archive_path))
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mtime = 0
                    with path.open("rb") as handle:
                        tar.addfile(info, handle)

    shutil.copyfile(report_source, report_target)
    manifest = {
        "version": project_version,
        "scientific_status": "PROVISIONAL_NO_OP",
        "source_archive": {
            "file": archive.name,
            "sha256": sha256(archive),
            "size_bytes": archive.stat().st_size,
        },
        "report": {
            "file": report_target.name,
            "sha256": sha256(report_target),
            "size_bytes": report_target.stat().st_size,
        },
        "protected_assets": 0,
    }
    manifest_path = RELEASE / f"retroz-s1-{project_version}-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    notes = f"""# RetroZ S1 {project_version}

Scientific status: **PROVISIONAL_NO_OP**.

This bundle contains the public source tree, synthetic demonstrations,
documentation, integrity manifests and generated report. No candidate is
production-approved, and no protected source image or private label set is
included.
"""
    (RELEASE / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
