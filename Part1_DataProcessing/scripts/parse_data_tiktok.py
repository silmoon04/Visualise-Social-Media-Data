"""Process TikTok liked items into session-based watch durations."""
from __future__ import annotations

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

LOGGER = logging.getLogger(__name__)


def _load_json(input_file: Path) -> Dict[str, object]:
    try:
        return json.loads(input_file.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"'{input_file}' not found") from exc
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Error parsing '{input_file}': {exc}") from exc


def _group_sessions(
    timestamps: Iterable[datetime],
    default_video_duration_seconds: int,
) -> List[Dict[str, float]]:
    sessions: List[Dict[str, float]] = []
    sorted_times = sorted(timestamps)
    if not sorted_times:
        return sessions

    session_start = sorted_times[0]
    duration_seconds = default_video_duration_seconds

    for previous, current in zip(sorted_times, sorted_times[1:]):
        gap = (current - previous).total_seconds()
        if gap <= 60:
            duration_seconds += default_video_duration_seconds
        else:
            sessions.append(
                {
                    "start": session_start,
                    "duration_minutes": duration_seconds / 60,
                }
            )
            session_start = current
            duration_seconds = default_video_duration_seconds

    sessions.append({"start": session_start, "duration_minutes": duration_seconds / 60})
    return sessions


def export_tiktok_watch_time(
    input_file: str | Path,
    output_csv: str | Path,
    default_video_duration_seconds: int,
    start_date: str,
    end_date: str,
) -> int:
    """Convert liked reels/posts into approximate watch durations."""
    if default_video_duration_seconds <= 0:
        raise ValueError("default_video_duration_seconds must be positive")

    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    data = _load_json(Path(input_file))
    liked_items = (
        data.get("Activity", {})
        .get("Like List", {})
        .get("ItemFavoriteList", [])
    )
    if not liked_items:
        LOGGER.info("No liked items found in %s", input_file)
        return 0

    by_day: Dict[datetime.date, List[datetime]] = {}
    for item in liked_items:
        date_str = item.get("Date")
        if not isinstance(date_str, str):
            continue
        try:
            timestamp = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            LOGGER.debug("Skipping unparseable TikTok timestamp: %s", date_str)
            continue

        if not (start_date_obj <= timestamp.date() < end_date_obj):
            continue
        by_day.setdefault(timestamp.date(), []).append(timestamp)

    events: List[Dict[str, float]] = []
    for day, timestamps in by_day.items():
        sessions = _group_sessions(timestamps, default_video_duration_seconds)
        for session in sessions:
            events.append(
                {
                    "DayOfYear": (day - start_date_obj).days + 1,
                    "MinuteOfDay": session["start"].hour * 60 + session["start"].minute,
                    "Duration": session["duration_minutes"],
                }
            )

    events.sort(key=lambda entry: (entry["DayOfYear"], entry["MinuteOfDay"]))

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["DayOfYear", "MinuteOfDay", "Duration"])
        writer.writeheader()
        writer.writerows(events)

    LOGGER.info("TikTok watch time -> %s (events=%s)", output_path, len(events))
    return len(events)


__all__ = ["export_tiktok_watch_time"]

