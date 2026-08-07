from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_MANIFEST_FILES = {
    "DOCUMENT_VALIDATION.json",
    "EVIDENCE_MANIFEST_SHA256.json",
    "PUBLIC_REPOSITORY_VERIFICATION.json",
    "ROOT_MANIFEST_SHA256.json",
    "SOURCE_MANIFEST_SHA256.json",
}

def test_no_protected_media_extensions():
    forbidden = {".avi", ".mkv", ".mov", ".mp4", ".webm"}
    matches = [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in forbidden
    ]
    assert not matches


def test_public_images_are_generated_or_synthetic():
    images = [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and "site-preview" not in path.parts
        and "release" not in path.parts
        and path.suffix.lower() in {".gif", ".jpeg", ".jpg", ".png", ".webp"}
    ]
    for path in images:
        relative = path.relative_to(ROOT).as_posix()
        assert (
            relative.startswith("examples/synthetic/")
            or relative.startswith("docs/assets/generated/")
            or relative == "docs/figures/github-social-preview.png"
        )


def test_manifest_directory_has_only_public_outputs():
    manifests = ROOT / "manifests"
    actual = {path.name for path in manifests.iterdir() if path.is_file()}
    assert actual <= ALLOWED_MANIFEST_FILES
