import atexit
import os
import subprocess
import tempfile


def convert_to_wav(input_path: str, verbose: bool = False) -> str:
    """
    Convert any audio format into .wav format.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file '{input_path}' does not exist.")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        output_path = tmpfile.name

    if verbose:
        stdout_setting = None
        stderr_setting = None
    else:
        stdout_setting = subprocess.DEVNULL
        stderr_setting = subprocess.DEVNULL

    subprocess.run(
        ["ffmpeg", "-i", input_path, "-y", output_path],
        check=True,
        stdout=stdout_setting,
        stderr=stderr_setting,
        text=True,
    )

    atexit.register(lambda: os.path.exists(output_path) and os.remove(output_path))
    return output_path
