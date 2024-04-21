import os
import csv
from math import fabs

def average_audio_features(csv_filename):
    # Get current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Define directory name
    directory_name = 'data'

    # Path to CSV file
    csv_path = os.path.join(current_directory, directory_name, csv_filename)

    # Check if the CSV file exists
    if not os.path.exists(csv_path):
        print(f"Error: {csv_filename} not found in {directory_name} directory.")
        return

    # Initialize variables to store column totals and count of rows
    column_totals = [0] * 7
    row_count = 0

    # Read CSV file and calculate totals
    with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Get header row
        for row in reader:
            # Check if row has enough columns
            if len(row) >= 7:
                # Convert values to floats and add to column totals
                for i in range(7):
                    # Check if the value is not empty
                    if row[-(i+1)] != '':
                        column_totals[i] += float(row[-(i+1)])  # Calculate from last 7 columns
                row_count += 1

    # Calculate average values
    if row_count > 0:
        average_values = [total / row_count for total in column_totals]
        # Combine column names with average values
        column_names = header[-7:]  # Get last 7 column names
        averages_with_names = list(zip(column_names, average_values))
        return averages_with_names
    else:
        print("Error: No data found in the CSV file.")
        return None


def score_calculator(
    average_values_with_names, playlist_csv_filename, output_csv_filename
):
    # Get current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Define directory name
    directory_name = "data"

    # Path to playlist CSV file
    playlist_csv_path = os.path.join(
        current_directory, directory_name, playlist_csv_filename
    )

    # Check if the playlist CSV file exists
    if not os.path.exists(playlist_csv_path):
        print(
            f"Error: {playlist_csv_filename} not found in {directory_name} directory."
        )
        return

    # Initialize variables to store the scores
    scores = []

    # Read playlist CSV file
    with open(playlist_csv_path, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        # Convert playlist column names to lowercase
        playlist_column_names = [name.lower() for name in reader.fieldnames]

        # Check if column names match
        if not set(playlist_column_names).issuperset(
            set([name.lower() for name, _ in average_values_with_names])
        ):
            print(
                "Error: Column names in the playlist data do not match with average values from user history data."
            )
            print("Playlist Column Names:", playlist_column_names)
            print(
                "User History Data Column Names:",
                [name for name, _ in average_values_with_names],
            )
            return

        for row in reader:
            # Initialize subscore and score for the current song
            subscores = []
            total_subscore = 0

            # Calculate subscore for each metric
            for column_name, average_value in average_values_with_names:
                metric_value_str = row[
                    column_name.lower()
                ]  # Convert playlist column name to lowercase
                if metric_value_str != "":
                    metric_value = float(metric_value_str)
                    subscore = 1 - fabs(average_value - metric_value)
                    subscores.append(subscore)
                else:
                    print(
                        f"Warning: Empty value found for {column_name.lower()} in row {row}. Skipping."
                    )

            # Calculate total subscore for the current song
            if subscores:
                total_subscore = sum(subscores) / len(subscores)

                # Append song info and score to the list
                song_info = {
                    "Artist(s)": row["artists"],
                    "Song Name": row["name"],
                    "Spotify Link": row["spotify_link"],
                    "Score": total_subscore,
                }
                scores.append(song_info)

    # Sort scores in descending order based on 'Score'
    scores.sort(key=lambda x: x["Score"], reverse=True)

    # Write sorted scores to output CSV file
    output_csv_path = os.path.join(
        current_directory, directory_name, output_csv_filename
    )
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Artist(s)", "Song Name", "Spotify Link", "Score"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for score in scores:
            writer.writerow(score)

    print(f"Scores saved to {output_csv_path}")


# TO COMPLETE!
# def score_trimmer(input_csv_filename, output_csv_filename):
#     # Initialize a list to store selected songs
#     selected_songs = []

#     # Get current directory
#     current_directory = os.path.dirname(os.path.abspath(__file__))

#     # Define directory name
#     directory_name = 'data'

#     # Path to playlist CSV file
#     playlist_csv_path = os.path.join(current_directory, directory_name, input_csv_filename)

#     # Check if the playlist CSV file exists
#     if not os.path.exists(playlist_csv_path):
#         print(f"Error: {input_csv_filename} not found in {directory_name} directory.")
#         return

#     # Read the input CSV file
#     with open(input_csv_filename, mode='r', newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             # Check if the song score is greater than or equal to 0.8
#             if float(row['Score']) >= 0.8:
#                 selected_songs.append({
#                     'Artist(s)': row['Artist(s)'],
#                     'Song Name': row['Song Name'],
#                     'Spotify Link': row['Spotify Link']
#                 })

#     # If fewer than 15 songs have a score >= 0.8, select the top 15 songs
#     if len(selected_songs) < 15:
#         # Sort the songs by score in descending order
#         selected_songs.sort(key=lambda x: float(x['Score']), reverse=True)
#         # Select the top 15 songs
#         selected_songs = selected_songs[:15]

#     # Write selected songs to the output CSV file
#     with open(output_csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
#         fieldnames = ['Artist(s)', 'Song Name', 'Spotify Link']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         for song in selected_songs:
#             writer.writerow(song)

#     print(f"Final list saved to {output_csv_filename}")

# csv_filename = 'user_history_data.csv'
# average_values_with_names = average_audio_features(csv_filename)

# playlist_csv_filename = "playlist_data.csv"
# output_csv_filename = "playlist_scores.csv"
# score_calculator(average_values_with_names, playlist_csv_filename, output_csv_filename)
