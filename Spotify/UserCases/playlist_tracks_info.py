import sys, os
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(raiz)
import config 


def playlist_tracks_info(playlist_link, AMOUNT=10):
    '''From a given user and one of its playlist links (the owner need to be the user), get information (like: URL,
        artists, name, popularity, gender, album) of the songs the are in the given playlist'''

    sp = config.connect(scope = 'playlist-read-private')
    playlist_URI = config.get_uri(playlist_link)
    results = sp.playlist_tracks(playlist_URI)
    
    for i, track in enumerate(results["items"]):
        artist_info = sp.artist(track["track"]["artists"][0]["uri"])
        print('Song ', i+1)
        print('\tSong name: "'+ track["track"]["name"].strip() + '"  and its uri: ' + track["track"]["uri"])
        print('\tMain artist name: "' + track["track"]["artists"][0]["name"].strip() + '"  and its uri: ' + track["track"]["artists"][0]["uri"])
        print('\tMain artist popularity and gender: ', artist_info["popularity"], ' -- ', artist_info["genres"])
        print('\tAlbum:', track["track"]["album"]["name"], '  || Song popularity:', track["track"]["popularity"])
        if i+1==AMOUNT:
            break


playlist_tracks_info("https://open.spotify.com/playlist/45SHVi5a9HRVuBsFNcnNhA")
