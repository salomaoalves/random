import config

def get_playlist_info():
    sp = config.connect(scope = 'playlist-read-private')
    results = sp.current_user_playlists(limit=50)
    for i, item in enumerate(results['items']):
        desc = item['description']
        size = item['tracks']['total']
        name = item['name']
        url = item['external_urls']['spotify']
