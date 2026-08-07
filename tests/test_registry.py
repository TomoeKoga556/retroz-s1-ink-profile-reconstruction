import json
from pathlib import Path

from retroz_s1.cli import candidate, registry


def test_registry_is_provisional_noop():
    data = registry()
    assert data["scientific_status"] == "PROVISIONAL_NO_OP"
    assert {item["candidate_id"] for item in data["candidates"]} == {
        "A",
        "B",
        "C",
        "D3",
        "ORACLE",
    }


def test_every_candidate_has_failure_and_status():
    for item in registry()["candidates"]:
        assert item["status"]
        assert item["known_failure"]
        assert item["actual_result"]


def test_lookup_is_case_insensitive():
    assert candidate("d3")["status"] == "REAL_EXACT_NO_OP"


def test_packaged_registry_matches_repository_registry():
    root = Path(__file__).resolve().parents[1]
    repository_registry = json.loads(
        (root / "configs/candidate_registry.json").read_text()
    )
    packaged_registry = json.loads(
        (root / "src/retroz_s1/configs/candidate_registry.json").read_text()
    )
    assert repository_registry == packaged_registry
