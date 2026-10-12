import sys, os
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(raiz)
import config 


def update_playlist_with_artists(playlist_id, artist_list, tracks_per_artist=4, clear=True):
    '''Searches for a list of artists, fetches X top tracks for each,
        and adds them to an existing Spotify playlist. Optionally clears the playlist beforehand.
    '''

    sp = config.connect("playlist-modify-public playlist-modify-private")

    # clear all existing tracks from the playlist
    if clear:
        print("Clearing playlist...")
        while True:
            # fetch current msc in the playlist
            current_tracks = sp.playlist_tracks(playlist_id, fields="items(track(uri))", limit=100)
            items = current_tracks["items"]
            
            if not items:
                break # no msc left to remove
                
            # extract uri and remove them in batches of 100
            track_uris = [item["track"]["uri"] for item in items if item["track"]]
            sp.playlist_remove_all_occurrences_of_items(playlist_id=playlist_id, items=track_uris)

    # get current tracks to prevent duplicates
    existing_uris = set()
    if not clear:
        print("Getting existing songs in the playlist to prevent duplicates...")
        offset = 0
        while True:
            current_tracks = sp.playlist_tracks(playlist_id, fields="items(track(uri))", limit=100, offset=offset)
            items = current_tracks["items"]
            if not items:
                break
            for item in items:
                if item["track"]:
                    existing_uris.add(item["track"]["uri"])
            offset += 100

    # search for artists and fetch their top tracks
    msc_uris_to_add, already_seen = [], []
    print("\nSearching for artists and its musics...")

    for artist_name in artist_list:
        
        # serach artist and check if it exists
        search_results = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
        artists = search_results["artists"]["items"]
        if not artists:
            print(f"Artist '{artist_name}' not found. Skipping...")
            continue

        artist_id, confirmed_name = artists[0]["id"], artists[0]["name"]

        # fetch top tracks
        top_tracks_results = sp.artist_top_tracks(artist_id, country="BR")
        tracks = top_tracks_results["tracks"][:tracks_per_artist]

        # add or not msc
        for track in tracks:
            track_uri = track["uri"]

            if track_uri in existing_uris or track_uri in already_seen:
                print(f"   ⏭ Skipped (duplicate): {track['name']} - {confirmed_name}")
                continue

            msc_uris_to_add.append(track_uri)
            already_seen.append(track_uri)
            print(f"   + Found: {track['name']} - {confirmed_name}")

    if not msc_uris_to_add:
        print("No tracks were found. Playlist update aborted.")
        return

    # 3. Add new tracks to the existing playlist (in batches of 100)
    print(f"\n📥 Adding {len(msc_uris_to_add)} tracks to the playlist...")
    for i in range(0, len(msc_uris_to_add), 100):
        batch = msc_uris_to_add[i : i + 100]
        sp.playlist_add_items(playlist_id=playlist_id, items=batch)

    print("✅ Success! Playlist updated.")


# --- USAGE EXAMPLE ---

# Paste your existing Spotify playlist ID here (found in the playlist share link)
EXISTING_PLAYLIST_ID = "YOUR_EXISTING_PLAYLIST_ID_HERE"

# List of artists to fetch tracks from
my_artists = ["Daft Punk", "The Weeknd", "Iron Maiden"]

# Execute function: will clear the playlist first and add 3 tracks per artist
update_playlist_with_artists(
    playlist_id=EXISTING_PLAYLIST_ID,
    artist_list=my_artists,
    tracks_per_artist=3,
    clear_playlist=True
)
