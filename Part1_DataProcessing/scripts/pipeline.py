"""Command line pipeline orchestrating the data processing tasks."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

from clean_and_combine_json_files import clean_and_combine_json_files
from parse_chats import ChatProcessingSummary, process_chat_data
from parse_data_tiktok import export_tiktok_watch_time
from parse_ig_likes import export_reels_watch_time
from process_yt_watchtime import process_yt_watchtime

# Load environment variables from .env file
load_dotenv()

LOGGER = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure a sensible default logging setup."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def validate_config(config: Dict[str, Any]) -> None:
    """Validate that the configuration contains all required fields."""
    required_global = ["output_folder", "start_date", "end_date"]
    if "global" not in config:
        raise ValueError("Config missing 'global' section")
    
    for field in required_global:
        if field not in config["global"]:
            raise ValueError(f"Config missing required global field: {field}")

def load_config(config_path: str | Path) -> Dict[str, Any]:
    """Load and validate the JSON configuration file."""
    config_file = Path(config_path)
    try:
        content = config_file.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Configuration file '{config_file}' not found") from exc

    if not content.strip():
        raise ValueError("Configuration file is empty")

    try:
        config = json.loads(content)
        validate_config(config)
        return config
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Invalid JSON in configuration file: {exc}") from exc


def ensure_output_folder(folder_path: str | Path) -> Path:
    """Ensure that the output folder exists."""
    path = Path(folder_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def file_exists(file_path: str | Path) -> bool:
    """Check if a file exists, logging a helpful message if it does not."""
    if not Path(file_path).exists():
        LOGGER.warning("Skipping task: '%s' not found.", file_path)
        return False
    return True


def main(config_path: str = "config.json") -> int:
    """Run the configured data-processing tasks."""
    setup_logging()
    config = load_config(config_path)

    global_config = config.get("global", {})
    output_folder = ensure_output_folder(global_config.get("output_folder", "output"))
    start_date_str = global_config.get("start_date")
    end_date_str = global_config.get("end_date")

    if not start_date_str or not end_date_str:
        LOGGER.error("Start and end dates must be provided in the config")
        return 1

    status_code = 0

    # Task 1 - combine instagram json files
    try:
        ccfg = config["clean_and_combine_json_files"]
        if file_exists(ccfg["input_folder"]):
            combined_output = output_folder / ccfg["output_file"]
            count = clean_and_combine_json_files(
                ccfg["input_folder"],
                combined_output,
                start_date_str,
                end_date_str,
            )
            LOGGER.info("Combined %s messages -> %s", count, combined_output)
    except KeyError:
        LOGGER.info("Task 'clean_and_combine_json_files' not configured; skipping")
    except Exception:  # pragma: no cover - defensive
        LOGGER.exception("Task 'clean_and_combine_json_files' failed")
        status_code = 1

    # Task 2 - chat processing
    try:
        pcfg = config["process_chat_data"]
        chat_file = output_folder / pcfg["output_csv"]
        calls_file = output_folder / pcfg["calls_csv"]
        if file_exists(pcfg["chat_file"]):
            summary: ChatProcessingSummary = process_chat_data(
                chat_file_path=pcfg["chat_file"],
                output_csv=chat_file,
                calls_csv=calls_file,
                your_name=pcfg["your_name"],
                reading_speed_cpm=int(pcfg["reading_speed_cpm"]),
                typing_speed_cpm=int(pcfg["typing_speed_cpm"]),
            )
            LOGGER.info(
                "Chat data -> %s (events=%s, calls=%s)",
                chat_file,
                summary.events_logged,
                summary.calls_logged,
            )
    except KeyError:
        LOGGER.info("Task 'process_chat_data' not configured; skipping")
    except Exception:  # pragma: no cover - defensive
        LOGGER.exception("Task 'process_chat_data' failed")
        status_code = 1

    # Task 3 - TikTok watch time
    try:
        tcfg = config["export_tiktok_watch_time"]
        if file_exists(tcfg["input_file"]):
            tiktok_output = output_folder / tcfg["output_csv"]
            events = export_tiktok_watch_time(
                input_file=tcfg["input_file"],
                output_csv=tiktok_output,
                default_video_duration_seconds=int(tcfg["default_video_duration_seconds"]),
                start_date=start_date_str,
                end_date=end_date_str,
            )
            LOGGER.info("TikTok data -> %s (events=%s)", tiktok_output, events)
    except KeyError:
        LOGGER.info("Task 'export_tiktok_watch_time' not configured; skipping")
    except Exception:  # pragma: no cover - defensive
        LOGGER.exception("Task 'export_tiktok_watch_time' failed")
        status_code = 1

    # Task 4 - YouTube watch time
    try:
        ycfg = config["youtube_watch_time"]
        if file_exists(ycfg["input_file"]):
            yt_output = output_folder / ycfg["output_csv"]
            process_yt_watchtime(
                input_file=ycfg["input_file"],
                output_csv=yt_output,
                playback_speed=float(ycfg["playback_speed"]),
                api_key_env=str(ycfg["api_key_env"]),
                start_date=start_date_str,
                end_date=end_date_str,
            )
            LOGGER.info("YouTube data -> %s", yt_output)
    except KeyError:
        LOGGER.info("Task 'youtube_watch_time' not configured; skipping")
    except Exception:  # pragma: no cover - defensive
        LOGGER.exception("Task 'youtube_watch_time' failed")
        status_code = 1

    # Task 5 - Instagram reels
    try:
        igcfg = config.get("export_reels_watch_time")
        if igcfg and file_exists(igcfg["input_file"]):
            ig_output = output_folder / igcfg["output_csv"]
            events = export_reels_watch_time(
                input_file=igcfg["input_file"],
                output_csv=ig_output,
                default_video_duration_seconds=int(igcfg["default_video_duration_seconds"]),
                start_date=start_date_str,
                end_date=end_date_str,
            )
            LOGGER.info("IG Reels data -> %s (events=%s)", ig_output, events)
        else:
            LOGGER.info("Task 'export_reels_watch_time' not configured; skipping")
    except Exception:  # pragma: no cover - defensive
        LOGGER.exception("Task 'export_reels_watch_time' failed")
        status_code = 1

    return status_code


if __name__ == "__main__":  # pragma: no cover - manual invocation
    raise SystemExit(main())
