import os

from .aligner import align_audio_text


def main():
    audio_path = os.path.expanduser("~/mfa_data/firstluv.wav")
    text_path = os.path.expanduser("~/mfa_data/firstluv.txt")
    aligned_words = align_audio_text(audio_path, text_path)
    for word in aligned_words:
        print(word)


if __name__ == "__main__":
    main()
