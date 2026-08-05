#!/usr/bin/env python3
"""Build a dependency-free static documentation preview."""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site-preview"


def render_markdown(source: Path) -> str:
    lines = source.read_text(encoding="utf-8").splitlines()
    out, in_code = [], False
    for raw in lines:
        if raw.startswith("```"):
            out.append("</code></pre>" if in_code else "<pre><code>"); in_code = not in_code; continue
        escaped = html.escape(raw)
        if in_code: out.append(escaped); continue
        if raw.startswith("### "): out.append(f"<h3>{html.escape(raw[4:])}</h3>")
        elif raw.startswith("## "): out.append(f"<h2>{html.escape(raw[3:])}</h2>")
        elif raw.startswith("# "): out.append(f"<h1>{html.escape(raw[2:])}</h1>")
        elif raw.startswith("- "): out.append(f"<li>{html.escape(raw[2:])}</li>")
        elif raw.strip(): out.append(f"<p>{escaped}</p>")
    return "\n".join(out)


def main() -> None:
    if SITE.exists(): shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    pages = sorted(p for p in DOCS.glob("*.md"))
    nav = " ".join(f'<a href="{p.stem}.html">{html.escape(p.stem.replace("-", " ").title())}</a>' for p in pages)
    css = "body{font-family:system-ui;max-width:980px;margin:auto;padding:2rem;color:#dfe7f1;background:#08111f;line-height:1.65}a{color:#75d4d2;margin-right:1rem}h1,h2{color:#fff}pre{background:#111d2d;padding:1rem;overflow:auto}p{max-width:75ch}.status{color:#ffcb69}"
    for page in pages:
        body = render_markdown(page)
        document = f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>RetroZ S1 · {page.stem}</title><style>{css}</style></head><body><nav>{nav}</nav><main>{body}</main></body></html>'
        (SITE / f"{page.stem}.html").write_text(document, encoding="utf-8")
    (SITE / "index.html").write_text((SITE / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
    assets = DOCS / "assets"
    if assets.exists(): shutil.copytree(assets, SITE / "assets")
    print(json.dumps({"builder": "dependency-free fallback", "pages": len(pages), "site": str(SITE)}, indent=2))


if __name__ == "__main__": main()
