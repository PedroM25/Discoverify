import traceback
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import csv
from dotenv import load_dotenv
from scrapSpotifyNewMusics import get_features_playlist
from scrapSpotifyClassifier import score_calculator, average_audio_features

# Load environment variables from .env file
load_dotenv()

# Get client ID and client secret from environment variables
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# Authenticate with Spotify API and request necessary scope
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:8888/callback",
        scope="user-read-recently-played",
    )
)


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


if __name__ == "__main__":
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
