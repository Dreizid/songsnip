import atexit
import tempfile
from typing import Optional

import demucs.separate


def split_audio(audio_path: str, output_path: Optional[str] = None) -> str:
    if output_path is None:
        TMPDIR = tempfile.TemporaryDirectory()
        atexit.register(TMPDIR.cleanup)
        output_path = TMPDIR.name
    args = ["--two-stems", "vocals", "-n", "htdemucs_ft", audio_path, "-o", output_path]
    demucs.separate.main(args)

    return output_path
