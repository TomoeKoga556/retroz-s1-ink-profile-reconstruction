import pytest
from retroz_s1.cli import main


def test_list_candidates(capsys):
    assert main(["list-candidates"]) == 0
    assert "PROVISIONAL" not in capsys.readouterr().out


def test_inspect(capsys):
    assert main(["inspect","--candidate","B"]) == 0
    assert "REAL_NEAR_NO_OP" in capsys.readouterr().out


def test_rejected_requires_ack(tmp_path):
    with pytest.raises(SystemExit, match="acknowledge"):
        main(["reproduce-failure","--candidate","A","--output",str(tmp_path)])


def test_failure_runs_with_ack(tmp_path):
    assert main(["reproduce-failure","--candidate","A","--output",str(tmp_path),"--allow-rejected-research-candidate"]) == 0
    assert (tmp_path/"result.json").is_file()
