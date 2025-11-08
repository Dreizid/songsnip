import json
import os
import bs4
import requests
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


def main():
    songs = fetch_songs("let it")

main()
