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

## random_artist_playlist.py
Take one of the artist lists of `config.py` (`br`, `latina` or `geral`), get 5 random songs from each artist (from its albums and singles) and put them all in a new playlist. Use `--mode` to choose between random songs (`random`, default) or the most recent songs of each artist (`latest`).
```
python random_artist_playlist.py "Playlist name" br            # 5 songs per artist, private playlist
python random_artist_playlist.py "Playlist name" geral -n 3 --public
python random_artist_playlist.py "Playlist name" latina --mode latest   # the 5 most recent songs of each artist
```

## playlist_genres.py
Given the name (or link) of a public playlist, show which music genres are in it: for each genre, in how many songs it appears (a song has the genres of its artists) and its first 3 songs (in the playlist order). Artists without genre on Spotify are listed at the end.
```
python playlist_genres.py "Rock Brasil"                    # all genres
python playlist_genres.py "Rock Brasil" --top 10           # only the 10 most common
python playlist_genres.py "Rock Brasil" --songs 5          # show 5 songs of each genre (default: 3)
python playlist_genres.py "https://open.spotify.com/playlist/..." --main-artist   # only the main artist of each song
```
