import sys, os
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(raiz)
import config 


def playlist_tracks_info(playlist_link, AMOUNT=10, gather_all_artist=False):
    '''From a given user and one of its playlist links (the owner need to be the user), get information (like: URL,
        artists, name, popularity, gender, album) of the songs the are in the given playlist'''

    sp = config.connect('playlist-read-private')
    results = sp.playlist_items(config.get_uri(playlist_link))
    all_msc = results["items"]

    # for pagination
    while results['next']:
        results = sp.next(results)
        all_msc.extend(results['items'])
    
    main_artist, all_artist = [], []
    for i, track in enumerate(all_msc):
        if gather_all_artist: #in a list and return it
            main_artist.append(track["track"]["artists"][0]["name"].strip())
            all_artist.append([artista['name'].lower() for artista in track["track"]['artists']])
        else:
            print('Song ', i+1)
            print('\tSong name: "'+ track["track"]["name"].strip() + '"  and its uri: ' + track["track"]["uri"])
            print('\tMain artist name: "' + track["track"]["artists"][0]["name"].strip() + '"  and its uri: ' + track["track"]["artists"][0]["uri"])
            artist_info = sp.artist(track["track"]["artists"][0]["uri"])
            print('\tMain artist popularity and gender: ', artist_info["popularity"], ' -- ', artist_info["genres"])
            print('\tAlbum:', track["track"]["album"]["name"], '  || Song popularity:', track["track"]["popularity"])
        if i+1==AMOUNT:
            break
    set_all_artist = set([item for sublist in all_artist for item in sublist])
    if gather_all_artist:
        return all_artist, set_all_artist, set(main_artist)

playlist_tracks_info("https://open.spotify.com/playlist/1JXhH6VTsPUajoX2fO1BQ4", 150, False)
