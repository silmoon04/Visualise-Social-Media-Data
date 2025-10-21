from __future__ import annotations

import csv
import json
from pathlib import Path

from parse_data_tiktok import export_tiktok_watch_time


def test_export_tiktok_watch_time_creates_sessions(tmp_path: Path):
    payload = {
        "Activity": {
            "Like List": {
                "ItemFavoriteList": [
                    {"Date": "2024-01-01 10:00:00"},
                    {"Date": "2024-01-01 10:00:40"},
                    {"Date": "2024-01-01 10:05:00"},
                ]
            }
        }
    }
    input_file = tmp_path / "tiktok.json"
    input_file.write_text(json.dumps(payload), encoding="utf-8")

    output_csv = tmp_path / "events.csv"
    events = export_tiktok_watch_time(
        input_file=input_file,
        output_csv=output_csv,
        default_video_duration_seconds=30,
        start_date="2024-01-01",
        end_date="2024-02-01",
    )

    assert events == 2
    with output_csv.open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[0]["Duration"] == "1.0"
    assert rows[1]["Duration"] == "0.5"
