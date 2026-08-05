import json
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]


def test_no_protected_media_extensions():
    forbidden={".mp4",".mkv",".webm",".avi",".mov"}
    assert not [p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in forbidden]


def test_public_images_are_generated_or_synthetic():
    images=[p for p in ROOT.rglob("*") if p.is_file() and "site-preview" not in p.parts and "release" not in p.parts and p.suffix.lower() in {".png",".jpg",".jpeg",".webp",".gif"}]
    assert all("examples/synthetic" in p.as_posix() or "docs/assets/generated" in p.as_posix() or p.name=="github-social-preview.png" for p in images)


def test_source_map_uses_sanitized_ids():
    mapping=json.loads((ROOT/"manifests/SOURCE_TO_DESTINATION_MAP.json").read_text())
    assert all(row["source_id"].startswith("source://") for row in mapping["entries"])
    serialized=json.dumps(mapping)
    assert ("/"+"home"+"/") not in serialized and ("/"+"mnt"+"/") not in serialized
