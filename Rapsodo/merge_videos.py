from pathlib import Path
from moviepy import VideoFileClip, concatenate_videoclips

base_dir = Path(__file__).parent

input_dir = base_dir / "videos_input"
output_dir = base_dir / "videos_output"

videos = [
    arq.name
    for arq in input_dir.iterdir()
    if arq.is_file() and not arq.name.startswith(".")
]

clips = [VideoFileClip(input_dir / v) for v in videos]

final_video = concatenate_videoclips(clips)

final_video.write_videofile(
    output_dir / "busNE,N.mp4",
    codec="libx264",
    audio_codec="aac"
)