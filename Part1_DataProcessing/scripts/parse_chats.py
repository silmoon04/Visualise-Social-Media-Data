"""Utilities for parsing chat conversations exported from Instagram."""
from __future__ import annotations

import csv
import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, MutableMapping, Optional

LOGGER = logging.getLogger(__name__)


@dataclass
class ChatProcessingSummary:
    """Simple summary of the processed chat statistics."""

    total_messages: int
    events_logged: int
    calls_logged: int


def parse_timestamp(message: MutableMapping[str, object]) -> Optional[datetime]:
    """Parse an ISO formatted timestamp from a chat message payload."""
    raw_value = message.get("timestamp")
    if not isinstance(raw_value, str):
        return None
    try:
        return datetime.fromisoformat(raw_value)
    except ValueError:  # pragma: no cover - defensive
        LOGGER.debug("Unable to parse timestamp '%s'", raw_value)
        return None


def calculate_reading_time(messages: Iterable[MutableMapping[str, object]], reading_speed_cpm: int) -> float:
    """Return the estimated reading time in minutes for ``messages``."""
    if reading_speed_cpm <= 0:
        raise ValueError("reading_speed_cpm must be greater than zero")
    total_chars = sum(len(str(m.get("content", ""))) for m in messages)
    return total_chars / reading_speed_cpm


def calculate_writing_time(content: str, typing_speed_cpm: int) -> float:
    """Return the estimated writing time in minutes for ``content``."""
    if typing_speed_cpm <= 0:
        raise ValueError("typing_speed_cpm must be greater than zero")
    return len(content) / typing_speed_cpm


def _serialise_event(timestamp: datetime, duration_minutes: float) -> Dict[str, float]:
    """Convert an event into a dictionary for CSV output."""
    return {
        "DayOfYear": timestamp.timetuple().tm_yday,
        "MinuteOfDay": timestamp.hour * 60 + timestamp.minute,
        "Duration": round(duration_minutes, 2),
    }


def process_chat_data(
    chat_file_path: str | Path,
    output_csv: str | Path,
    calls_csv: str | Path,
    your_name: str,
    reading_speed_cpm: int,
    typing_speed_cpm: int,
) -> ChatProcessingSummary:
    """Process the exported chat JSON and calculate reading/writing effort."""
    try:
        with Path(chat_file_path).open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, FileNotFoundError) as exc:
        raise RuntimeError(f"Error loading chat JSON file: {exc}") from exc

    messages = data if isinstance(data, list) else data.get("messages", [])
    if not isinstance(messages, list):
        raise ValueError("Chat export did not contain a messages list")
    messages.sort(key=lambda payload: payload.get("timestamp", ""))

    unread_messages: Dict[str, List[MutableMapping[str, object]]] = defaultdict(list)
    total_messages = 0
    total_logged = 0
    total_calls = 0

    output_path = Path(output_csv)
    calls_path = Path(calls_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    calls_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file, calls_path.open(
        "w", newline="", encoding="utf-8"
    ) as calls_file:
        writer = csv.DictWriter(csv_file, fieldnames=["DayOfYear", "MinuteOfDay", "Duration"])
        writer.writeheader()

        calls_writer = csv.DictWriter(calls_file, fieldnames=["DayOfYear", "MinuteOfDay", "CallDuration"])
        calls_writer.writeheader()

        for message in messages:
            total_messages += 1
            sender = message.get("sender_name")
            receiver = message.get("receiver_name")
            timestamp = parse_timestamp(message)
            content = str(message.get("content", ""))

            if not sender or timestamp is None:
                continue

            if "call_duration" in message:
                try:
                    call_duration = float(message["call_duration"]) / 60
                except (TypeError, ValueError):  # pragma: no cover - defensive
                    LOGGER.debug("Invalid call duration encountered")
                    continue
                calls_writer.writerow(
                    {
                        "DayOfYear": timestamp.timetuple().tm_yday,
                        "MinuteOfDay": timestamp.hour * 60 + timestamp.minute,
                        "CallDuration": round(call_duration, 2),
                    }
                )
                total_calls += 1
                continue

            if receiver == your_name:
                unread_messages[sender].append(message)
                continue

            if sender == your_name and receiver:
                pending_messages = unread_messages.get(receiver, [])
                reading_time = calculate_reading_time(pending_messages, reading_speed_cpm) if pending_messages else 0
                writing_time = calculate_writing_time(content, typing_speed_cpm)
                total_duration = reading_time + writing_time

                if total_duration > 0:
                    writer.writerow(_serialise_event(timestamp, total_duration))
                    total_logged += 1

                unread_messages[receiver].clear()

    summary = ChatProcessingSummary(
        total_messages=total_messages,
        events_logged=total_logged,
        calls_logged=total_calls,
    )
    LOGGER.info(
        "Chat processing complete: messages=%s, events=%s, calls=%s",
        summary.total_messages,
        summary.events_logged,
        summary.calls_logged,
    )
    return summary


__all__ = [
    "ChatProcessingSummary",
    "calculate_reading_time",
    "calculate_writing_time",
    "parse_timestamp",
    "process_chat_data",
]