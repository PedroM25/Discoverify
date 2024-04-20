import time
from flask import Flask, redirect, request, session, url_for, render_template
import requests

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
        "scope=user-read-private%20user-top-read%20playlist-modify-public"  # Add playlist-modify-public scope
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
                return render_template('', data=data)
            else:
                error_message = f"Failed to fetch top artists. Response: {response.text}"
                return error_message, response.status_code
        else:
            return f"Failed to fetch profile data. Response: {response.text}", response.status_code
    else:
        return redirect(url_for('index'))

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    # Fetch user profile using the access token
    access_token = session.get('access_token')
    if access_token:
        # Get song data from the JSON request
        data = request.json

        # Assume data is a list of tuples, first value name of the song, second a list with the artists
        songs = data.get('songs')
        song_titles = [t[0] for t in songs]
        song_artists = [t[1] for t in songs]
                
        # Create playlist
        create_playlist_url = "https://api.spotify.com/v1/me/playlists"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        playlist_data = {
            'name': 'My New Playlist',
            'description': 'This is my new playlist created by my Flask app!'
        }

        response = requests.post(create_playlist_url, headers=headers, json=playlist_data)
        if response.status_code == 201:
            
            playlist_id = response.json()['id']
            
            # Add songs to the playlist
            add_tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

            for i in range(len(song_titles)):
                # Search for the track based on name and artist
                search_url = "https://api.spotify.com/v1/search"
                params = {
                    'q': f"track:{song_titles[i]} artist:{song_artists[i][0]}",
                    'type': 'track',
                    'limit': 1
                }
                response = requests.get(search_url, headers=headers, params=params)
                if response.status_code == 200:
                
                    tracks = response.json()['tracks']['items']
                    if tracks:
                        track_uri = tracks[0]['uri']
                    
                        data = {
                            'uris': [track_uri]
                        }
                        response = requests.post(add_tracks_url, headers=headers, json=data)
                        if response.status_code == 200:
                            continue
                            # Redirect to display endpoint with playlist_id
                            # return redirect(url_for(f'display_playlist', playlist_id=playlist_id))
                        else:
                            error_message = f"Failed to add song to playlist. Response: {response.text}"
                            return error_message, response.status_code
                    else:
                        return f"Song '{song_titles[i]}' by '{song_artists[i]}' not found", 404
                else:
                    return "Failed to search for tracks", response.status_code
        else:
            error_message = f"Failed to create playlist. Response: {response.text}"
            return error_message, response.status_code
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

