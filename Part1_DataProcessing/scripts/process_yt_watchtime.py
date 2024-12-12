import json
import datetime
from datetime import timezone
from googleapiclient.discovery import build
import csv
import isodate
import urllib.parse

def load_watch_history(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def filter_by_date(data, start_date, end_date):
    return [
        e for e in data
        if 'time' in e and start_date <= datetime.datetime.fromisoformat(e['time'].replace('Z', '+00:00')) <= end_date
    ]

def extract_video_id(title_url: str):
    parsed_url = urllib.parse.urlparse(title_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    return query_params['v'][0] if 'v' in query_params else None

def fetch_video_durations(video_ids, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    durations = {}
    for i in range(0, len(video_ids), 50):
        response = youtube.videos().list(part="contentDetails", id=','.join(video_ids[i:i+50])).execute()
        for item in response.get('items', []):
            vid = item['id']
            dur = isodate.parse_duration(item['contentDetails']['duration']).total_seconds()
            if dur <= 3 * 3600:
                durations[vid] = dur
    return durations

def process_yt_watchtime(input_file: str, output_csv: str, playback_speed: float, api_key: str, start_date: str, end_date: str):

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    
    if not api_key:
        print("Error: No API key set.")
        return
    wh = load_watch_history(input_file)
    filtered = filter_by_date(wh, start_date, end_date)
    video_ids = [extract_video_id(e['titleUrl']) for e in filtered if 'titleUrl' in e]
    video_ids = [vid for vid in video_ids if vid is not None]  # Filter out None values
    video_durations = fetch_video_durations(video_ids, api_key)
    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['DayOfYear', 'MinuteOfDay', 'Duration'])
        writer.writeheader()
        for entry in filtered:
            vid = extract_video_id(entry['titleUrl'])
            if vid in video_durations:
                duration = video_durations[vid] / playback_speed
                ts = datetime.datetime.fromisoformat(entry['time'].replace('Z', '+00:00'))
                writer.writerow({
                    'DayOfYear': ts.timetuple().tm_yday,
                    'MinuteOfDay': ts.hour * 60 + ts.minute,
                    'Duration': round(duration, 2)
                })
    print(f"YouTube watch time -> {output_csv}")
