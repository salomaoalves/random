# Rapsodo

Small video toolkit built on [MoviePy](https://zulko.github.io/moviepy/): it converts `.avi` videos to `.mp4` and stitches several videos together into a single one.

## Why "Rapsodo"?
A **rapsodo** (*rhapsode*, from the Greek *rhapsōidós*) was not a god, but a professional performer of ancient Greece who travelled from city to city reciting epic poetry, above all Homer's *Iliad* and *Odyssey*, at festivals and competitions. The rhapsodes were the "voice" of the Muses and of Apollo's art: they kept the great poems alive long before they were written down.

The name itself explains the link: *rhapsōidós* comes from *rháptein* ("to stitch, to sew") + *ōidḗ* ("song"), so a rhapsode was literally a **"stitcher of songs"**. He joined separate episodes and verses into one continuous performance, and that is exactly what this project does with videos: it takes separate pieces and sews them into a single, continuous video.

## Requirements
```
pip install moviepy
```
The scripts use the MoviePy 2.x imports (`from moviepy import ...`). MoviePy downloads its own `ffmpeg` binary (via `imageio-ffmpeg`), so nothing else should be needed.

## Folders
| Folder | Used by | What goes there |
| --- | --- | --- |
| `videos_2convert/` | `convert_avi2mp4.py` | `.avi` files to convert |
| `videos_converted/` | `convert_avi2mp4.py` | converted `.mp4` files |
| `videos_input/` | `merge_videos.py` | videos to be joined |
| `videos_output/` | `merge_videos.py` | the final merged video |

## convert_avi2mp4.py
Converts every `.avi` file in `videos_2convert/` to `.mp4` (video `libx264`, audio `aac`) and saves it in `videos_converted/` with the same name.
```
python convert_avi2mp4.py
```

## merge_videos.py
Joins all the videos in `videos_input/` (hidden files are ignored) one after the other and saves the result as `videos_output/busNE,N.mp4` (video `libx264`, audio `aac`).
```
python merge_videos.py
```
- The videos are joined in the order the folder lists them, which is not guaranteed to be alphabetical. To control the order, sort the list (e.g. `sorted(videos)`) and name the files with a prefix like `01_`, `02_`, ...
- To change the name of the final video, edit the `output_dir / "busNE,N.mp4"` line.

## Typical flow
1. Put the `.avi` files in `videos_2convert/` and run `convert_avi2mp4.py`.
2. Move the converted videos (and any other `.mp4`) to `videos_input/`.
3. Run `merge_videos.py` and get the final video in `videos_output/`.
