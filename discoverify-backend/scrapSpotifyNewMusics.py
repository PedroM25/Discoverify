import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import os
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get client ID and client secret from environment variables
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# Get audio features of every song onf every album mentioned in the playlist
def get_features_playlist(playlist_url, csv_filename):
    # Initialize Spotipy with your credentials
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Extract playlist ID from URL using regular expression
    playlist_id = re.findall(r'/playlist/([^/?]+)', playlist_url)[0]
    
    # Get tracks from the playlist
    results = sp.playlist_tracks(playlist_id)
    
    # Get current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Define directory name
    directory_name = 'data'
    
    # Create directory if it doesn't exist
    data_directory = os.path.join(current_directory, directory_name)
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    
    # Open CSV file for writing inside the 'data' directory
    with open(os.path.join(data_directory, csv_filename), mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'artists', 'spotify_link', 'acousticness', 
                      'danceability', 'energy', 'instrumentalness', 'liveness', 
                      #'loudness', 
                      'speechiness', 'valence']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write CSV header
        writer.writeheader()
        
        # Iterate through tracks and extract song information and audio features
        for item in results['items']:
            track = item['track']
            if track is not None:
                song_info = {}
                song_info['name'] = track['name']
                song_info['artists'] = ', '.join([artist['name'] for artist in track['artists']])
                song_info['spotify_link'] = track['external_urls']['spotify']
                
                # Get audio features if available
                audio_features = sp.audio_features(track['id'])[0]
                if audio_features is not None:
                    for feature in ['acousticness', 'danceability', 'energy', 
                                    'instrumentalness', 'liveness', 
                                    # 'loudness', 
                                    'speechiness', 'valence']:
                        song_info[feature] = audio_features[feature]
                else:
                    # If audio features are not available, set them to None
                    for feature in ['acousticness', 'danceability', 'energy', 
                                    'instrumentalness', 'liveness', 
                                    # 'loudness', 
                                    'speechiness', 'valence']:
                        song_info[feature] = None
                
                # Write song info and features to CSV
                writer.writerow(song_info)

# playlist_url = 'https://open.spotify.com/playlist/37i9dQZF1DX4JAvHpjipBk?si=c96f2a225c1f4817'
# csv_filename = 'playlist_data.csv'
# get_features_playlist(playlist_url, csv_filename)
# print("Playlist data saved to:", os.path.join('data', csv_filename))
