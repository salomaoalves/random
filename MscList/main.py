import config

def get_uri(link):
    '''
        @link: str, a open/spotify link'''
    playlist_URI = link.split("/")[-1].split("?")[0]
    return playlist_URI

def playlist_info(playlist_link):
    sp = config.connect(scope = 'playlist-read-private')
    playlist_URI = get_uri(playlist_link)
    for track in sp.playlist_tracks(playlist_URI)["items"]:
        #URI
        track_uri = track["track"]["uri"]
        print(track_uri)

        #Track name
        track_name = track["track"]["name"]
        print(track_name)
        
        #Main Artist
        artist_uri = track["track"]["artists"][0]["uri"]
        print(artist_uri)
        artist_info = sp.artist(artist_uri)
        print(artist_info)
        
        #Name, popularity, genre
        artist_name = track["track"]["artists"][0]["name"]
        print(artist_name)
        artist_pop = artist_info["popularity"]
        print(artist_pop)
        artist_genres = artist_info["genres"]
        print(artist_genres)
        
        #Album
        album = track["track"]["album"]["name"]
        print(album)
        
        #Popularity of the track
        track_pop = track["track"]["popularity"]
        print(track_pop)

playlist_link = "https://open.spotify.com/playlist/4bJUhMPraAFAKpZjnHtJw3"
#playlist_info(playlist_link)



# # sp = config.connect()
# # results = sp.current_user_saved_tracks()
# # for idx, item in enumerate(results['items']):
# #     #track = item['track']
# #     print(item)
# #     #print(idx, track['artists'][0]['name'], " – ", track['name'])
# #     input()
# # playlists = sp.user_playlists('spotify')
# # while playlists:
# #     for i, playlist in enumerate(playlists['items']):
# #         print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
# #     if playlists['next']:
# #         playlists = sp.next(playlists)
# #     else:
# #         playlists = None

def get_playlist_info():
    sp = config.connect(scope = 'playlist-read-private')
    results = sp.current_user_playlists(limit=50)
    for i, item in enumerate(results['items']):
        desc = item['description']
        size = item['tracks']['total']
        name = item['name']
        url = item['external_urls']['spotify']

