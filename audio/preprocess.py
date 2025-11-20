import atexit
import os
import subprocess
import tempfile


def convert_to_wav(input_path: str) -> str:
    """
    Convert any audio format into .wav format.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        output_path = tmpfile.name
    process = subprocess.run(
        ["ffmpeg", "-i", input_path, "-y", output_path]
        check=True,
        stdout=subprocess.subprocess.DEVNULL,
        stderr=subprocess.subprocess.DEVNULL,
        text=True
    )

    atexit.register(lambda: os.path.exists(output_path) and os.remove(output_path))
    return output_path
