import requests, os, base64, json
from dotenv import load_dotenv
from pathlib import Path
from string import punctuation

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes),"utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization":"Basic " + auth_base64,
        "Content-Type":"application/x-www-form-urlencoded"
    }
    data = {"grant_type":"client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def clean_data(result):
    for char in punctuation:
        if char in result:
            result = result.replace(char,'')
    return result

def cleanup():
    for root, dir, files  in os.walk('.', topdown=True):
        for file in files:
            if not file.isascii():
                os.rename(os.path.join(root, file), os.path.join(root, file).encode('ascii',errors='ignore'))

def get_authorization(token):
    return {"Authorization":"Bearer " + token}

def getAllArtists(filename):
    with open(filename,'r') as f:
        reader = f.readlines()
    return reader

def getArtists(filename, lookfor):
    artists = []
    with open(filename,'r') as f:
        for line in f:
            if line.upper().startswith(lookfor):
                artists.append(line.strip('\n'))
    return artists

def findArtist(token, name):
    url = "https://api.spotify.com/v1/search"
    headers = get_authorization(token)
    query = url + "?" + f"q={name}&type=artist&limit=1"
    result = requests.get(query, headers=headers)
    jresult = json.loads(result.content)["artists"]["items"]
    if len(jresult) == 0:
        return None
    return jresult[0]

def findAlbums(token, id):
    url = f'https://api.spotify.com/v1/artists/{id}/albums?market=GB'
    headers = get_authorization(token)
    result = requests.get(url, headers=headers)
    jresult = json.loads(result.content)["items"]
    return jresult

def findTracks(token, id):
    url = f'https://api.spotify.com/v1/albums/{id}/tracks?market=GB'
    headers = get_authorization(token)
    result = requests.get(url, headers=headers)
    jresult = json.loads(result.content)['items']
    return jresult

if __name__ == "__main__":
    token = get_token()

    #dirs = getArtists('music.txt','L')
    dirs = getAllArtists('music.txt')
    for dir in dirs:
        if not os.path.exists(dir[0]):
            os.mkdir(dir[0])

        artist = findArtist(token,dir)
        artist['name'] = clean_data(artist['name'])
        if not os.path.exists(dir[0] + "/" + artist['name']):
            os.mkdir(dir[0] + "/" + artist['name'])
    
        albums = findAlbums(token, artist['id'])
        for album in albums:
            album['name'] = clean_data(album['name'])
            if not os.path.exists(dir[0] + "/" + artist['name'] + "/" + album['name']):
                os.mkdir(dir[0] + "/" + artist['name'] + "/" + album['name'])
        
            tracks = findTracks(token, album['id'])
            for track in tracks:
                track['name'] = clean_data(track['name'])
                print(f"./{album['name']}/{track['name']}")
                try:
                    Path(f"./{dir[0]}/{artist['name']}/{album['name']}/{track['name']}").touch()
                except:
                    pass