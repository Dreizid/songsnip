import atexit
import tempfile
from typing import Optional

import demucs.separate

TMPDIR = tempfile.TemporaryDirectory()
atexit.register(TMPDIR.cleanup)


def split_audio(audio_path: str, output_path: Optional[str] = None) -> str:
    args = ["--two-stems", "vocals", "-n", "htdemucs_ft", audio_path]
    if output_path is not None:
        args.extend(["-o", output_path])
    else:
        args.extend(["-o", TMPDIR.name])
    demucs.separate.main(args)

    return TMPDIR.name if output_path is None else output_path
