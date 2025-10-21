"""Convert Instagram liked posts into estimated watch durations."""
from __future__ import annotations

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

LOGGER = logging.getLogger(__name__)


def export_reels_watch_time(
    input_file: str | Path,
    output_csv: str | Path,
    default_video_duration_seconds: int,
    start_date: str,
    end_date: str,
) -> int:
    """Process Instagram likes into a CSV of watch events."""
    if default_video_duration_seconds <= 0:
        raise ValueError("default_video_duration_seconds must be positive")

    try:
        data = json.loads(Path(input_file).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Error reading IG likes file: {exc}") from exc

    liked_items = data.get("likes_media_likes", [])
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    events: List[Dict[str, float]] = []
    for item in liked_items:
        entry = item.get("string_list_data", [{}])
        metadata = entry[0] if entry else {}
        timestamp_raw = metadata.get("timestamp")
        if timestamp_raw is None:
            continue
        try:
            timestamp_value = int(timestamp_raw)
        except (TypeError, ValueError):
            LOGGER.debug("Skipping invalid timestamp: %s", timestamp_raw)
            continue

        # Instagram exports appear either as seconds or milliseconds. We support both.
        if timestamp_value > 10**11:  # treat as milliseconds
            timestamp_seconds = timestamp_value / 1000
        else:
            timestamp_seconds = timestamp_value

        try:
            timestamp = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
        except (TypeError, ValueError):
            LOGGER.debug("Skipping invalid timestamp: %s", timestamp_raw)
            continue

        if not (start_date_obj <= timestamp.date() < end_date_obj):
            continue

        events.append(
            {
                "DayOfYear": (timestamp.date() - start_date_obj).days + 1,
                "MinuteOfDay": timestamp.hour * 60 + timestamp.minute,
                "Duration": default_video_duration_seconds / 60,
            }
        )

    events.sort(key=lambda entry: (entry["DayOfYear"], entry["MinuteOfDay"]))

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["DayOfYear", "MinuteOfDay", "Duration"])
        writer.writeheader()
        writer.writerows(events)

    LOGGER.info("IG Reels watch time -> %s (events=%s)", output_path, len(events))
    return len(events)


__all__ = ["export_reels_watch_time"]

