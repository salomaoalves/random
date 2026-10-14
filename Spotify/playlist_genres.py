import argparse, sys, os
from collections import Counter
raiz = os.path.dirname(os.path.abspath(__file__))
sys.path.append(raiz)
import config


def find_playlist(sp, playlist):
    '''Get a public playlist by its link/uri/id or, if it isn't one, search it by name
        (prefer an exact (case-insensitive) match over the first result)'''

    if "open.spotify.com/playlist/" in playlist or playlist.startswith("spotify:playlist:"):
        playlist_id = config.get_uri(playlist).split(":")[-1]
        return sp.playlist(playlist_id, fields="id,name,owner(display_name),external_urls")

    results = sp.search(q=playlist, type="playlist", limit=10)["playlists"]["items"]
    results = [item for item in results if item] # search can return null items
    if not results:
        return None
    for item in results:
        if item["name"].lower() == playlist.lower():
            return item
    return results[0]


def get_playlist_artists(sp, playlist_id):
    '''Return, for each track of the playlist, the list of its artists ids (and a id -> name dict)'''

    # GET /playlists/{id}/items: endpoint of the Feb/2026 Spotify API ('track' was renamed to 'item')
    page = sp._get(f"playlists/{playlist_id}/items", limit=100)
    items = page["items"]
    while page["next"]:
        page = sp.next(page)
        items.extend(page["items"])

    tracks_artists, artist_names = [], {}
    for item in items:
        track = item.get("item") or item.get("track")
        if not track or track.get("type") != "track": # skip podcasts episodes and unavailable songs
            continue
        ids = []
        for artist in track["artists"]:
            if artist.get("id"): # local files have artists without id
                ids.append(artist["id"])
                artist_names[artist["id"]] = artist["name"]
        tracks_artists.append(ids)
    return tracks_artists, artist_names


def get_artists_genres(sp, artist_ids):
    '''Get the genres of each artist (one request per artist: the batch GET /artists was removed in Feb/2026)'''
    genres = {}
    for i, artist_id in enumerate(artist_ids):
        print(f"\r   Getting artists genres... {i+1}/{len(artist_ids)}", end="", flush=True)
        genres[artist_id] = sp.artist(artist_id).get("genres", [])
    print()
    return genres


def playlist_genres(playlist, top=None, main_artist_only=False):
    '''From the name (or link) of a public playlist, show which music genres are in it,
        counting in how many songs each genre appears (a song has the genres of its artists)'''

    sp = config.connect()
    found = find_playlist(sp, playlist)
    if not found:
        print(f"Playlist '{playlist}' not found.")
        return None
    print(f"Playlist: {found['name']} (by {found['owner']['display_name']}) - {found['external_urls']['spotify']}")

    tracks_artists, artist_names = get_playlist_artists(sp, found["id"])
    if main_artist_only:
        tracks_artists = [ids[:1] for ids in tracks_artists]
    if not tracks_artists:
        print("The playlist has no songs.")
        return None

    artists_genres = get_artists_genres(sp, sorted({a for ids in tracks_artists for a in ids}))

    genre_count, no_genre = Counter(), 0
    for ids in tracks_artists:
        track_genres = {genre for artist_id in ids for genre in artists_genres[artist_id]}
        genre_count.update(track_genres)
        no_genre += not track_genres

    total = len(tracks_artists)
    print(f"\n{len(genre_count)} genres found in {total} songs ({len(artists_genres)} artists):")
    for genre, count in genre_count.most_common(top):
        print(f"   {genre:<35} {count:>4} songs  ({count/total:.0%})")
    if no_genre:
        print(f"\n{no_genre} songs have artists without genre on Spotify:")
        print("   " + ", ".join(sorted({artist_names[a] for a, g in artists_genres.items() if not g})))
    return genre_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show the music genres present in a public playlist")
    parser.add_argument("playlist", help="name of the public playlist (or its link)")
    parser.add_argument("-t", "--top", type=int, default=None, help="show only the TOP most common genres (default: all)")
    parser.add_argument("--main-artist", action="store_true", help="use only the main artist of each song (default: all artists)")
    args = parser.parse_args()

    playlist_genres(args.playlist, args.top, args.main_artist)
