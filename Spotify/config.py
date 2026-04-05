import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

def get_uri(spotify_url):
    '''Get the last set of char of a open.spotify url'''
    return spotify_url.split("/")[-1].split("?")[0]
 
def connect(scope=''):
    '''Connect with Spotify API - to get its dats
        get the dev credentials (ClientId, ClientSecret, RedirectUrl) in https://developer.spotify.com/
         and add them to env vars to be able to log in to the account
        @param scope        a declaration of what permissions your app needs from the user; when empty, no login is done
    '''

    with_user = scope!=''
    try:
        if not with_user: # get public data
            sp = spotipy.Spotify(
                client_credentials_manager = SpotifyClientCredentials())
        else: # get user data
            sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(scope=scope))
    except:
        print('Unable to connect with Spotify')
    return sp