from __future__ import annotations

import csv
from pathlib import Path

import pytest

from parse_chats import (
    ChatProcessingSummary,
    calculate_reading_time,
    calculate_writing_time,
    process_chat_data,
)


def test_calculate_reading_time_validates_speed():
    with pytest.raises(ValueError):
        calculate_reading_time([], 0)


def test_calculate_writing_time_validates_speed():
    with pytest.raises(ValueError):
        calculate_writing_time("hello", 0)


def test_process_chat_data_round_trip(tmp_path: Path):
    chat_payload = {
        "messages": [
            {
                "sender_name": "Friend",
                "receiver_name": "Me",
                "timestamp": "2024-01-01T09:00:00",
                "content": "Hello",
            },
            {
                "sender_name": "Friend",
                "receiver_name": "Me",
                "timestamp": "2024-01-01T09:01:00",
                "content": "How are you?",
            },
            {
                "sender_name": "Me",
                "receiver_name": "Friend",
                "timestamp": "2024-01-01T09:05:00",
                "content": "Doing well!",
            },
            {
                "sender_name": "Me",
                "receiver_name": "Friend",
                "timestamp": "2024-01-01T10:00:00",
                "call_duration": 120,
            },
        ]
    }

    chat_file = tmp_path / "chat.json"
    chat_file.write_text(__import__("json").dumps(chat_payload), encoding="utf-8")

    output_csv = tmp_path / "out" / "chat.csv"
    calls_csv = tmp_path / "out" / "calls.csv"

    summary = process_chat_data(
        chat_file_path=chat_file,
        output_csv=output_csv,
        calls_csv=calls_csv,
        your_name="Me",
        reading_speed_cpm=100,
        typing_speed_cpm=50,
    )

    assert isinstance(summary, ChatProcessingSummary)
    assert summary.total_messages == 4
    assert summary.calls_logged == 1
    assert summary.events_logged == 1

    with output_csv.open() as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["DayOfYear"] == "1"
    assert rows[0]["MinuteOfDay"] == "545"

    with calls_csv.open() as handle:
        call_rows = list(csv.DictReader(handle))
    assert call_rows[0]["CallDuration"] == "2.0"
