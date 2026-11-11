import argparse, sys, os
from collections import Counter
raiz = os.path.dirname(os.path.abspath(__file__))
sys.path.append(raiz)
import config
from playlist_genres import find_playlist, get_playlist_artists


def playlist_artists(playlist, main_artist_only=False, sort_by="songs"):
    '''From the link (or name) of a public playlist, show all its artists and in how many songs each one appears
        SORT_BY: 'songs' (most songs first) | 'name' (artist name)'''

    sp = config.connect()
    found = find_playlist(sp, playlist)
    if not found:
        print(f"Playlist '{playlist}' not found.")
        return None
    print(f"Playlist: {found['name']} (by {found['owner']['display_name']}) - {found['external_urls']['spotify']}")

    tracks_artists, artist_names = get_playlist_artists(sp, found["id"])
    if main_artist_only:
        tracks_artists = [(name, ids[:1]) for name, ids in tracks_artists]
    if not tracks_artists:
        print("The playlist has no songs.")
        return None

    artist_count = Counter(artist_id for _, ids in tracks_artists for artist_id in set(ids))
    if sort_by == "name":
        artists = sorted(artist_count.items(), key=lambda item: artist_names[item[0]].lower())
    else:
        artists = sorted(artist_count.items(), key=lambda item: (-item[1], artist_names[item[0]].lower()))

    print(f"\n{len(artists)} artists in {len(tracks_artists)} songs:")
    for artist_id, count in artists:
        print(f"   {artist_names[artist_id]:<40} {count:>4} songs")
    return {artist_names[artist_id]: count for artist_id, count in artists}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show all the artists of a public playlist")
    parser.add_argument("playlist", help="link of the public playlist (or its name)")
    parser.add_argument("--main-artist", action="store_true", help="use only the main artist of each song (default: all artists)")
    parser.add_argument("-s", "--sort", choices=("songs", "name"), default="songs", help="sort by number of songs or by artist name (default: songs)")
    args = parser.parse_args()

    playlist_artists(args.playlist, args.main_artist, args.sort)
