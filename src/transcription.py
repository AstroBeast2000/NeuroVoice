import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path


WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME", "small.en")


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
        "highpass=f=70,lowpass=f=7600",
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
        ratio = most_common_count * size / len(words)
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
            "The transcription contained generated boilerplate. "
            "Please record again."
        )

    if repeated_phrase_ratio(words) >= 0.65:
        raise RuntimeError(
            "The transcription contained an artificial repeated phrase loop."
        )

    unique_ratio = len(set(words)) / len(words)

    if len(words) >= 20 and unique_ratio < 0.18:
        raise RuntimeError(
            "The transcription was excessively repetitive."
        )

    if task_name == "cookie" and len(words) < 10:
        raise RuntimeError(
            "Too little understandable speech was detected for the "
            "Cookie Theft task."
        )

    if task_name == "fluency" and len(words) < 3:
        raise RuntimeError(
            "Too few understandable words were detected for the "
            "verbal fluency task."
        )


def transcribe_with_subprocess(
    audio_path: str,
    output_directory: str,
) -> str:
    command = [
        sys.executable,
        "-m",
        "whisper",
        audio_path,
        "--model",
        WHISPER_MODEL_NAME,
        "--language",
        "English",
        "--task",
        "transcribe",
        "--device",
        "cpu",
        "--fp16",
        "False",
        "--temperature",
        "0",
        "--condition_on_previous_text",
        "False",
        "--output_format",
        "txt",
        "--output_dir",
        output_directory,
        "--verbose",
        "False",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        timeout=int(os.environ.get("WHISPER_TIMEOUT_SECONDS", "1200")),
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Whisper transcription failed:\n"
            + result.stderr[-3000:]
        )

    transcript_path = (
        Path(output_directory)
        / f"{Path(audio_path).stem}.txt"
    )

    if not transcript_path.exists():
        raise RuntimeError(
            "Whisper finished but did not create a transcript."
        )

    return transcript_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def transcribe_audio_bytes(
    audio_bytes: bytes,
    task_name: str,
) -> str:
    if not audio_bytes:
        raise ValueError("No audio data was received.")

    with tempfile.TemporaryDirectory() as temp_directory:
        source_path = Path(temp_directory) / "source.wav"
        normalized_path = Path(temp_directory) / "normalized.wav"
        transcript_directory = Path(temp_directory) / "transcript"

        transcript_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        source_path.write_bytes(audio_bytes)

        normalize_audio(
            str(source_path),
            str(normalized_path),
        )

        transcript = transcribe_with_subprocess(
            str(normalized_path),
            str(transcript_directory),
        )

        transcript = normalize_text(transcript)

        validate_transcript(
            transcript,
            task_name,
        )

        return transcript


