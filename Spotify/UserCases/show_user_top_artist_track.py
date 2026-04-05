import sys, os
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(raiz)
import config 

def show_user_top_artist_tracks(AMOUNT=5):
    '''From a given user, get the top AMOUNT artists/songs for that user'''

    sp = config.connect(scope = 'user-top-read')
    ranges = [['short_term','4 weeks'], ['medium_term','6 months'], ['long_term','1 year']]

    for sp_range in ranges:
        print("range:", sp_range[0], '- last', sp_range[1])

        print('Artists:')
        results_artists = sp.current_user_top_artists(time_range=sp_range[0], limit=AMOUNT)
        for i, item in enumerate(results_artists['items']):
            print(i+1, item['name'])

        results_tracks = sp.current_user_top_tracks(time_range=sp_range[0], limit=AMOUNT)
        print('Songs:', '-'*15)
        for i, item in enumerate(results_tracks['items']):
            print(i+1, item['name'], '//', item['artists'][0]['name'])
        print('-'*100)

show_user_top_artist_tracks()