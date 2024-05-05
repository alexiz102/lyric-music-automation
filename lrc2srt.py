import os
import re


def parse_lrc_timestamp(timestamp):
    try:
        minutes, seconds = timestamp.split(':')
        seconds, milliseconds = seconds.split('.')
        minutes, seconds, milliseconds = int(minutes), int(seconds), int(milliseconds)
        return minutes * 60 + seconds + milliseconds / 100
    except ValueError:
        return None


def lrc_to_srt(lrc_file_path, srt_file_path, offset_time=0):
    with open(lrc_file_path, 'r', encoding='utf-8') as lrc_file:
        lrc_content = lrc_file.read()

    sub_num = 1
    subs = []
    pattern = r'\[(\d+:\d+\.\d+)\](.*)'
    matches = re.findall(pattern, lrc_content)
    for idx, match in enumerate(matches):
        timestamp, text = match
        start_time = parse_lrc_timestamp(timestamp)
        if start_time is not None and len(text.strip()) != 0:
            end_time = parse_lrc_timestamp(matches[idx + 1][0]) if idx + 1 < len(matches) else start_time + 1
            subs.append(f'{sub_num}\n{format_time(start_time+offset_time)} --> {format_time(end_time+offset_time)}\n{text.strip()}\n\n')
            sub_num += 1

    with open(srt_file_path, 'w', encoding='utf-8') as srt_file:
        srt_file.writelines(subs)


def format_time(seconds):
    hours = int(seconds) // 3600
    minutes = (int(seconds) % 3600) // 60
    seconds = int(seconds) % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
