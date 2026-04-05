import sys, os
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(raiz)
import config 

def all_playlists_info(AMOUNT=5):
    '''From a given user, get AMOUNT playlist and show its name, 
        description and total number of songs'''

    sp = config.connect(scope = 'playlist-read-private')
    results = sp.current_user_playlists(limit=AMOUNT)

    for i, item in enumerate(results['items']):
        print(str(i+1) + '.  name: ', item['name'])
        print('     desc: ', item['description'])
        print('     total songs: ', item['tracks']['total'])
        print('---------')

all_playlists_info(50)