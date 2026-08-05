#!/usr/bin/env python3
"""Validate structured documents, registry schema, and local Markdown links."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT=Path(__file__).resolve().parents[1]
ALLOWED_STATUS={"REJECTED_PRE_IMAGE","REJECTED_PRE_BINDING","SYNTHETIC_REJECT","REAL_STYLE_REJECT","REAL_NEAR_NO_OP","REAL_EXACT_NO_OP","ORACLE_NEAR_NO_OP","ORACLE_FEASIBILITY_ONLY","PROVISIONAL_NO_OP","HISTORICAL_ONLY"}
REQUIRED={"candidate_id","display_name","lineage","version","status","runnable_on_user_image","synthetic_reproducer_available","real_image_reproducer_available","requires_oracle_labels","requires_private_data","expected_behavior","actual_result","known_failure","scientific_interpretation","public_files","private_files","superseded_by","provenance_hashes"}


def main()->int:
    errors=[]; json_count=0; yaml_count=0; link_count=0
    for path in ROOT.rglob("*.json"):
        if any(part in {"site-preview","release"} for part in path.relative_to(ROOT).parts): continue
        try: json.loads(path.read_text(encoding="utf-8")); json_count+=1
        except Exception as exc: errors.append(f"json:{path.relative_to(ROOT)}:{exc}")
    for pattern in ("*.yaml","*.yml"):
        for path in ROOT.rglob(pattern):
            if any(part in {"site-preview","release"} for part in path.relative_to(ROOT).parts): continue
            try: yaml.safe_load(path.read_text(encoding="utf-8")); yaml_count+=1
            except Exception as exc: errors.append(f"yaml:{path.relative_to(ROOT)}:{exc}")
    registry=json.loads((ROOT/"configs/candidate_registry.json").read_text(encoding="utf-8"))
    for row in registry["candidates"]:
        missing=REQUIRED-set(row)
        if missing: errors.append(f"registry:{row.get('candidate_id')} missing {sorted(missing)}")
        if row.get("status") not in ALLOWED_STATUS: errors.append(f"registry:{row.get('candidate_id')} status")
    for path in ROOT.rglob("*.md"):
        if any(part in {"site-preview","release"} for part in path.relative_to(ROOT).parts): continue
        text=path.read_text(encoding="utf-8")
        for target in re.findall(r"!?(?:\[[^\]]*\])\(([^)]+)\)",text):
            target=target.strip().strip("<>").split("#",1)[0]
            if not target or "://" in target or target.startswith("mailto:"): continue
            link_count+=1
            if not (path.parent/target).resolve().exists(): errors.append(f"link:{path.relative_to(ROOT)}->{target}")
    result={"status":"PASS" if not errors else "FAIL","json_files":json_count,"yaml_files":yaml_count,"local_links":link_count,"errors":errors}
    (ROOT/"manifests/DOCUMENT_VALIDATION.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2)); return 0 if not errors else 1


if __name__=="__main__": raise SystemExit(main())
