import sys, os
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(raiz)
import config 

sp = config.connect(scope = "playlist-modify-public playlist-modify-private")

PLAYLIST_ID = config.get_uri('https://open.spotify.com/playlist/1JXhH6VTsPUajoX2fO1BQ4')
TARGET_ARTIST = "Nome do Artista"    # O artista que você quer remover
#{'papatinho', 'mc ryan sp', 'conecrewdiretoria', 'família madá', 'mc rodrigo do cn', 'pedro lotto', 'diego thug', 'mc deni', 'dj hv', 'misael', 'tribo da periferia', 'lit up', 'mc samuka', 'letodie', 'mr. catra', 'mc bdk', 'paiva prod', 'ponto de equilíbrio', 'billy billy', 'haikaiss', 'cacife gold', 'duckjay', 'diey', 'mc denny', 'marília mendonça', 'eltin', 'mc lan', 'nog', 'dj dudu coupper', 'teaga', 'andré nine', 'dl funk', '9 house 1', 'hungria', 'mc lipi', 'bagua records', 'braão', 'cts kamika-z', 'projota', 'rapha renó', 'rô rosa', 'r3hab', 'eme lab', 'dj pedro', 'mc caverinha', 'barcellos', 'costa gold', 'wc no beat', 'bonde da stronda', 'kayblack', 'mc surya', 'dj nattan', 'os gemeos da putaria', 'dj marquinhos tm', 'dj gm', 'xamã', 'sid', 'chiocki', 'dj carlinhos da s.r', 'gustah', 'kawe', 'neo beats', 'matuê', 'cacife clandestino', 'haitam', 'shark47', 'mc paulin da capital', 'l7nnon', 'nocivo shomon'}

print("Search music in the playlist...")
results = sp.playlist_items(PLAYLIST_ID)
all_msc = results['items']
while results['next']:
    results = sp.next(results)
    all_msc.extend(results['items'])

msc_to_remove, all_msc_artist = [], {}

# verify each msc
for item in all_msc:
    track = item['track']
    if not track: continue
        
    track_id, track_name = track['id'], track['name']

    # get dict w all msc/artist
    all_msc_artist[track_name] = track['artists'][0]['name'].lower()
    
    # get the artists
    artists_from_msc = [artist['name'].lower() for artist in track['artists']]
    
    # check, to confirm the removal
    # if TARGET_ARTIST.lower() in artists_from_msc:
    #     print(f"Music to remove: {track_name} - Artista: {TARGET_ARTIST}")
    #     proceed = input("Confirm removal (y/n): ")
    #     if proceed.lower() == 'y': msc_to_remove.append(track_id)

# sort (by artirs) n write all msc/artist
all_msc_artist_sort = dict(sorted(all_msc_artist.items(), key=lambda item: item[1]))
with open('./musicas.txt', 'w', encoding='utf-8') as f:
    for key, value in all_msc_artist_sort.items():
        f.write(f"{key} -> {value}\n")

print('------------------------------------------------------------------')
print(artists_from_msc)

# Remove the selected msc
if msc_to_remove:
    print(f"\nRemoving {len(msc_to_remove)} mscs selected...")
    for i in range(0, len(msc_to_remove), 100):#spotify allow to remove only 100 per time
        batch = msc_to_remove[i:i+100]
        sp.playlist_remove_specific_occurrences_of_items(
            playlist_id=PLAYLIST_ID,
            items=[{"uri": f"spotify:track:{t_id}"} for t_id in batch])
    print("Removal completed successfully.!")
else:
    print("\nNo songs by this artist were found on the playlist.")
