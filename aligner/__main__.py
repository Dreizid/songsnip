import argparse
import os

from .aligner import align_audio_text


def main(audio_path: str, lyric_path: str):
    audio_path = os.path.expanduser(audio_path)
    lyric_path = os.path.expanduser(lyric_path)
    aligned_words = align_audio_text(audio_path, lyric_path)
    for word in aligned_words:
        print(word)


def cli():
    parser = argparse.ArgumentParser(description="Align audio and text files")
    parser.add_argument("audio_path", help="Path of the audio")
    parser.add_argument("lyric_path", help="Path to the lyric file")
    args = parser.parse_args()
    main(args.audio_path, args.lyric_path)


if __name__ == "__main__":
    cli()
