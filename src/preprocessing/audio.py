from enum import StrEnum
import subprocess
import tempfile
import shutil
from pathlib import Path
from src.utils.hashing import calculate_file_hash
from src.config.paths import CACHE_ROOT


class DemucsModels(StrEnum):
    HTDEMUCS = "htdemucs"
    HTDEMUCS_FT = "htdemucs_ft"
    HTDEMUCS_MMI = "htdemucs_mmi"
    MDX = "mdx"
    MDX_EXTRA = "mdx_extra"


def _run_demucs(
    audio_path: Path, output_path: Path, model: DemucsModels = DemucsModels.HTDEMUCS
) -> Path:
    cmd = [
        "demucs",
        "--name",
        model.value,
        "-d",
        "cuda",
        "--float32",
        "-o",
        str(output_path),
        "--two-stems",
        "vocals",
        str(audio_path),
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Demucs failed execution. CLI Error: {e.stdout.strip()}"
        ) from e

    demucs_output = Path(output_path) / model.value / audio_path.stem / "vocals.wav"

    if not demucs_output.exists():
        raise FileNotFoundError("Demucs finished execution but vocal stem is missing.")

    return demucs_output


def split_audio(
    audio_path: Path | str,
    model: DemucsModels = DemucsModels.HTDEMUCS,
) -> Path:
    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(
            f"Unable to split audio. File {audio_path} does not exist."
        )

    # Evaluate cache
    file_hash = calculate_file_hash(audio_path)
    audio_cache_dir = CACHE_ROOT / "vocals"
    audio_cache_dir.mkdir(exist_ok=True, parents=True)
    file_cache_path = audio_cache_dir / f"{file_hash}.wav"

    if file_cache_path.exists():
        return file_cache_path

    with tempfile.TemporaryDirectory() as tmpdir:
        raw_vocal_stem = _run_demucs(
            audio_path=audio_path, model=model, output_path=Path(tmpdir)
        )
        shutil.move(str(raw_vocal_stem), str(file_cache_path))

    return file_cache_path
