import json

import numpy as np
import pytest
from PIL import Image

from retroz_s1.io import load_rgb, save_rgb, write_provenance


def test_load_rgb_returns_contiguous_float32(tmp_path):
    path = tmp_path / "input.png"
    Image.new("RGB", (4, 3), (10, 20, 30)).save(path)

    result = load_rgb(path)

    assert result.shape == (3, 4, 3)
    assert result.dtype == np.float32
    assert result.flags.c_contiguous


def test_save_rgb_rejects_non_finite_values(tmp_path):
    values = np.zeros((3, 4, 3), dtype=np.float32)
    values[0, 0, 0] = np.nan
    with pytest.raises(ValueError, match="finite"):
        save_rgb(tmp_path / "bad.png", values)


def test_write_provenance_creates_parent_directory(tmp_path):
    output = tmp_path / "nested" / "render.png"
    path = write_provenance(output, {"value": np.int64(7)})
    assert json.loads(path.read_text()) == {"value": 7}
