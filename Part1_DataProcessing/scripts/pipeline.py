import json
from clean_and_combine_json_files import clean_and_combine_json_files
from parse_chats import process_chat_data
from parse_data_tiktok import export_tiktok_watch_time
from parse_ig_likes import export_reels_watch_time
from process_yt_watchtime import process_yt_watchtime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def load_config(config_path: str):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                raise ValueError("Config file is empty.")
            return json.loads(content)
    except FileNotFoundError:
        print(f"Error: '{config_path}' not found.")
        exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: {e}")
        exit(1)

def ensure_output_folder(folder_path: str):
    os.makedirs(folder_path, exist_ok=True)

def file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    if not os.path.exists(file_path):
        print(f"Skipping task: '{file_path}' not found.")
        return False
    return True

def main():
    config = load_config('config.json')
    global_config = config.get("global", {})
    output_folder = global_config.get("output_folder", "output")
    start_date_str = global_config.get("start_date")
    end_date_str = global_config.get("end_date")
    
    if not start_date_str or not end_date_str:
        print("Error: Start/end date missing in config.")
        return

    # Task 1
    try:
        ccfg = config["clean_and_combine_json_files"]
        if file_exists(ccfg["input_folder"]):
            combined_output = os.path.join(output_folder, ccfg["output_file"])
            clean_and_combine_json_files(ccfg["input_folder"], combined_output, start_date_str, end_date_str)
            print(f"Combined JSON -> {combined_output}")
    except KeyError:
        print("Task 1 skipped.")
    except Exception as e:
        print(f"Task 1 error: {e}")

    # Task 2
    try:
        pcfg = config["process_chat_data"]
        if file_exists(pcfg["chat_file"]):
            chat_output = os.path.join(output_folder, pcfg["output_csv"])
            calls_output = os.path.join(output_folder, pcfg["calls_csv"])
            process_chat_data(pcfg["chat_file"], chat_output, calls_output, pcfg["your_name"], pcfg["reading_speed_cpm"], pcfg["typing_speed_cpm"])
            print(f"Chat data -> {chat_output}")
            print(f"Calls data -> {calls_output}")
    except KeyError:
        print(f"Task 2 skipped: {pcfg}")
    except Exception as e:
        print(f"Task 2 error: {e}")

    # Task 3
    try:
        tcfg = config["export_tiktok_watch_time"]
        if file_exists(tcfg["input_file"]):
            tiktok_output = os.path.join(output_folder, tcfg["output_csv"])
            export_tiktok_watch_time(tcfg["input_file"], tiktok_output, tcfg["default_video_duration_seconds"], start_date_str, end_date_str)
            print(f"TikTok data -> {tiktok_output}")
    except KeyError:
        print("Task 3 skipped.")
    except Exception as e:
        print(f"Task 3 error: {e}")

    # Task 4
    try:
        ycfg = config["youtube_watch_time"]
        if file_exists(ycfg["input_file"]):
            yt_output = os.path.join(output_folder, ycfg["output_csv"])
            process_yt_watchtime(
                input_file=ycfg["input_file"],
                output_csv=yt_output,
                playback_speed=ycfg["playback_speed"],
                api_key=os.getenv(ycfg["api_key_env"]),
                start_date=start_date_str,
                end_date=end_date_str
            )
            print(f"YouTube data -> {yt_output}")
            
    except KeyError:
        print("Task 4 skipped.")
    except Exception as e:
        print(f"Task 4 error: {e}")

    # Task 5 (IG Reels)
    try:
        igcfg = config.get("export_reels_watch_time", {})
        if igcfg and file_exists(igcfg["input_file"]):
            ig_output = os.path.join(output_folder, igcfg["output_csv"])
            export_reels_watch_time(igcfg["input_file"], ig_output, igcfg["default_video_duration_seconds"], start_date_str, end_date_str)
            print(f"IG Reels data -> {ig_output}")
        else:
            print("Task 5 skipped.")
    except Exception as e:
        print(f"Task 5 error: {e}")

if __name__ == "__main__":
    main()