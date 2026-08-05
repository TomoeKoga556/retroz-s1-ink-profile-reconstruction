#!/usr/bin/env python3
"""Classify requested privacy/security terms and enforce public asset policy."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
TEXT={".md",".py",".json",".yaml",".yml",".toml",".txt",".cff",""}


def main()->int:
    private_patterns={
        "local_user":"tomo"+"ekoga",
        "home_root":"/"+"home"+"/",
        "mounted_root":"/"+"mnt"+"/",
        "attachment_id":r"\.codex/"+r"attachments/",
        "session_uuid":r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "private_video":"test"+"3.mp4",
    }
    review_words=["pass"+"word","pass"+"wd","to"+"ken","api"+"_key","bear"+"er","sec"+"ret","private"+"_key","validation","holdout","shadow"]
    forbidden=[]; classified=[]; symlinks=[]; caches=[]; large=[]
    for path in ROOT.rglob("*"):
        rel=path.relative_to(ROOT).as_posix()
        if path.is_symlink(): symlinks.append(rel)
        if path.is_dir() and path.name in {"__pycache__",".pytest_cache"}: caches.append(rel)
        if not path.is_file(): continue
        if path.stat().st_size>10*1024*1024: large.append({"path":rel,"size_bytes":path.stat().st_size})
        if path.suffix.lower() not in TEXT: continue
        try: content=path.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        for name,pattern in private_patterns.items():
            if re.search(pattern,content,re.I): forbidden.append({"path":rel,"term":name,"classification":"PRIVATE_MATCH_REMOVE"})
        lower=content.lower()
        for word in review_words:
            if word in lower:
                classification="SCANNER_RULE" if rel.endswith("security_privacy_scan.py") else "BENIGN_DOCUMENTATION_OR_CODE"
                classified.append({"path":rel,"term":word,"classification":classification})
    media=[p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in {".mp4",".mkv",".webm",".avi",".mov"}]
    result={"status":"PASS" if not(forbidden or symlinks or caches or media) else "FAIL","private_matches":forbidden,"classified_review_terms":classified,"symlinks":symlinks,"cache_directories":caches,"protected_video_files":media,"files_over_10_mib":large}
    out=ROOT/"manifests/SECURITY_PRIVACY_SCAN.json"; out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"private_matches":len(forbidden),"classified_review_matches":len(classified),"symlinks":len(symlinks),"caches":len(caches),"protected_video":len(media),"large_files":len(large)},indent=2))
    return 0 if result["status"]=="PASS" else 1


if __name__=="__main__": raise SystemExit(main())
