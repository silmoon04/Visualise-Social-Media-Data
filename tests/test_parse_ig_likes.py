from __future__ import annotations

import csv
import json
from pathlib import Path

from parse_ig_likes import export_reels_watch_time


def test_export_reels_watch_time_filters_dates(tmp_path: Path):
    payload = {
        "likes_media_likes": [
            {
                "string_list_data": [
                    {
                        "timestamp": 1704096000,  # 2024-01-01T00:00:00Z
                    }
                ]
            },
            {
                "string_list_data": [
                    {
                        "timestamp": 1609459200,  # 2021-01-01T00:00:00Z
                    }
                ]
            },
        ]
    }
    input_file = tmp_path / "ig.json"
    input_file.write_text(json.dumps(payload), encoding="utf-8")

    output_csv = tmp_path / "ig.csv"
    events = export_reels_watch_time(
        input_file=input_file,
        output_csv=output_csv,
        default_video_duration_seconds=60,
        start_date="2024-01-01",
        end_date="2025-01-01",
    )

    assert events == 1
    with output_csv.open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert rows[0]["Duration"] == "1.0"
