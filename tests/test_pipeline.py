from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline import ensure_output_folder, file_exists, load_config


def test_load_config_reads_json(tmp_path: Path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"global": {"start_date": "2024-01-01", "end_date": "2024-12-31"}}), encoding="utf-8")
    config = load_config(config_file)
    assert config["global"]["start_date"] == "2024-01-01"


def test_load_config_raises_for_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "missing.json")


def test_file_exists(tmp_path: Path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello", encoding="utf-8")
    assert file_exists(file_path)
    assert not file_exists(tmp_path / "missing.txt")


def test_ensure_output_folder(tmp_path: Path):
    path = ensure_output_folder(tmp_path / "out")
    assert path.exists()
    assert path.is_dir()
