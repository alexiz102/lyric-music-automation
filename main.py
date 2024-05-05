import math
import os
import cv2
import pysrt
import syncedlyrics
import tkinter as tk
from spotify_handle import download_song_via_spotdl
from moviepy.config import change_settings
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from lrc2srt import lrc_to_srt

IMAGEMAGICK_PATH = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe" # Path to ImageMagick.exe
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_PATH})

# Song Details
song_name = "Art Gallery"  # Song Name
artist_name = "mrld"  # Artist Name

# Video Display
title_size = 128
title_color = "black"
title_font = "Courier"
title_outline = "black"
title_outline_thickness = 0

# Lyrics Details
lyrics_color = "black"
lyric_font = "Courier"
lyrics_outline = "black"
lyrics_outline_thickness = 0
lyrics_size = 64

# Adjust subtitle timing
offset_time = 0

# Video Output Resolution
output_width = 2245
output_height = 1587

# Video FPS
fps = 1

# Download Audio File and Lyrics
download_audio_file = True
download_lrc = True

# Specify paths
input_image_path = 'images/bg_1.jpg'  # Add image for Background
output_video_path = f'outputs/{song_name} Lyrics Music Video.mp4'  # Video Output Path
output_path = 'audio'
audio_path = 'audio/audio.mp3'  # Audio Path
subtitle_path = 'lyrics/lyrics.srt'
lrc_path = 'lyrics/lyrics.lrc'

# TODO: Add interface, Customization, and Selection

def time_to_seconds(time_obj):
    return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000


def create_subtitle_clips(subtitles, video_size, font_size=24, font='Arial', color='black', song_length=0):
    subtitle_clips = []

    song_title_display = TextClip(f"{song_name}", fontsize=title_size,
                                   color=title_color,
                                   transparent=True,
                                   stroke_width=title_outline_thickness,
                                   stroke_color=title_outline).set_start(0).set_duration(song_length)

    subtitle_clips.append(song_title_display.set_position(("center", "center")))

    for subtitle in subtitles:
        start_time = time_to_seconds(subtitle.start)
        end_time = time_to_seconds(subtitle.end)
        l_duration = end_time - start_time

        video_width, video_height = video_size

        text_clip = (TextClip(subtitle.text, fontsize=font_size, font=font, color=color, transparent=True,
                              size=(video_width * 3 / 4, None), method='caption', stroke_width=1, stroke_color="black")
                     .set_start(start_time).set_duration(l_duration))

        subtitle_x_position = 'center'
        subtitle_y_position = video_height * 4 / 5

        text_position = (subtitle_x_position, subtitle_y_position)
        # subtitle_clips.append(outline_clip.set_position(text_position))
        subtitle_clips.append(text_clip.set_position(text_position))

    return subtitle_clips


def add_lyrics(vid_clip, subtitles_path, song_length):
    if download_lrc:
        if os.path.exists(lrc_path):
            os.remove(lrc_path)
        syncedlyrics.search(f"{song_name} {artist_name}", save_path=lrc_path)
        print("Downloaded LRC")
        if os.path.exists(subtitles_path):
            os.remove(subtitles_path)
        lrc_to_srt(lrc_path, subtitles_path, offset_time)
    # audio_to_sub(audio_path, subtitles_path)
    print("Adding Subtitles...")
    subtitles = pysrt.open(subtitles_path)
    subtitle_clip = create_subtitle_clips(subtitles, vid_clip.size, lyrics_size, lyric_font, lyrics_color, song_length=song_length)

    sub_clip = CompositeVideoClip([vid_clip] + subtitle_clip)
    print("Added Lyrics")
    return sub_clip


def create_video():
    if download_audio_file:
        download_song_via_spotdl(f"{song_name} - {artist_name}")

    # Read input image and audio
    image = cv2.imread(input_image_path)
    audio_clip = AudioFileClip(audio_path)

    if output_height != 0 and output_width != 0:
        image = cv2.resize(image, (output_width, output_height))

    video_duration = math.ceil(audio_clip.duration)

    # Get image dimensions
    height, width, layers = image.shape

    # Calculate duration in seconds
    print(f'Song Length: {video_duration} seconds')

    if os.path.exists(output_video_path):
        os.remove(output_video_path)

    # Create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # Write repeated frames to create video
    total_frames: int = video_duration * fps
    for _ in range(total_frames):
        video_writer.write(image)
    video_writer.release()

    # Combine video with clipped audio
    video_clip = VideoFileClip(output_video_path)
    video_with_audio = video_clip.set_audio(audio_clip)
    print("Add Audio")
    video_with_audio_and_sub = add_lyrics(video_with_audio, subtitle_path, song_length=video_duration)
    video_with_audio_and_sub.write_videofile(output_video_path, codec='libx264', audio_codec='aac')

    print(f"Video with sound saved as {output_video_path}")


create_video()
