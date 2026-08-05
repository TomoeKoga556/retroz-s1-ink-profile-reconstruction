import json
import numpy as np

from retroz_s1.cli import render_b, render_d3
from retroz_s1.candidates.oracle_renderer import render_oracle
from retroz_s1.synthetic import edge_fixture, reproduce_a, reproduce_c, synthetic_oracle_labels
from retroz_s1.io import write_provenance


def test_b_is_deterministic_and_nonmutating():
    source=edge_fixture(96,17).astype(np.float32); before=source.copy()
    a,da=render_b(source); b,db=render_b(source)
    assert np.array_equal(source,before)
    assert np.array_equal(a,b)
    assert da==db


def test_d3_is_deterministic_and_nonmutating():
    source=edge_fixture(96,0).astype(np.float32); before=source.copy()
    a,da=render_d3(source); b,db=render_d3(source)
    assert np.array_equal(source,before)
    assert np.array_equal(a,b)
    assert dict(da)==dict(db)


def test_oracle_user_labels_are_local():
    source=edge_fixture(96,0).astype(np.float32)
    labels=synthetic_oracle_labels(96)
    out,changed,diag=render_oracle(source,labels["segments"],np.zeros((96,96),bool),method="P1",tier="R0",fold=0)
    assert out.shape==source.shape
    assert changed.shape==source.shape[:2]
    assert np.array_equal(out[~changed],source[~changed])


def test_failure_reproducers(tmp_path):
    assert reproduce_a(tmp_path/"a")["activated_samples"]==0
    assert reproduce_c(tmp_path/"c")["mean_absolute_halo_energy"]>0


def test_nested_immutable_diagnostics_are_json_serializable(tmp_path):
    from types import MappingProxyType
    path=write_provenance(tmp_path/"render.png",{"diagnostics":MappingProxyType({"nested":MappingProxyType({"value":np.int64(3)})})})
    assert json.loads(path.read_text())["diagnostics"]["nested"]["value"]==3
