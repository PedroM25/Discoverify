from flask import Flask, redirect, request, session, url_for, render_template
import requests
import pandas as pd
import json
import spotipy
from spotipy import cache_handler
from spotipy.oauth2 import SpotifyOAuth
import os
import csv
from dotenv import load_dotenv
from discoverify_backend.scrapSpotifyNewMusics import get_features_playlist
from discoverify_backend.scrapSpotifyClassifier import score_calculator, average_audio_features

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a random secret key

# Spotify API credentials
CLIENT_ID = '377e5bb50c4d43d0938abbafb4d6829d'
CLIENT_SECRET = '5687d169707347599c8722ce0198598c'
REDIRECT_URI = 'http://localhost:5000/profile'  # Update this with your redirect URI
#SP_cache = cache_handler.CacheFileHandler()

auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-read-recently-played,user-read-private,user-top-read,playlist-modify-public,playlist-modify-private"
        #cache_handler=SP_cache
    )
sp = spotipy.Spotify(auth_manager)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spotify_login')
def spotify_login():
    return redirect(auth_manager.get_authorize_url())

#@app.route('/callback')
#def callback():
#    # Handle Spotify callback
 #   code = request.args.get('code')
 #   if code:
 #       # Exchange authorization code for access token
 #       token_url = "https://accounts.spotify.com/api/token"
 #       auth_header = (CLIENT_ID, CLIENT_SECRET)
 #       data = {
 #           'grant_type': 'authorization_code',
 #           'code': code,
 #           'redirect_uri': REDIRECT_URI
 #       }
 #       response = requests.post(token_url, data=data, auth=auth_header)
 #       if response.status_code == 200:
 #           access_token = response.json()['access_token']
 #           session['access_token'] = access_token  # Store access token in session
 #           return redirect(url_for('profile'))
 #       else:
 #           return "Failed to obtain access token"
 #   else:
 #       return "Authorization code not received"
 
 #   code = request.args.get('code')
 #   token_info = auth_manager.get_access_token(code)
 #   session['token_info'] = token_info
 #   return redirect("/profile")
    
@app.route('/profile')
def profile():
    # Fetch user profile using the access token
#    token_info = auth_manager.get_cached_token()
#
#    if token_info:
#        print("Found cached token!")
#        access_token = token_info['access_token']
#        print(token_info)

    user = sp.current_user()
    print(user)

#    if access_token:
#        profile_url = "https://api.spotify.com/v1/me"
#        headers = {'Authorization': f'Bearer {access_token}'}
#        response = requests.get(profile_url, headers=headers)
#        if response.status_code == 200:
#            profile_data = response.json()
#            user_id = profile_data['id']
#            
#            # Fetch top artists
#            top_artists_url = f"https://api.spotify.com/v1/me/top/artists?limit=5"
#            response = requests.get(top_artists_url, headers=headers)
#            if response.status_code == 200:
#                top_artists_data = response.json()
#                artists = [artist['name'] for artist in top_artists_data['items']]
#                data = {"display_name": profile_data['display_name'], "id": profile_data['id'], "top_artists": artists}
#                return f"name: {profile_data['display_name']}" #render_template('create_playlist', data=data)
#            else:
#                error_message = f"Failed to fetch top artists. Response: {response.text}"
#                return error_message, response.status_code
#        else:
#            return f"Failed to fetch profile data. Response: {response.text}", response.status_code
#    else:
#        return redirect(url_for('index'))

    
@app.route('/create_playlist')
def create_playlist():
    print(access_token)
    if access_token:

        scrapUser()
        
        data = pd.read_csv('discoverify_backend/data/playlist_scores.csv')
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

# Get current user's recently played tracks
def get_recently_played_tracks(limit=50):
    results = sp.current_user_recently_played(limit=limit)
    return results["items"]


# Get audio features for a track
def get_audio_features(track_id):
    return sp.audio_features(track_id)[0]


# Write data to CSV file
def write_to_csv(data, filename):
    # Get current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Define directory name
    directory_name = 'data'
    # Create directory if it doesn't exist
    data_directory = os.path.join(current_directory, directory_name)
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    # Write to CSV file inside the 'data' directory
    with open(os.path.join(data_directory, filename), mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Artist", "Track Name", "Spotify Link", "Acousticness", 
                         "Danceability", "Energy", "Instrumentalness", "Liveness", 
                         #"Loudness", 
                         "Speechiness", "Valence"])
        for row in data:
            writer.writerow(row)


# Print the names of the last 50 songs and retrieve their audio features
def get_features_history():
    data = []
    recently_played_tracks = get_recently_played_tracks()
    if recently_played_tracks:
        print("Retrieving audio features for recently played tracks...")
        for track in recently_played_tracks:
            track_name = track["track"]["name"]
            artist = track["track"]["artists"][0]["name"]  # Get the first artist's name
            spotify_link = track["track"]["external_urls"]["spotify"]
            audio_features = get_audio_features(track["track"]["id"])
            if audio_features:
                acousticness = audio_features["acousticness"]
                danceability = audio_features["danceability"]
                energy = audio_features["energy"]
                instrumentalness = audio_features["instrumentalness"]
                liveness = audio_features["liveness"]
                # loudness = audio_features["loudness"]
                speechiness = audio_features["speechiness"]
                valence = audio_features["valence"]
                data.append([artist, track_name, spotify_link, acousticness, 
                             danceability, energy, instrumentalness, liveness, 
                             # loudness, 
                             speechiness, valence])
    else:
        print("No recently played tracks found.")

    return data


def scrapUser():
    history_csv = "user_history_data.csv"
    playlist_csv = "playlist_data.csv"
    # Retrieve user's history
    data = get_features_history()
    if data:
        write_to_csv(data, history_csv)
        print("Data exported to data/user_history_data.csv")

    # New Music Friday Playlist URL
    playlist_url = 'https://open.spotify.com/playlist/37i9dQZF1DX4JAvHpjipBk?si=c96f2a225c1f4817'
    # Retrieve the stats referring to every song of every album mentioned in the playlist
    get_features_playlist(playlist_url, playlist_csv)
    print("Playlist data saved to:", os.path.join('data', playlist_csv))

    # Get average metrics
    average_metrics = average_audio_features(playlist_csv)

    playlist_full_scores = "playlist_scores.csv"

    score_calculator(average_metrics, playlist_csv, playlist_full_scores)
    print("Scores saved to", playlist_full_scores)
    # except FileNotFoundError:
    #     print("Error: playlist_scores.csv file not found.")
    #     traceback.print_exc()  # Print traceback for detailed error information

    # Final trimmed list [SOME ERRORS STILL]
    # best_scores = "final_list.csv"
    # score_trimmer(playlist_full_scores, best_scores)



if __name__ == '__main__':
    app.run(debug=True)

