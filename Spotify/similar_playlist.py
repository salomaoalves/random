import argparse, random, sys, os
from collections import Counter
raiz = os.path.dirname(os.path.abspath(__file__))
sys.path.append(raiz)
import config
from playlist_genres import find_playlist, get_playlist_artists, get_artists_genres


def search_genre_tracks(sp, genre, amount, skip_artists, skip_songs, max_pages=10):
    '''Search songs of a GENRE (a song has the genres of its artists) and return AMOUNT random ones,
        ignoring songs of SKIP_ARTISTS (ids) and SKIP_SONGS ('song - artist', lower) and one song per artist'''

    pool = {} # artist id -> uri, so the playlist isn't filled by a few artists
    for page in range(max_pages): # search returns at most 10 per request
        results = sp.search(q=f'genre:"{genre}"', type="track", limit=10, offset=page*10)["tracks"]["items"]
        for track in results:
            if not track or not track["artists"]:
                continue
            artist_id = track["artists"][0]["id"]
            name = f"{track['name']} - {track['artists'][0]['name']}".lower()
            if artist_id in skip_artists or name in skip_songs:
                continue
            pool.setdefault(artist_id, track["uri"])
        if len(results) < 10 or len(pool) >= amount * 3: # no more results or enough to choose from
            break
    return random.sample(list(pool.values()), min(amount, len(pool)))


def create_similar_playlist(playlist, playlist_name=None, total_songs=50, top_genres=5, include_artists=False, public=False):
    '''From the link (or name) of a public playlist, find its TOP_GENRES most common genres and create a new playlist
        with TOTAL_SONGS songs of these genres (split by how common each genre is in the original playlist)
        By default, artists of the original playlist are left out (INCLUDE_ARTISTS to keep them, but not the same songs)
        PLAYLIST_NAME: default is 'Like <original playlist name>'
    '''

    sp = config.connect("playlist-modify-public playlist-modify-private")
    found = find_playlist(sp, playlist)
    if not found:
        print(f"Playlist '{playlist}' not found.")
        return None
    print(f"Playlist: {found['name']} (by {found['owner']['display_name']}) - {found['external_urls']['spotify']}")

    tracks_artists, _ = get_playlist_artists(sp, found["id"])
    if not tracks_artists:
        print("The playlist has no songs.")
        return None
    artist_ids = sorted({a for _, ids in tracks_artists for a in ids})
    artists_genres = get_artists_genres(sp, artist_ids)

    genre_count = Counter(genre for _, ids in tracks_artists for genre in {g for a in ids for g in artists_genres[a]})
    genres = genre_count.most_common(top_genres)
    if not genres:
        print("The artists of the playlist have no genre on Spotify. Playlist not created.")
        return None

    # split the songs among the genres, proportional to how many songs of each genre the playlist has
    total_count = sum(count for _, count in genres)
    amounts = {genre: max(1, round(total_songs * count / total_count)) for genre, count in genres}

    skip_artists = set() if include_artists else set(artist_ids)
    skip_songs = {name.lower() for name, _ in tracks_artists}
    print(f"Getting {total_songs} songs of the genres: {', '.join(amounts)}...")
    track_uris = []
    for genre, amount in amounts.items():
        tracks = [uri for uri in search_genre_tracks(sp, genre, amount, skip_artists, skip_songs) if uri not in track_uris]
        print(f"   + {len(tracks)} songs of {genre}")
        track_uris.extend(tracks)

    if not track_uris:
        print("No songs were found. Playlist not created.")
        return None
    random.shuffle(track_uris)
    track_uris = track_uris[:total_songs]

    playlist_name = playlist_name or f"Like {found['name']}"
    # POST /me/playlists and /playlists/{id}/items: endpoints of the Feb/2026 Spotify API
    new_playlist = sp._post("me/playlists", payload={
        "name": playlist_name,
        "public": public,
        "description": f"Songs of the same genres of '{found['name']}': {', '.join(amounts)}"})
    for i in range(0, len(track_uris), 100): # spotify allow to add only 100 per time
        sp._post(f"playlists/{new_playlist['id']}/items", payload={"uris": track_uris[i:i+100]})

    print(f"\nPlaylist '{playlist_name}' created with {len(track_uris)} songs: {new_playlist['external_urls']['spotify']}")
    return new_playlist


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a playlist with songs of the same genres of a public playlist")
    parser.add_argument("playlist", help="link of the public playlist (or its name)")
    parser.add_argument("-N", "--name", default=None, help="name of the new playlist (default: 'Like <playlist name>')")
    parser.add_argument("-n", "--songs", type=int, default=50, help="number of songs of the new playlist (default: 50)")
    parser.add_argument("-g", "--genres", type=int, default=5, help="use the GENRES most common genres of the playlist (default: 5)")
    parser.add_argument("--include-artists", action="store_true", help="allow songs of artists already in the playlist (default: only other artists)")
    parser.add_argument("--public", action="store_true", help="create a public playlist (default: private)")
    args = parser.parse_args()

    create_similar_playlist(args.playlist, args.name, args.songs, args.genres, args.include_artists, args.public)
