#!/usr/bin/env python3
"""Build a deterministic local research release without publishing it."""

from __future__ import annotations

import gzip
import hashlib
import json
import shutil
import tarfile
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
RELEASE=ROOT/"release"
ARCHIVE=RELEASE/"RetroZ-S1-v0.1.0-research-source.tar.gz"
EXCLUDE={".git",".pytest_cache","__pycache__","site-preview","release","build","dist"}
EXCLUDE_FILES={"ROOT_MANIFEST_SHA256.json","PUBLIC_MANIFEST_SHA256.json"}


def sha(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()


def source_files()->list[Path]:
    return sorted(
        p
        for p in ROOT.rglob("*")
        if p.is_file()
        and p.name not in EXCLUDE_FILES
        and not any(part in EXCLUDE for part in p.relative_to(ROOT).parts)
    )


def main()->None:
    RELEASE.mkdir(parents=True,exist_ok=True)
    with ARCHIVE.open("wb") as raw:
        with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as zipped:
            with tarfile.open(fileobj=zipped,mode="w") as tar:
                for path in source_files():
                    arc=Path("retroz-s1-ink-profile-reconstruction")/path.relative_to(ROOT)
                    info=tar.gettarinfo(str(path),str(arc)); info.uid=info.gid=0; info.uname=info.gname=""; info.mtime=0
                    with path.open("rb") as handle: tar.addfile(info,handle)
    report=RELEASE/"RetroZ-S1-v0.1.0-research-report.pdf"
    shutil.copy2(ROOT/"reports/RETROZ_S1_INK_PROFILE_RECONSTRUCTION_REPORT.pdf",report)
    manifest={"release":"v0.1.0-research","scientific_status":"PROVISIONAL_NO_OP","published":False,"source_archive":{"file":ARCHIVE.name,"sha256":sha(ARCHIVE),"size_bytes":ARCHIVE.stat().st_size},"report":{"file":report.name,"sha256":sha(report),"size_bytes":report.stat().st_size},"protected_assets":0}
    (RELEASE/"RetroZ-S1-v0.1.0-reproducibility-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    notes='''# RetroZ S1 v0.1.0-research

Scientific status: **PROVISIONAL_NO_OP**.

This local, unpublished research release preserves clean-room candidate implementations, synthetic demonstrations, documentation, evaluation lessons, and negative results. No candidate is production-approved. No protected source image, private label set, raw session, remote, tag, or published release is included.

Manual review remains required for repository licensing, citation ownership, and final public presentation.
'''
    (RELEASE/"RELEASE_NOTES.md").write_text(notes,encoding="utf-8")
    print(json.dumps(manifest,indent=2))


if __name__=="__main__": main()
