import json
from datetime import datetime
import csv
import os

def export_reels_watch_time(input_file: str, output_csv: str, default_video_duration_seconds: int, start_date: str, end_date: str):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading IG likes file: {e}")
        return

    liked_items = data.get("likes_media_likes", [])
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    events = []
    for item in liked_items:
        key = item.get("string_list_data", [{}])[0]
        timestamp_ms = key.get("timestamp")
        if not timestamp_ms:
            continue
        timestamp = datetime.utcfromtimestamp(timestamp_ms / 1000)
        day = timestamp.date()
        if not (start_date_obj <= day < end_date_obj):
            continue
        day_of_year = (day - start_date_obj).days + 1
        minute_of_day = timestamp.hour * 60 + timestamp.minute
        duration_minutes = default_video_duration_seconds / 60
        events.append({
            'DayOfYear': day_of_year,
            'MinuteOfDay': minute_of_day,
            'Duration': duration_minutes
        })

    events.sort(key=lambda x: (x['DayOfYear'], x['MinuteOfDay']))
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['DayOfYear', 'MinuteOfDay', 'Duration'])
        writer.writeheader()
        writer.writerows(events)
    print(f"IG Reels watch time -> {output_csv}")
