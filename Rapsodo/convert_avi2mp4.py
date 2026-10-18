from pathlib import Path
from moviepy import VideoFileClip

base_dir = Path(__file__).parent

input_dir = base_dir / "videos_2convert"
output_dir = base_dir / "videos_converted"


for avi_file in input_dir.glob("*.avi"):
    output_file = output_dir / f"{avi_file.stem}.mp4"

    print(f"Converting {avi_file.name} ....")

    with VideoFileClip(str(avi_file)) as clip:
        clip.write_videofile(
            str(output_file),
            codec="libx264",
            audio_codec="aac"
        )

print("Done.")