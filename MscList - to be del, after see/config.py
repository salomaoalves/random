import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

client_id=os.environ['SPOTIFY_ID']
client_secret=os.environ['SPOTIFY_SECRET']
redirect_uri='https://www.google.com.br/'
username='uyb18xqfygmzgjqs3lng9h38u'


def connect(scope=''):

    # Authentication
    with_user = True
    try:
        if not with_user:
            sp = spotipy.Spotify(
                client_credentials_manager = SpotifyClientCredentials(
                                                            client_id=client_id, 
                                                            client_secret=client_secret))
        else:
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                            client_secret=client_secret,
                                                            redirect_uri=redirect_uri,
                                                            scope=scope))
    except:
        print('Unable to connect with Spotify')
    return sp