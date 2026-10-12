import sys, os
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(raiz)
import config 


'''list the lastest music/tracks that was played by the user'''

n_lastest = 50

sp = config.connect(scope = 'user-read-recently-played')

# Search for recent history
recent_tracks = sp.current_user_recently_played(limit=n_lastest)


# show results in terminal
for idx, track in enumerate(recent_tracks['items']):
    track_name = track['track']['name']
    artist_name = track['track']['artists'][0]['name']
    played_at = track['played_at']
    print(f"{idx+1}. {track_name} - {artist_name} (Tocado em: {played_at})")


import pandas as pd

# save in csv
data = [
    (track['track']['name'], track['track']['artists'][0]['name'], track['played_at'])
        for track in recent_tracks['items']
]
df = pd.DataFrame(data, columns=["Música", "Artista", "Tocada em"])
df.to_csv("music_history.csv", index=False)
print("Histórico salvo como 'music_history.csv' 🎵✅")