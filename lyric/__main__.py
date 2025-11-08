from scraper import fetch_lyrics, fetch_songs

if __name__ == "__main__":
    query = "Bohemian Rhapsody"
    songs = fetch_songs(query=query)
    print("Search results: ", songs[:3])

    if songs:
        lyrics = fetch_lyrics(songs[0]["url"])
        print(f"Lyrics for {songs[0]['title']}:\n")
        print(lyrics)
