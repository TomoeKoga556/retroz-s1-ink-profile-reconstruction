import json
from pathlib import Path

from retroz_s1.cli import candidate, registry


def test_registry_is_provisional_noop():
    data=registry()
    assert data["scientific_status"] == "PROVISIONAL_NO_OP"
    assert {x["candidate_id"] for x in data["candidates"]} == {"A","B","C","D3","ORACLE"}


def test_every_candidate_has_failure_and_status():
    for item in registry()["candidates"]:
        assert item["status"]
        assert item["known_failure"]
        assert item["actual_result"]


def test_lookup():
    assert candidate("d3")["status"] == "REAL_EXACT_NO_OP"


def test_packaged_registry_matches_repository_registry():
    root=Path(__file__).resolve().parents[1]
    assert json.loads((root/"configs/candidate_registry.json").read_text()) == json.loads((root/"src/retroz_s1/configs/candidate_registry.json").read_text())
