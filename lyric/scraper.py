import os
import re
from urllib.parse import urlparse

import bs4
import requests
from bs4.element import NavigableString, Tag
from dotenv import load_dotenv

load_dotenv()

ALLOWED_DOMAINS = ["genius.com"]
TIMEOUT_SECONDS = 20


def fetch_songs(query: str):
    """ "
    Fetches songs from genius.com based on the query.

    Parameters:
        query (str): The title of the song to search for.

    Returns:
        list of dict: A list of songs that match the query. Each dictionary contains:
            - 'title' (str): The title of the song.
            - 'url' (str): The URL for the song lyrics.
    """
    base_url = "https://api.genius.com/search"
    header = {"Authorization": f"Bearer {os.getenv('GENIUS_API_KEY')}"}
    params = {"q": query}
    response = requests.get(
        url=base_url, headers=header, params=params, timeout=TIMEOUT_SECONDS
    )
    response_dict = response.json()
    songs = [
        {"title": song["result"]["full_title"], "url": song["result"]["url"]}
        for song in response_dict["response"]["hits"]
    ]
    return songs


def fetch_lyrics(url: str):
    """
    Fetches and parses the lyrics of a song.

    Parameters:
        url (str): The URL of the song to scrape.

    Returns:
        str: The lyrics of the song.
    """
    if not is_allowed_url(url):
        raise ValueError("URL is not from a trusted source")
    response = requests.get(url, timeout=TIMEOUT_SECONDS)
    results = response.text
    soup = bs4.BeautifulSoup(results, "html.parser")
    headers = soup.find_all("div", class_=re.compile("LyricsHeader"))
    if headers:
        for header in headers:
            header.decompose()

    lyrics = []
    lyric_container = soup.find_all("div", attrs={"data-lyrics-container": "true"})
    if not lyric_container:
        print(f"Lyrics was not found in {url}")
        return None
    for lyric in lyric_container:
        if not lyric.contents:
            lyrics.append("\n")
            continue
        for content in lyric.contents:
            if not isinstance(content, (NavigableString, Tag)):
                raise TypeError("HTML Error")
            if content.name == "br":
                lyrics.append("\n")
            elif isinstance(content, NavigableString):
                lyrics.append(str(content))
            elif content.get("data-exclude-from-selection") != "true":
                lyrics.append(content.get_text(separator="\n"))
    return "".join(lyrics)


def is_allowed_url(url: str) -> bool:
    parsed = urlparse(url=url)
    hostname = parsed.hostname
    return bool(hostname) and any(
        hostname == d or hostname.endswith("." + d) for d in ALLOWED_DOMAINS
    )
