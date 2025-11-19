import os

import torch
from ctc_forced_aligner import (
    generate_emissions,
    get_alignments,
    get_spans,
    load_alignment_model,
    load_audio,
    postprocess_results,
    preprocess_text,
)


def load_resources(audio_path: str, text_path: str):
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load model
    alignment_model, alignment_tokenizer = load_alignment_model(
        device,
        dtype=torch.float16 if device == "cuda" else torch.float32,
    )

    # Load audio
    audio_waveform = load_audio(
        audio_path, alignment_model.dtype, alignment_model.device
    )

    # Load lyrics
    with open(text_path, "r") as f:
        lines = f.readlines()
    text = "".join(line for line in lines).replace("\n", " ").strip()

    return alignment_model, alignment_tokenizer, audio_waveform, text


def prepare_text(text: str, language: str = "iso"):
    tokens_starred, text_starred = preprocess_text(
        text,
        romanize=True,
        language=language,
    )

    return tokens_starred, text_starred


def run_model(alignment_model, audio_waveform, batch_size: int = 16):
    emissions, stride = generate_emissions(
        alignment_model, audio_waveform, batch_size=batch_size
    )

    return emissions, stride


def align_tokens(emissions, tokens_starred, alignment_tokenizer):
    segments, scores, blank_token = get_alignments(
        emissions,
        tokens_starred,
        alignment_tokenizer,
    )

    spans = get_spans(tokens_starred, segments, blank_token)

    return spans, scores, blank_token


def compute_word_timestamps(text_starred, spans, stride, scores):
    return postprocess_results(text_starred, spans, stride, scores)


def align_audio_text(audio_path: str, text_path: str):
    model, tokenizer, audio, text = load_resources(
        audio_path=audio_path, text_path=text_path
    )
    tokens_starred, text_starred = prepare_text(text)
    emissions, stride = run_model(model, audio)
    spans, scores, blank_token = align_tokens(emissions, tokens_starred, tokenizer)
    word_timestamps = compute_word_timestamps(text_starred, spans, stride, scores)

    return word_timestamps
