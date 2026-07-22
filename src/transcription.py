import os
import re
import subprocess
import tempfile
from collections import Counter
import gc
from pathlib import Path

import torch
import whisper


WHISPER_MODEL_NAME = "base.en"


def load_whisper_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"

    return whisper.load_model(
        WHISPER_MODEL_NAME,
        device=device,
    )


def normalize_audio(source_path: str, output_path: str) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        source_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        "-af",
        (
            "highpass=f=70,"
            "lowpass=f=7600,"
            "loudnorm=I=-18:TP=-2:LRA=11"
        ),
        output_path,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg could not prepare the recording:\n"
            + result.stderr.strip()
        )


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)

    return text


def repeated_phrase_ratio(words: list[str]) -> float:
    if len(words) < 8:
        return 0.0

    highest_ratio = 0.0

    for size in range(2, 9):
        if len(words) < size * 2:
            continue

        phrases = [
            tuple(words[index:index + size])
            for index in range(len(words) - size + 1)
        ]

        counts = Counter(phrases)
        most_common_count = counts.most_common(1)[0][1]

        covered_words = most_common_count * size
        ratio = covered_words / len(words)
        highest_ratio = max(highest_ratio, ratio)

    return highest_ratio


def validate_transcript(
    transcript: str,
    task_name: str,
) -> None:
    lowered = transcript.lower()
    words = re.findall(r"[a-zA-Z']+", lowered)

    if not words:
        raise RuntimeError(
            "No understandable speech was detected. "
            "Please record again in a quieter location."
        )

    prompt_leak_phrases = (
        "theft picture in english",
        "participant is describing",
        "participant is naming animals",
        "you can use the word",
    )

    if any(phrase in lowered for phrase in prompt_leak_phrases):
        raise RuntimeError(
            "The transcription was unreliable and contained "
            "generated boilerplate. Please record again."
        )

    phrase_ratio = repeated_phrase_ratio(words)

    if phrase_ratio >= 0.65:
        raise RuntimeError(
            "The transcription contained an artificial repeated-phrase "
            "loop. Please record again with less background noise."
        )

    unique_ratio = len(set(words)) / len(words)

    if len(words) >= 20 and unique_ratio < 0.18:
        raise RuntimeError(
            "The transcription was excessively repetitive and could "
            "not be analyzed reliably. Please record again."
        )

    if task_name == "cookie":
        if len(words) < 10:
            raise RuntimeError(
                "Too little understandable speech was detected for the "
                "Cookie Theft Picture Description Task."
            )

    elif task_name == "fluency":
        if len(words) < 3:
            raise RuntimeError(
                "Too few understandable words were detected for the "
                "Semantic Verbal Fluency Test."
            )

    else:
        raise ValueError(f"Unknown task name: {task_name}")


def transcribe_audio_bytes(
    audio_bytes: bytes,
    task_name: str,
) -> str:
    if not audio_bytes:
        raise ValueError("No audio data was received.")

    source_path = None
    normalized_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as source_file:
            source_file.write(audio_bytes)
            source_path = source_file.name

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as normalized_file:
            normalized_path = normalized_file.name

        normalize_audio(
            source_path,
            normalized_path,
        )

        model = load_whisper_model()

        result = model.transcribe(
            normalized_path,
            language="en",
            task="transcribe",
            temperature=0,
            condition_on_previous_text=False,
            fp16=torch.cuda.is_available(),
            no_speech_threshold=0.55,
            logprob_threshold=-1.0,
            compression_ratio_threshold=2.2,
            verbose=False,
        )

        transcript = normalize_text(
            result.get("text", "")
        )

        validate_transcript(
            transcript,
            task_name,
        )

        return transcript

    finally:
        # Release Whisper before the acoustic fusion model loads.
        if "model" in locals():
            del model

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        gc.collect()

        for file_path in (
            source_path,
            normalized_path,
        ):
            if file_path and Path(file_path).exists():
                os.remove(file_path)
