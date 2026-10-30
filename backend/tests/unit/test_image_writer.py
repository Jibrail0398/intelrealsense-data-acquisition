from dataclasses import replace
from unittest import mock

import cv2
import numpy as np
import pytest

from app.services.image_writer import FORMATS, write_shot
from app.utils.naming import image_name, max_index_in_dir, parse_index, validate_class_name


@pytest.fixture
def frames():
    color = np.random.default_rng(0).integers(0, 255, (48, 64, 3), dtype=np.uint8)
    depth = np.random.default_rng(1).integers(0, 9000, (48, 64), dtype=np.uint16)
    return color, depth


def test_layout_and_lossless_depth(tmp_path, frames):
    color, depth = frames
    files = write_shot(tmp_path, list(FORMATS), "tidak stunting", "tidak stunting-0001", color, depth)

    assert files["png"] == str(tmp_path / "png" / "tidak stunting" / "tidak stunting-0001.png")
    assert files["png16"] == str(tmp_path / "png16" / "tidak stunting" / "tidak stunting-0001.png")
    assert files["npy"].endswith("npy/tidak stunting/tidak stunting-0001.npy")

    assert np.array_equal(cv2.imread(files["png"]), color)
    for key in ("png16", "tiff"):
        loaded = cv2.imread(files[key], cv2.IMREAD_UNCHANGED)
        assert loaded.dtype == np.uint16
        assert np.array_equal(loaded, depth)
    assert np.array_equal(np.load(files["npy"]), depth)


def test_failed_format_leaves_nothing_behind(tmp_path, frames):
    color, depth = frames
    failing = replace(FORMATS["npy"], encode=mock.Mock(side_effect=RuntimeError("boom")))
    with mock.patch.dict(FORMATS, {"npy": failing}), pytest.raises(RuntimeError):
        write_shot(tmp_path, ["png", "npy"], "a", "a-0001", color, depth)
    assert not any(p.is_file() for p in tmp_path.rglob("*"))


def test_refuses_to_overwrite(tmp_path, frames):
    color, depth = frames
    write_shot(tmp_path, ["png"], "a", "a-0001", color, depth)
    with pytest.raises(FileExistsError):
        write_shot(tmp_path, ["png"], "a", "a-0001", color, depth)


def test_naming_rules(tmp_path):
    assert image_name("stunting", 7) == "stunting-0007"
    assert parse_index("stunting-0042", "stunting") == 42
    assert parse_index("stunting-x", "stunting") is None
    assert validate_class_name("  tidak   stunting ") == "tidak stunting"
    for bad in ("", "a/b", "x:y", ".hidden"):
        with pytest.raises(ValueError):
            validate_class_name(bad)

    folder = tmp_path / "png" / "a"
    folder.mkdir(parents=True)
    for n in (1, 2, 9):
        (folder / f"a-{n:04d}.png").touch()
    (folder / "ab-0099.png").touch()
    assert max_index_in_dir(folder, "a") == 9
