from dotenv import load_dotenv
from flask import Flask, request, redirect, session, url_for
import os
import base64
from requests import post, get
import json
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
import requests


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = os.getenv("CLIENT_ID") # Goes into the .env file and grabs the values we reference in the parameter passed
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = 'http://127.0.0.1:5000/callback'
scope = 'user-read-recently-played'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id = client_id,
    client_secret = client_secret,
    redirect_uri=redirect_uri,
    scope = scope,
    cache_handler=cache_handler,
    show_dialog = True
)

sp = Spotify(auth_manager=sp_oauth)

@app.route('/')
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('get_recently_played'))

def validate_token():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

# we have to refresh the token when it expires
@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'], False)
    return redirect(url_for('get_recently_played'))

@app.route('/get_recently_played')
def get_recently_played():
    validate_token()

    recently_played = sp.current_user_recently_played(limit=50) 
    recently_played_info = [] # list comprehension
    songs = []
    for idx, item in enumerate(recently_played['items']):
        track = item['track']
        recently_played_info.append(f"{idx+1} {track['artists'][0]['name']} - {track['name']}")

    for item in recently_played["items"]:
        track = item["track"]

        songs.append({
            "song_name" : track["name"],
            "artist":track["artists"][0]["name"],
            "album": track["album"]["name"]
        })
    
    with open("recently_played.json", "w", encoding="utf-8") as file:
        json.dump(songs, file, indent=4)
    return recently_played_info


#clear the session, log out. remove access token and everything from the session
@app.route('/logout')
def logout():
    session.clear() # clears everything in session
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
