from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from clean_and_combine_json_files import clean_and_combine_json_files


def test_clean_and_combine_json_files(tmp_path: Path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    message_1 = inbox / "message_1.json"
    message_2 = inbox / "message_2.json"

    payload = {
        "participants": ["Me", "Friend"],
        "messages": [
            {
                "timestamp_ms": int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp() * 1000),
                "sender_name": "Me",
                "content": "Hello",
            },
            {
                "timestamp_ms": int(datetime(2023, 12, 1, tzinfo=timezone.utc).timestamp() * 1000),
                "sender_name": "Friend",
                "content": "Old message",
            },
        ],
    }

    message_1.write_text(json.dumps(payload), encoding="utf-8")
    message_2.write_text(json.dumps(payload), encoding="utf-8")

    output_file = tmp_path / "combined.json"
    count = clean_and_combine_json_files(
        input_folder=inbox,
        output_file=output_file,
        start_date="2023-12-15",
        end_date="2024-12-31",
    )

    assert count == 2  # one message from each file within the date range
    combined = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(combined) == 2
    assert combined[0]["content"] == "Hello"
