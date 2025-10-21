"""Utilities for combining Instagram JSON message exports."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, MutableMapping, Sequence

import logging

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Simple representation of an Instagram message."""

    timestamp: datetime
    payload: MutableMapping[str, object]

    @property
    def day(self) -> datetime.date:
        """Return the calendar day component of the timestamp."""
        return self.timestamp.date()


def _discover_json_files(input_folder: Path) -> Sequence[Path]:
    """Return a sorted list of JSON files within ``input_folder``."""
    candidates = sorted(Path(input_folder).rglob("*.json"))
    if not candidates:
        logger.warning("No JSON files found in %s", input_folder)
    return candidates


def _load_messages(file_path: Path) -> Iterable[MutableMapping[str, object]]:
    """Load Instagram style message payloads from ``file_path``."""
    try:
        with file_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise ValueError(f"{file_path} is not valid JSON") from exc

    if isinstance(payload, list):
        return payload
    if isinstance(payload, MutableMapping):
        messages = payload.get("messages")
        if isinstance(messages, list):
            return messages
    raise ValueError(f"Unsupported message format in {file_path}")


def _parse_timestamp(message: MutableMapping[str, object]) -> datetime:
    """Extract a timestamp from a raw Instagram message payload."""
    if "timestamp_ms" in message:
        timestamp_ms = int(message["timestamp_ms"])  # type: ignore[arg-type]
        return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)

    if "timestamp" in message:
        raw_value = message["timestamp"]
        if isinstance(raw_value, str):
            try:
                return datetime.fromisoformat(raw_value)
            except ValueError as exc:  # pragma: no cover - defensive
                raise ValueError(f"Invalid ISO timestamp: {raw_value}") from exc

    raise ValueError("Message did not contain a recognised timestamp field")


def _normalise_messages(raw_messages: Iterable[MutableMapping[str, object]]) -> List[Message]:
    """Convert raw payload dictionaries into :class:`Message` objects."""
    normalised: List[Message] = []
    for message in raw_messages:
        try:
            timestamp = _parse_timestamp(message)
        except ValueError as exc:
            logger.debug("Skipping message without timestamp: %s", exc)
            continue
        normalised.append(Message(timestamp=timestamp, payload=message))
    return normalised


def clean_and_combine_json_files(
    input_folder: str | Path,
    output_file: str | Path,
    start_date: str,
    end_date: str,
) -> int:
    """Combine Instagram message archives into a single JSON file.

    Parameters
    ----------
    input_folder:
        Folder containing Instagram ``message_*.json`` exports.
    output_file:
        Target JSON file that will receive the filtered messages.
    start_date, end_date:
        Date boundaries in ``YYYY-MM-DD`` format. Messages on or after
        ``start_date`` and strictly before ``end_date`` are kept.

    Returns
    -------
    int
        The number of messages written to ``output_file``.
    """

    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    candidates = _discover_json_files(Path(input_folder))
    combined: List[Message] = []
    for file_path in candidates:
        try:
            raw_messages = _load_messages(file_path)
        except ValueError as exc:
            logger.warning("Skipping %s: %s", file_path, exc)
            continue
        combined.extend(_normalise_messages(raw_messages))

    filtered = [msg for msg in combined if start <= msg.day < end]
    filtered.sort(key=lambda msg: msg.timestamp)

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    serialisable = [msg.payload for msg in filtered]
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(serialisable, handle, ensure_ascii=False, indent=2)

    logger.info("Wrote %s messages to %s", len(serialisable), output_path)
    return len(serialisable)
