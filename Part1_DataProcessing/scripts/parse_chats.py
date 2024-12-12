import json
import csv
from datetime import datetime
from collections import defaultdict
from typing import Optional, List, Dict

def parse_timestamp(message: Dict) -> Optional[datetime]:
    ts = message.get('timestamp')
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None

def calculate_reading_time(messages: List[Dict], reading_speed_cpm: int) -> float:
    total_chars = sum(len(m.get('content', '')) for m in messages)
    return total_chars / reading_speed_cpm

def calculate_writing_time(content: str, typing_speed_cpm: int) -> float:
    return len(content) / typing_speed_cpm

def process_chat_data(chat_file: str, output_csv: str, calls_csv: str, your_name: str, reading_speed_cpm: int, typing_speed_cpm: int):
    try:
        with open(chat_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading JSON file: {e}")
        return

    messages = data if isinstance(data, list) else data.get('messages', [])
    messages.sort(key=lambda x: x.get('timestamp', ''))

    unread_messages = defaultdict(list)
    total_messages = 0
    total_logged = 0
    total_calls = 0

    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file, open(calls_csv, 'w', newline='', encoding='utf-8') as calls_file:
        writer = csv.DictWriter(csv_file, fieldnames=['DayOfYear', 'MinuteOfDay', 'Duration'])
        writer.writeheader()
        
        calls_writer = csv.DictWriter(calls_file, fieldnames=['DayOfYear', 'MinuteOfDay', 'CallDuration'])
        calls_writer.writeheader()

        for msg in messages:
            total_messages += 1
            sender = msg.get('sender_name')
            receiver = msg.get('receiver_name')
            timestamp = parse_timestamp(msg)
            content = msg.get('content', '')

            if not sender or not timestamp:
                continue

            if "call_duration" in msg:
                call_duration = msg["call_duration"]
                calls_writer.writerow({
                    'DayOfYear': timestamp.timetuple().tm_yday,
                    'MinuteOfDay': timestamp.hour * 60 + timestamp.minute,
                    'CallDuration': round(call_duration / 60, 2)  # Convert seconds to minutes
                })
                total_calls += 1
                continue

            if receiver == your_name:
                unread_messages[sender].append(msg)
            elif sender == your_name:
                reading_time = calculate_reading_time(unread_messages[receiver], reading_speed_cpm) if unread_messages[receiver] else 0
                writing_time = calculate_writing_time(content, typing_speed_cpm)
                total_duration = reading_time + writing_time

                if total_duration > 0:
                    writer.writerow({
                        'DayOfYear': timestamp.timetuple().tm_yday,
                        'MinuteOfDay': timestamp.hour * 60 + timestamp.minute,
                        'Duration': round(total_duration, 2)
                    })
                    total_logged += 1

                unread_messages[receiver].clear()

    print("Chat processing complete.")
    print(f"Total messages processed: {total_messages}")
    print(f"Events logged: {total_logged}")
    print(f"Total calls logged: {total_calls}")