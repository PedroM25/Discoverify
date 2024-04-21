import time
from flask import Flask, redirect, request, session, url_for, render_template
import requests
import pandas as pd
import json
import subprocess

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a random secret key

# Spotify API credentials
CLIENT_ID = '377e5bb50c4d43d0938abbafb4d6829d'
CLIENT_SECRET = '5687d169707347599c8722ce0198598c'
REDIRECT_URI = 'http://localhost:5000/callback'  # Update this with your redirect URI

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spotify_login')
def spotify_login():
    # Generate Spotify OAuth URL
    auth_url = (
        "https://accounts.spotify.com/authorize?"
        f"client_id={CLIENT_ID}&"
        "response_type=code&"
        f"redirect_uri={REDIRECT_URI}&"
        "scope=user-read-private%20user-top-read%20playlist-modify-public%20playlist-modify-private"  # Add playlist scopes
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Handle Spotify callback
    code = request.args.get('code')
    if code:
        # Exchange authorization code for access token
        token_url = "https://accounts.spotify.com/api/token"
        auth_header = (CLIENT_ID, CLIENT_SECRET)
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI
        }
        response = requests.post(token_url, data=data, auth=auth_header)
        if response.status_code == 200:
            access_token = response.json()['access_token']
            session['access_token'] = access_token  # Store access token in session
            return redirect(url_for('profile'))
        else:
            return "Failed to obtain access token"
    else:
        return "Authorization code not received"
    
@app.route('/profile')
def profile():
    # Fetch user profile using the access token
    access_token = session.get('access_token')
    if access_token:
        profile_url = "https://api.spotify.com/v1/me"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(profile_url, headers=headers)
        if response.status_code == 200:
            profile_data = response.json()
            user_id = profile_data['id']
            
            # Fetch top artists
            top_artists_url = f"https://api.spotify.com/v1/me/top/artists?limit=5"
            response = requests.get(top_artists_url, headers=headers)
            if response.status_code == 200:
                top_artists_data = response.json()
                artists = [artist['name'] for artist in top_artists_data['items']]
                data = {"display_name": profile_data['display_name'], "id": profile_data['id'], "top_artists": artists}
                return f"name: {profile_data['display_name']}" #render_template('create_playlist', data=data)
            else:
                error_message = f"Failed to fetch top artists. Response: {response.text}"
                return error_message, response.status_code
        else:
            return f"Failed to fetch profile data. Response: {response.text}", response.status_code
    else:
        return redirect(url_for('index'))

    
@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    access_token = session.get('access_token')
    if access_token:

        try:
            subprocess.run(['python', 'file_b.py'], check=True)
        except subprocess.CalledProcessError as e:
            print("Error while running file B:", e)
        
        data = pd.read_csv('discoverify-backend/data/playlist_scores.csv')
        data = data.iloc[0:15, :]

        names = data.iloc[:, 1].values.tolist()
        artists = data.iloc[:, 0].values.tolist()
        size = len(names)

        # Initialize an empty list to store track URIs
        track_uris = []
        # Iterate over the tracks and search for each track on Spotify
        for i in range(size):
            search_url = "https://api.spotify.com/v1/search"
            params = {
                'q': f"{names[i]} artist:{artists[i]}",
                'type': 'track',
                'limit': 1
            }
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.get(search_url, headers=headers, params=params)
            if response.status_code == 200:
                # Extract the track URI from the response and append it to the list
                track_data = response.json()['tracks']['items']
                if track_data:
                    track_uris.append(track_data[0]['uri'])
        # Once all track URIs are obtained, create the playlist and add tracks to it
        if track_uris:
            create_playlist_url = "https://api.spotify.com/v1/me/playlists"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            playlist_data = {
                'name': 'My new playlist',
                'description': 'This is my new playlist created by Discoverify!',
                'public': False  # You can change this as needed
            }
            response = requests.post(create_playlist_url, headers=headers, data=json.dumps(playlist_data))
            if response.status_code == 201:
                playlist_id = response.json()['id']
                # Add tracks to the playlist
                add_tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
                data = {
                    'uris': track_uris
                }
                response = requests.post(add_tracks_url, headers=headers, data=json.dumps(data))
                print(response.status_code)
                if response.status_code == 200:
                    return "Playlist created and tracks added successfully!", 201
                else:
                    error_message = f"Failed to add tracks to playlist. Response: {response.text}"
                    return error_message, response.status_code
            else:
                error_message = f"Failed to create playlist. Response: {response.text}"
                return error_message, response.status_code
        else:
            return "No tracks found or no track URIs obtained", 404
    else:
        return redirect(url_for('index'))

@app.route('/display_playlist/<playlist_id>', methods=['GET'])
def display_playlist(playlist_id):
    # Fetch user profile using the access token
    access_token = session.get('access_token')
    if access_token:
        # Get playlist details
        playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(playlist_url, headers=headers)
        if response.status_code == 200:
            playlist = response.json()
            names = []
            for item in playlist['tracks']['items']:
                artists = []
                for artist in item['track']['artists']:
                    artists.append(artist['name'])
                names.append((item['track']['name'], artists))
            print(names)
            return "Names printed!"
        else:
            error_message = f"Failed to fetch playlist. Response: {response.text}"
            return error_message, response.status_code
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

