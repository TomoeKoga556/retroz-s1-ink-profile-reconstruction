import json
from types import MappingProxyType

import numpy as np
import pytest

from retroz_s1.candidates import b_runtime
from retroz_s1.candidates.oracle_renderer import render_oracle
from retroz_s1.cli import render_b, render_d3
from retroz_s1.io import write_provenance
from retroz_s1.synthetic import (
    edge_fixture,
    reproduce_a,
    reproduce_c,
    synthetic_oracle_labels,
)


def test_b_frozen_params_constructor():
    params = b_runtime.frozen_params()
    assert params.enabled is True
    with pytest.raises(TypeError, match="exact bool"):
        b_runtime.frozen_params(enabled=1)


def test_b_is_deterministic_and_nonmutating():
    source = edge_fixture(96, 17).astype(np.float32)
    before = source.copy()

    first, first_diagnostics = render_b(source)
    second, second_diagnostics = render_b(source)

    assert np.array_equal(source, before)
    assert np.array_equal(first, second)
    assert first_diagnostics == second_diagnostics


def test_d3_is_deterministic_and_nonmutating():
    source = edge_fixture(96, 0).astype(np.float32)
    before = source.copy()

    first, first_diagnostics = render_d3(source)
    second, second_diagnostics = render_d3(source)

    assert np.array_equal(source, before)
    assert np.array_equal(first, second)
    assert dict(first_diagnostics) == dict(second_diagnostics)


def test_oracle_user_labels_are_local():
    source = edge_fixture(96, 0).astype(np.float32)
    labels = synthetic_oracle_labels(96)
    output, changed, _ = render_oracle(
        source,
        labels["segments"],
        np.zeros((96, 96), bool),
        method="P1",
        tier="R0",
        fold=0,
    )

    assert output.shape == source.shape
    assert changed.shape == source.shape[:2]
    assert np.array_equal(output[~changed], source[~changed])


def test_failure_reproducers(tmp_path):
    first = tmp_path / "a-first"
    second = tmp_path / "a-second"

    assert reproduce_a(first)["activated_samples"] == 0
    assert reproduce_a(second)["activated_samples"] == 0
    assert (first / "activation_failure.npz").read_bytes() == (
        second / "activation_failure.npz"
    ).read_bytes()

    with np.load(first / "activation_failure.npz") as artifact:
        assert np.array_equal(artifact["x"], np.round(artifact["x"], 12))
        assert np.array_equal(artifact["edge"], np.round(artifact["edge"], 12))

    assert reproduce_c(tmp_path / "c")["mean_absolute_halo_energy"] > 0


def test_nested_immutable_diagnostics_are_json_serializable(tmp_path):
    path = write_provenance(
        tmp_path / "render.png",
        {
            "diagnostics": MappingProxyType(
                {"nested": MappingProxyType({"value": np.int64(3)})}
            )
        },
    )
    assert json.loads(path.read_text())["diagnostics"]["nested"]["value"] == 3
