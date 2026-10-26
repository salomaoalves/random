import argparse, random, sys, os
raiz = os.path.dirname(os.path.abspath(__file__))
sys.path.append(raiz)
import config

ARTIST_LISTS = {
    'br': config.get_isthis_artist_br,
    'latina': config.get_isthis_artist_latina,
    'geral': config.get_isthis_artist,
}
MODES = ('random', 'latest')


def find_artist(sp, artist_name):
    '''Search an artist by name; prefer an exact (case-insensitive) match over the first result'''
    artists = sp.search(q=f"artist:{artist_name}", type="artist", limit=10)["artists"]["items"]
    if not artists:
        return None
    for artist in artists:
        if artist["name"].lower() == artist_name.lower():
            return artist
    return artists[0]


def get_all_items(sp, page):
    '''Follow the pagination of a spotify response and return all its items'''
    items = page["items"]
    while page["next"]:
        page = sp.next(page)
        items.extend(page["items"])
    return items


def random_artist_tracks(sp, artist_id, amount=5, pool_size=30, mode="random"):
    '''Get AMOUNT random tracks from an artist, looking into its albums and singles in a random order
        (stops reading albums once there are POOL_SIZE different songs to choose from)
        If MODE is 'latest', get instead its AMOUNT most recent songs (albums and singles from the newest to the oldest)'''

    latest = mode == "latest"
    albums = get_all_items(sp, sp.artist_albums(artist_id, include_groups="album,single", limit=10))
    if latest:
        albums.sort(key=lambda album: album["release_date"], reverse=True) # YYYY-MM-DD (or YYYY-MM / YYYY)
        pool_size = amount
    else:
        random.shuffle(albums)

    pool = {} # song name (lower) -> uri, so the same song from album and single isn't picked twice
    for album in albums:
        for track in get_all_items(sp, sp.album_tracks(album["id"], limit=50)):
            if any(artist["id"] == artist_id for artist in track["artists"]):
                pool.setdefault(track["name"].lower(), track["uri"])
            if latest and len(pool) >= pool_size: # keep the newest songs only
                break
        if len(pool) >= pool_size:
            break

    if latest:
        return list(pool.values())
    return random.sample(list(pool.values()), min(amount, len(pool)))


def create_random_artist_playlist(playlist_name, list_type, tracks_per_artist=5, public=False, mode="random"):
    '''Get one of the artist lists of config.py (br | latina | geral), take TRACKS_PER_ARTIST random songs
        from each artist and put them all, shuffled, in a new playlist called PLAYLIST_NAME
        MODE: 'random' (random songs) | 'latest' (the TRACKS_PER_ARTIST most recent songs of each artist)'''

    sp = config.connect("playlist-modify-public playlist-modify-private")
    artist_list = ARTIST_LISTS[list_type]()

    print(f"Getting {tracks_per_artist} {mode} songs from {len(artist_list)} artists ({list_type})...")
    track_uris = []
    for artist_name in artist_list:
        artist = find_artist(sp, artist_name)
        if not artist:
            print(f"   Artist '{artist_name}' not found. Skipping...")
            continue
        tracks = random_artist_tracks(sp, artist["id"], tracks_per_artist, mode=mode)
        print(f"   + {len(tracks)} songs from {artist['name']}")
        track_uris.extend(tracks)

    if not track_uris:
        print("No songs were found. Playlist not created.")
        return
    random.shuffle(track_uris)

    # POST /me/playlists and /playlists/{id}/items: endpoints of the Feb/2026 Spotify API
    playlist = sp._post("me/playlists", payload={
        "name": playlist_name,
        "public": public,
        "description": f"{tracks_per_artist} {mode} songs from each artist of the '{list_type}' list"})
    for i in range(0, len(track_uris), 100): # spotify allow to add only 100 per time
        sp._post(f"playlists/{playlist['id']}/items", payload={"uris": track_uris[i:i+100]})

    print(f"\nPlaylist '{playlist_name}' created with {len(track_uris)} songs: {playlist['external_urls']['spotify']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a playlist with random songs from one of the artist lists of config.py")
    parser.add_argument("name", help="name of the new playlist")
    parser.add_argument("list", choices=ARTIST_LISTS.keys(), help="which artist list to use")
    parser.add_argument("-n", "--tracks", type=int, default=5, help="songs per artist (default: 5)")
    parser.add_argument("--public", action="store_true", help="create a public playlist (default: private)")
    parser.add_argument("-m", "--mode", choices=MODES, default="random", help="random songs or the most recent ones of each artist (default: random)")
    args = parser.parse_args()

    create_random_artist_playlist(args.name, args.list, args.tracks, args.public, args.mode)
