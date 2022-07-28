from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup
import json
from pytube import YouTube
from youtubesearchpython import VideosSearch
import os
from colorama import init,Fore

PlaylistTracks = []
init()



def get_new_token():
    r = requests.request("GET", "https://open.spotify.com/")
    r_text = BeautifulSoup(r.content, "html.parser").find("script", {"id": "config"}).get_text()
    return json.loads(r_text)['accessToken']

def get_tracks(playlist_id, offset, limit, token):
    print(f"{Fore.BLUE}Getting tracks from playlist...")
    url = "https://api.spotify.com/v1/playlists/" + str(playlist_id) + "/tracks?offset=" + str(offset) + "&limit=" + str(limit) + "&market=GB"
    payload={}
    headers = {
      'authorization': 'Bearer ' + str(token),
      'Sec-Fetch-Dest': 'empty',
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)

def ParsePlaylist(playlist_id):
    global PlaylistTracks
    done = False
    offset_counter = 0
    while not done:
        new_token = get_new_token()
        data = get_tracks(playlist_id, offset_counter, 100, new_token)
        if(data['total'] > 0):
            limit = data['limit']
            offset = data['offset']
            total = data['total']
            if(offset < total):
                offset_counter += limit
            else:
                done = True
            for song in data['items']:
                song_name = song['track']['name']
                artist_name = song['track']['artists'][0]['name']
                PlaylistTracks.append(f"{artist_name} - {song_name}")
        else:
            print('Playlist is empty')
            done = True



def DownloadTrack(TrackName):
    print(f"{Fore.GREEN}Started downloading{Fore.BLUE} {TrackName}{Fore.RESET}")
    url = "https://www.youtube.com/watch?v=" + VideosSearch(f'{TrackName}', limit = 1).result()['result'][0]['id']
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    #print("Enter the destination address (leave blank to save in current directory)")
    destination =  '.'
    out_file = video.download(output_path=destination)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    try:
        os.rename(out_file, new_file)
    except:
        os.remove(out_file)
    print(Fore.GREEN + "downloaded")




pl = input('\nEnter the spotify playlist link or id > ')
if('playlist/' in pl):
    pl = pl.split('playlist/')[1]
if('?' in pl):
    pl = pl.split('?')[0]


ParsePlaylist(pl)


os.system("cls")
print(f"{len(PlaylistTracks)} tracks found in playlist, start downloading...")
for track in PlaylistTracks:
    try:
        DownloadTrack(track)
    except KeyboardInterrupt:
        print(f"{Fore.RED}{track} skipped{Fore.RESET}")
    except:
        print(f"{Fore.RED}Error downloading {track}")
