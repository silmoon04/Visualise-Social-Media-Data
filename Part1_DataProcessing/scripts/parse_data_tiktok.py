import json
from datetime import datetime
import csv

def export_tiktok_watch_time(input_file: str, output_csv: str, default_video_duration_seconds: int, start_date: str, end_date: str):
    try:
        with open(input_file, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: '{input_file}' not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing '{input_file}': {e}")
        return

    liked_items = data.get("Activity", {}).get("Like List", {}).get("ItemFavoriteList", [])
    if not liked_items:
        print("No liked items found.")
        return

    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError as e:
        print(f"Error in date format: {e}")
        return

    events = []
    sessions = {}
    for item in liked_items:
        date_str = item.get("Date")
        if not date_str:
            continue
        try:
            timestamp = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        day = timestamp.date()
        if not (start_date_obj <= day < end_date_obj):
            continue
        sessions.setdefault(day, []).append(timestamp)

    for day, times in sessions.items():
        times.sort()
        day_of_year = (day - start_date_obj).days + 1
        session_start = times[0]
        duration = default_video_duration_seconds
        for i in range(1, len(times)):
            if (times[i] - times[i - 1]).total_seconds() <= 60:
                duration += default_video_duration_seconds
            else:
                events.append({
                    'DayOfYear': day_of_year,
                    'MinuteOfDay': session_start.hour * 60 + session_start.minute,
                    'Duration': duration / 60
                })
                session_start = times[i]
                duration = default_video_duration_seconds
        events.append({
            'DayOfYear': day_of_year,
            'MinuteOfDay': session_start.hour * 60 + session_start.minute,
            'Duration': duration / 60
        })

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['DayOfYear', 'MinuteOfDay', 'Duration'])
        writer.writeheader()
        writer.writerows(events)
    print(f"TikTok watch time -> {output_csv}")
