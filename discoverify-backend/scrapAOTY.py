import googlesearch
import requests
from collections import defaultdict
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


def search_album_of_the_year(artist):
    query = f"albumoftheyear {artist}"
    search_results = googlesearch.search(query, num=5, stop=5, pause=2)

    for result in search_results:
        if result.startswith("https://www.albumoftheyear.org/artist/"):
            return result
    return None

# ===================================================================
# NOT AVAILABLE: AOTY doesn't let me retrieve data from artist pages
# ===================================================================

# def is_url_allowed_by_robots(url):
#     robots_url = "https://www.albumoftheyear.org/robots.txt"
#     parsed_url = urlparse(url)
#     base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

#     # Get the content of robots.txt
#     response = requests.get(robots_url)
#     if response.status_code != 200:
#         print("Failed to retrieve robots.txt content.")
#         return False

#     robots_content = response.text

#     # Parse robots.txt content
#     robots_parser = RobotFileParser()
#     robots_parser.parse(robots_content)

#     # Check if the URL is allowed
#     return robots_parser.can_fetch("*", url)


# def extract_genres(artist_url, genres_counter):
#     # Check if the URL is allowed by the robots.txt file
#     if not is_url_allowed_by_robots(artist_url):
#         print("Access to this URL is not allowed by robots.txt.")
#         return

#     response = requests.get(artist_url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, "html.parser")
#         detail_rows = soup.find_all("div", class_="detailRow")

#         for row in detail_rows:
#             genre_link = row.find("a", href=lambda href: href and "genre" in href)
#             if genre_link:
#                 genre_text = genre_link.text.strip()
#                 genres_counter[genre_text] += 1

artist_name = ["Ornatos Violeta", "Twenty One Pilots", "The Weeknd", "Pearl Jam", "††† (crosses)"]
# print(f"Artist's name: {artist_name}")
artist_url = []
for artist in artist_name:
    result_url = search_album_of_the_year(artist)

    if result_url:
        print(f"The URL for {artist} on Album of the Year is: {result_url}")
        artist_url.append(result_url)
    else:
        print(f"No results found for {artist} on Album of the Year.")

artist_page = dict()
for i in range(5):
    artist_page[artist_name[i]] = artist_url[i]
# print(artist_page)


# ===================================================================
# NOT AVAILABLE: AOTY doesn't let me retrieve data from artist pages
# ===================================================================
    
# for url in artist_url:
#     genres_counter = defaultdict(int)
#     extract_genres(url, genres_counter)

#     if genres_counter:
#         print("Genres and their counts:")
#         for genre, count in genres_counter.items():
#             print(f"{genre}: {count}")
#     else:
#         print("No genres found on the artist's page.")

# url = "https://www.albumoftheyear.org/album/8780-ornatos-violeta-cao.php"
# genres_counter = defaultdict(int)
# extract_genres(url, genres_counter)

# if genres_counter:
#     print("Genres and their counts:")
#     for genre, count in genres_counter.items():
#         print(f"{genre}: {count}")
# else:
#     print("No genres found on the artist's page.")

# from albumoftheyearapi import ArtistMethods

# client = ArtistMethods()
# print(client.similar_artists('5812-crosses'))
