import requests
from bs4 import BeautifulSoup

def get_genres(artist_url):
    # Send a GET request to the artist's RateYourMusic page
    response = requests.get(artist_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the section containing genres
        genre_section = soup.find('span', {'class': 'profileGenres'})

        if genre_section:
            # Extract the genres
            genres = [genre.text.strip() for genre in genre_section.find_all('a')]
            return genres
        else:
            print("Genres not found on the page.")
            return []
    else:
        print("Failed to retrieve the page. Status code:", response.status_code)
        return []

# Example usage:
artist_url = 'https://rateyourmusic.com/artist/kendrick-lamar'
genres = get_genres(artist_url)
if genres:
    print("Genres:", genres)
