import sys

from scraper import fetch_lyrics, fetch_songs


def select_song():
    print("Song: ", file=sys.stderr, end="")
    query = input()
    songs = fetch_songs(query)

    for i, song in enumerate(songs):
        print(i, ". ", song["title"], file=sys.stderr, end="\n")

    print("Select song: ", file=sys.stderr, end="")
    song_index = int(input())
    lyrics = fetch_lyrics(songs[song_index]["url"])
    print(lyrics)


if __name__ == "__main__":
    select_song()
