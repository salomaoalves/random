All functions has a little explanation below them (in its respectively .py file) for more details.

## config.py
File responsible for set spotify functions to configure the access, like to connect with spotify (with or without a user credentials) or get the uri from a given spotify url.

## User Cases
Here, there is general functons that can be used - just random ones. The goal here was to feel the lib.
- 1. **all_playlists_info.py:** get the X user playlist and show some information.
- 2. **playlist_tracks_info.py:** get information about the songs in a given user playlist.
- 3. **show_user_top_artist_track.py:** get the top X artist and tracks from 1Year|6Months|4Weeks ago from the config user.
- 4. **get_music_history.py:** list the last 50 tracks played by the config user and save them to `music_history.csv`.

## remove_artist.py
Export every track of a playlist to `musicas.txt` (sorted by artist). The removal of a given artist (`TARGET_ARTIST`) is commented out - uncomment it to remove that artist's tracks.

## test.py
Search a list of artists, get their top tracks and add them to an existing playlist (optionally clearing it first).
