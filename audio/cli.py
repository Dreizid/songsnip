from pathlib import Path
from typing import Optional

import typer

from audio.preprocess import convert_to_wav
from audio.splitter import split_audio

app = typer.Typer(help="Audio splitting related commands")


@app.command()
def split(
    audio_path: Path,
    output_path: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Optional output path"
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose", help="Set output to be verbose"
    ),
):
    audio_path_str = str(audio_path)
    wav_audio_path = convert_to_wav(audio_path_str, verbose)
    split_audio_path = split_audio(wav_audio_path, str(output_path) if output_path else None)

    if verbose:
        typer.echo(split_audio_path)
