import json
import os
import re

import bs4
import requests
from bs4.element import NavigableString, Tag
from dotenv import load_dotenv

load_dotenv()


def fetch_songs(query: str):
    base_url = "https://api.genius.com/search"
    header = {"Authorization": f"Bearer {os.getenv('GENIUS_API_KEY')}"}
    params = {"q": query}
    response = requests.get(url=base_url, headers=header, params=params)
    response_dict = json.loads(response.text)
    songs = [
        {"title": song["result"]["full_title"], "url": song["result"]["url"]}
        for song in response_dict["response"]["hits"]
    ]
    return songs


def fetch_lyrics(url: str):
    response = requests.get(url)
    results = response.text
    soup = bs4.BeautifulSoup(results, "html.parser")
    headers = soup.find_all("div", class_=re.compile("LyricsHeader"))
    if headers:
        for header in headers:
            header.decompose()

    lyrics = ""
    lyric_container = soup.find_all("div", attrs={"data-lyrics-container": "true"})
    for lyric in lyric_container:
        if not lyric.contents:
            lyrics += "\n"
            continue
        for content in lyric.contents:
            assert isinstance(content, (NavigableString, Tag))
            if content.name == "br":
                lyrics += "\n"
            elif isinstance(content, NavigableString):
                lyrics += str(content)
            elif content.get("data-exclude-from-selection") != "true":
                lyrics += content.get_text(separator="\n")
    return lyrics
