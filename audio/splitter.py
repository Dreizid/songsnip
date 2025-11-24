import atexit
import re
import tempfile
from pathlib import Path
from typing import Optional

import demucs.separate


def split_audio(audio_path: str, output_path: Optional[str] = None):
    if output_path is None:
        TMPDIR = tempfile.TemporaryDirectory()
        atexit.register(TMPDIR.cleanup)
        output_path = TMPDIR.name
    args = ["--two-stems", "vocals", "-n", "htdemucs_ft", audio_path, "-o", output_path]
    demucs.separate.main(args)

    REGEX_PATTERN = r"([\w\s\-_.()]+\.wav)$"
    audio_name_match = re.search(REGEX_PATTERN, audio_path)
    if audio_name_match:
        audio_name_str = audio_name_match.group(1)
        audio_name = Path(audio_name_str).stem
    else:
        raise ValueError(f"Could not extract .wav filename from path: {audio_path}")

    return str(Path(output_path) / "separated" / "htdemucs_ft" / audio_name)
