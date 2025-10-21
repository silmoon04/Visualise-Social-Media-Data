"""Utilities for transforming YouTube watch history into timeline events."""
from __future__ import annotations

import csv
import datetime
import json
import logging
import os
import urllib.parse
from datetime import timezone
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence

import isodate

LOGGER = logging.getLogger(__name__)

VideoDurationFetcher = Callable[[Sequence[str], str], Mapping[str, float]]


def load_watch_history(file_path: str | Path) -> List[MutableMapping[str, object]]:
    """Load the YouTube watch history JSON file."""
    with Path(file_path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def filter_by_date(
    data: Iterable[MutableMapping[str, object]],
    start_date: datetime.datetime,
    end_date: datetime.datetime,
) -> List[MutableMapping[str, object]]:
    """Filter watch history entries between ``start_date`` and ``end_date`` (inclusive)."""
    filtered: List[MutableMapping[str, object]] = []
    for entry in data:
        raw_time = entry.get("time")
        if not isinstance(raw_time, str):
            continue
        timestamp = datetime.datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
        if start_date <= timestamp <= end_date:
            filtered.append(entry)
    return filtered


def extract_video_id(title_url: str) -> Optional[str]:
    """Extract the YouTube video ID from a ``titleUrl`` field."""
    parsed_url = urllib.parse.urlparse(title_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    return query_params.get("v", [None])[0]


def fetch_video_durations(video_ids: Sequence[str], api_key: str) -> Mapping[str, float]:
    """Fetch the duration (in seconds) for each video via the YouTube Data API."""
    if not video_ids:
        return {}

    try:
        from googleapiclient.discovery import build  # type: ignore
    except ImportError as exc:  # pragma: no cover - defensive
        raise RuntimeError("google-api-python-client is required for YouTube processing") from exc

    youtube = build("youtube", "v3", developerKey=api_key)
    durations: Dict[str, float] = {}
    for i in range(0, len(video_ids), 50):
        response = youtube.videos().list(part="contentDetails", id=",".join(video_ids[i : i + 50])).execute()
        for item in response.get("items", []):
            video_id = item["id"]
            duration_seconds = isodate.parse_duration(item["contentDetails"]["duration"]).total_seconds()
            if duration_seconds <= 3 * 3600:
                durations[video_id] = duration_seconds
    return durations


def process_yt_watchtime(
    input_file: str | Path,
    output_csv: str | Path,
    playback_speed: float,
    api_key_env: str,
    start_date: str,
    end_date: str,
    fetcher: Optional[VideoDurationFetcher] = None,
) -> int:
    """Convert YouTube watch history into CSV duration entries."""
    if playback_speed <= 0:
        raise ValueError("playback_speed must be positive")

    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    api_key = None
    if api_key_env:
        api_key = os.getenv(api_key_env)
    if not api_key:
        raise RuntimeError("No YouTube API key provided")

    watch_history = load_watch_history(input_file)
    filtered = filter_by_date(watch_history, start_dt, end_dt)
    video_ids = [extract_video_id(entry.get("titleUrl", "")) for entry in filtered]
    video_ids = [video_id for video_id in video_ids if video_id]

    duration_fetcher = fetcher or fetch_video_durations
    durations = duration_fetcher(video_ids, api_key)

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    events_written = 0
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["DayOfYear", "MinuteOfDay", "Duration"])
        writer.writeheader()
        for entry in filtered:
            video_id = extract_video_id(entry.get("titleUrl", ""))
            if not video_id:
                continue
            duration_seconds = durations.get(video_id)
            if not duration_seconds:
                continue
            timestamp = datetime.datetime.fromisoformat(entry["time"].replace("Z", "+00:00"))
            writer.writerow(
                {
                    "DayOfYear": timestamp.timetuple().tm_yday,
                    "MinuteOfDay": timestamp.hour * 60 + timestamp.minute,
                    "Duration": round(duration_seconds / playback_speed, 2),
                }
            )
            events_written += 1

    LOGGER.info("YouTube watch time -> %s (events=%s)", output_path, events_written)
    return events_written


__all__ = [
    "VideoDurationFetcher",
    "extract_video_id",
    "fetch_video_durations",
    "filter_by_date",
    "load_watch_history",
    "process_yt_watchtime",
]

