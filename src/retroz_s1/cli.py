"""Unified command-line interface for the public RetroZ S1 package."""

from __future__ import annotations

import argparse
import importlib.resources
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from retroz_s1 import SCIENTIFIC_STATUS, __version__
from retroz_s1.candidates import b_runtime, d3_renderer, oracle_renderer
from retroz_s1.io import file_sha256, load_rgb, save_rgb, write_provenance
from retroz_s1.public_masks import public_masks
from retroz_s1.synthetic import reproduce_a, reproduce_c


REJECTED = {"A", "B", "C", "D3", "ORACLE"}


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def registry() -> dict:
    resource = importlib.resources.files("retroz_s1").joinpath("configs/candidate_registry.json")
    return json.loads(resource.read_text(encoding="utf-8"))


def candidate(candidate_id: str) -> dict:
    for item in registry()["candidates"]:
        if item["candidate_id"].upper() == candidate_id.upper():
            return item
    raise SystemExit(f"unknown candidate: {candidate_id}")


def acknowledge(args: argparse.Namespace, item: dict) -> None:
    print(f"Candidate {item['candidate_id']}: {item['status']}", file=sys.stderr)
    if item["candidate_id"] in REJECTED and not getattr(args, "allow_rejected_research_candidate", False):
        raise SystemExit("This candidate is rejected or historical. Re-run with --allow-rejected-research-candidate to acknowledge research-only use.")


def render_b(rgb: np.ndarray) -> tuple[np.ndarray, dict]:
    values = {name: float(expected) for name, expected in b_runtime._FROZEN_FLOAT_FIELDS}
    params = b_runtime.CandidateBParams(enabled=True, **values)
    output, diagnostics = b_runtime.apply_candidate_b(rgb, rgb, public_masks(rgb), params, return_diagnostics=True)
    return output, {"public_mask_approximation": True, "active_pixels": int(np.count_nonzero(diagnostics["mlsr_action"] > 0))}


def render_d3(rgb: np.ndarray) -> tuple[np.ndarray, dict]:
    output, diagnostics = d3_renderer.render_d3_r0(rgb, public_masks(rgb, for_d3=True))
    return np.array(output, copy=True), dict(diagnostics)


def run_render(args: argparse.Namespace) -> None:
    item = candidate(args.candidate)
    acknowledge(args, item)
    rgb = load_rgb(args.input)
    if item["candidate_id"] == "B":
        output, diagnostics = render_b(rgb)
    elif item["candidate_id"] == "D3":
        output, diagnostics = render_d3(rgb)
    else:
        raise SystemExit(f"Candidate {item['candidate_id']} is failure-reproduction only and is excluded from render")
    save_rgb(args.output, output)
    write_provenance(args.output, {"project_status": SCIENTIFIC_STATUS, "candidate": item, "input_sha256": file_sha256(args.input), "diagnostics": diagnostics, "warning": "Research-only output; not a recommended production filter."})


def run_compare(args: argparse.Namespace) -> None:
    rgb = load_rgb(args.input)
    images = [("INPUT", rgb)]
    for name in args.candidates.split(","):
        item = candidate(name.strip())
        acknowledge(args, item)
        if item["candidate_id"] == "B": out, _ = render_b(rgb)
        elif item["candidate_id"] == "D3": out, _ = render_d3(rgb)
        else: raise SystemExit(f"{item['candidate_id']} cannot render arbitrary user images")
        images.append((item["candidate_id"], out))
    h, w = rgb.shape[:2]
    canvas = Image.new("RGB", (w * len(images), h + 28), "black")
    from PIL import ImageDraw
    draw = ImageDraw.Draw(canvas)
    for index, (label, values) in enumerate(images):
        canvas.paste(Image.fromarray(np.uint8(np.clip(values, 0, 1) * 255 + 0.5), "RGB"), (index*w, 28))
        draw.text((index*w + 8, 8), label, fill="white")
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "comparison.png"
    canvas.save(path)
    write_provenance(path, {"project_status": SCIENTIFIC_STATUS, "candidates": args.candidates, "input_sha256": file_sha256(args.input)})


def run_oracle(args: argparse.Namespace) -> None:
    item = candidate("ORACLE")
    acknowledge(args, item)
    rgb = load_rgb(args.input)
    labels = json.loads(args.labels.read_text(encoding="utf-8"))
    segments = labels.get("segments")
    if not isinstance(segments, list) or not segments:
        raise SystemExit("Oracle labels must contain a non-empty segments list")
    hard = np.zeros(rgb.shape[:2], dtype=np.bool_)
    output, changed, diagnostics = oracle_renderer.render_oracle(rgb, segments, hard, method=args.method, tier=args.tier, fold=int(labels.get("fold", 0)))
    save_rgb(args.output, output)
    write_provenance(args.output, {"project_status": SCIENTIFIC_STATUS, "candidate": item, "method": args.method, "tier": args.tier, "input_sha256": file_sha256(args.input), "labels_sha256": file_sha256(args.labels), "changed_pixels": int(np.count_nonzero(changed)), "diagnostics": dict(diagnostics)})


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="python -m retroz_s1", description="RetroZ S1 research CLI. Current status: PROVISIONAL_NO_OP.")
    root.add_argument("--version", action="version", version=__version__)
    sub = root.add_subparsers(dest="command", required=True)
    sub.add_parser("list-candidates", help="List candidate status and capabilities")
    inspect = sub.add_parser("inspect", help="Inspect one candidate")
    inspect.add_argument("--candidate", required=True)
    render = sub.add_parser("render", help="Render a rejected research candidate on a user-owned image")
    render.add_argument("--candidate", required=True); render.add_argument("--input", type=Path, required=True); render.add_argument("--output", type=Path, required=True)
    render.add_argument("--allow-rejected-research-candidate", action="store_true")
    failure = sub.add_parser("reproduce-failure", help="Generate a public-safe synthetic failure reproduction")
    failure.add_argument("--candidate", required=True); failure.add_argument("--output", type=Path, required=True)
    failure.add_argument("--allow-rejected-research-candidate", action="store_true")
    compare = sub.add_parser("compare", help="Compare research candidates on a user-owned image")
    compare.add_argument("--input", type=Path, required=True); compare.add_argument("--candidates", required=True); compare.add_argument("--output", type=Path, required=True)
    compare.add_argument("--allow-rejected-research-candidate", action="store_true")
    oracle = sub.add_parser("oracle-render", help="Render with user-supplied contour labels")
    oracle.add_argument("--input", type=Path, required=True); oracle.add_argument("--labels", type=Path, required=True); oracle.add_argument("--method", choices=("P1","P2","P3"), required=True); oracle.add_argument("--tier", choices=("R0","R1","R3"), required=True); oracle.add_argument("--output", type=Path, required=True)
    oracle.add_argument("--allow-rejected-research-candidate", action="store_true")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "list-candidates":
        for item in registry()["candidates"]: print(f"{item['candidate_id']:8} {item['status']:22} {item['display_name']}")
    elif args.command == "inspect": print(json.dumps(candidate(args.candidate), indent=2))
    elif args.command == "render": run_render(args)
    elif args.command == "compare": run_compare(args)
    elif args.command == "oracle-render": run_oracle(args)
    elif args.command == "reproduce-failure":
        item = candidate(args.candidate); acknowledge(args, item)
        if item["candidate_id"] == "A": print(json.dumps(reproduce_a(args.output), indent=2))
        elif item["candidate_id"] == "C": print(json.dumps(reproduce_c(args.output), indent=2))
        else: raise SystemExit("This candidate uses synthetic-demo or render rather than reproduce-failure")
    return 0
