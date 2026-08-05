#!/usr/bin/env python3
"""Regenerate the public large-file policy report."""

from __future__ import annotations

import json
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
THRESHOLD=10*1024*1024
LIMIT=100*1024*1024


def main()->None:
    rows=[]
    for path in sorted(p for p in ROOT.rglob("*") if p.is_file()):
        if any(part in {".git",".pytest_cache","__pycache__","site-preview"} for part in path.relative_to(ROOT).parts): continue
        if path.stat().st_size>THRESHOLD:
            rows.append({"path":path.relative_to(ROOT).as_posix(),"size_bytes":path.stat().st_size,"purpose":"public package artifact","required_publicly":False,"alternative":"exclude or publish as a separate release asset","release_asset":True,"lfs_candidate":False,"excluded":False})
    payload={"threshold_bytes":THRESHOLD,"hard_limit_bytes":LIMIT,"files":rows,"files_over_100_mib":sum(row["size_bytes"]>LIMIT for row in rows),"status":"PASS" if not any(row["size_bytes"]>LIMIT for row in rows) else "FAIL"}
    (ROOT/"LARGE_FILE_REPORT.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    lines=["# Large File Report","",f"**Status: {payload['status']}**","",f"Files larger than 10 MiB: {len(rows)}. Files larger than 100 MiB: {payload['files_over_100_mib']}.",""]
    if rows:
        lines.extend(["| Path | Size bytes | Publicly required | Alternative |","|---|---:|---|---|"])
        lines.extend(f"| `{row['path']}` | {row['size_bytes']} | no | separate release asset or exclude |" for row in rows)
    else: lines.append("No normal-tree file exceeds 10 MiB. No LFS configuration is required.")
    (ROOT/"LARGE_FILE_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(payload,indent=2))


if __name__=="__main__": main()
