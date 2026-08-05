#!/usr/bin/env python3
"""Copy the public tree into a fresh directory and run the public workflow."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path, env: dict[str, str]) -> dict:
    process = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
    return {"command": command, "returncode": process.returncode, "stdout": process.stdout[-2000:], "stderr": process.stderr[-2000:]}


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="retroz_s1_clean_room_") as temp:
        clean=Path(temp)/"repo"
        shutil.copytree(ROOT, clean, ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "site-preview", "release-bundle", "build", "dist"))
        install_site=Path(temp)/"install-site"
        env=os.environ.copy(); env["PYTHONPATH"]=str(install_site)
        commands=[
            [sys.executable,"-m","pip","install",".","--no-deps","--no-build-isolation","--target",str(install_site)],
            [sys.executable,"-m","compileall","-q",str(install_site/"retroz_s1")],
            [sys.executable,"-m","retroz_s1","--help"],
            [sys.executable,"-m","retroz_s1","list-candidates"],
            [sys.executable,"-m","retroz_s1","inspect","--candidate","D3"],
            [sys.executable,"scripts/generate_synthetic_demo.py"],
            [sys.executable,"-m","pytest","-q"],
            [sys.executable,"-m","retroz_s1","reproduce-failure","--candidate","A","--output","clean-output/a","--allow-rejected-research-candidate"],
            [sys.executable,"-m","retroz_s1","reproduce-failure","--candidate","C","--output","clean-output/c","--allow-rejected-research-candidate"],
            [sys.executable,"-m","retroz_s1","render","--candidate","B","--input","examples/synthetic/original_fixture.png","--output","clean-output/b.png","--allow-rejected-research-candidate"],
            [sys.executable,"-m","retroz_s1","render","--candidate","D3","--input","examples/synthetic/original_fixture.png","--output","clean-output/d3.png","--allow-rejected-research-candidate"],
            [sys.executable,"-m","retroz_s1","oracle-render","--input","examples/synthetic/original_fixture.png","--labels","examples/synthetic/oracle_labels.json","--method","P1","--tier","R0","--output","clean-output/oracle.png","--allow-rejected-research-candidate"],
            [sys.executable,"-m","retroz_s1","compare","--input","examples/synthetic/original_fixture.png","--candidates","B,D3","--output","clean-output/compare","--allow-rejected-research-candidate"],
            [sys.executable,"scripts/build_report.py"],
            [sys.executable,"scripts/build_docs.py"],
            [sys.executable,"scripts/validate_documents.py"],
            [sys.executable,"scripts/build_manifests.py"],
            [sys.executable,"scripts/verify_repository.py"],
        ]
        results=[run(command,clean,env) for command in commands]
        ok=all(row["returncode"]==0 for row in results)
    payload={"status":"PASS" if ok else "FAIL","historical_tree_available":False,"private_bundle_available":False,"protected_media_available":False,"commands":results}
    out=ROOT/"reports/CLEAN_ROOM_REPRODUCTION_REPORT.json"; out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    (ROOT/"manifests/CLEAN_ROOM_TEST_REPORT.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    lines=["# Clean-Room Reproduction Report","",f"**Status: {payload['status']}**","","The repository was copied into a fresh temporary directory. The historical research tree, private bundle, protected media, and private labels were unavailable.","","| Step | Result |","|---|---|"]
    for row in results:
        lines.append(f"| `{' '.join(row['command'][:4])}` | {'PASS' if row['returncode']==0 else 'FAIL'} |")
    docker_note="Docker verification is recorded in `DOCKER_REPRODUCTION_REPORT.md`." if (ROOT/"reports/DOCKER_REPRODUCTION_REPORT.md").is_file() else "Docker is reviewed separately because daemon and base-image availability are platform-dependent."
    lines.extend(["",docker_note])
    (ROOT/"reports/CLEAN_ROOM_REPRODUCTION_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(payload,indent=2)); return 0 if ok else 1


if __name__ == "__main__": raise SystemExit(main())
