from __future__ import annotations

import json
import lzma
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import joblib
import librosa
import numpy as np
import pandas as pd


MODEL_DIR = Path(__file__).resolve().parents[1] / "models" / "cookie"
MODEL_ARCHIVE_PATH = MODEL_DIR / "FINAL_clean_oof_stacking_model.joblib.xz"
CONFIG_PATH = MODEL_DIR / "cookie_fusion_extractor_config.json"


class CookieTheftEnsemble:
    """Transcript-plus-acoustic fusion model for Cookie Theft recordings."""

    def __init__(self) -> None:
        if not MODEL_ARCHIVE_PATH.exists():
            raise FileNotFoundError(
                f"Compressed fusion model not found: {MODEL_ARCHIVE_PATH}"
            )
        if not CONFIG_PATH.exists():
            raise FileNotFoundError(f"Extractor configuration not found: {CONFIG_PATH}")

        model_cache_dir = Path(tempfile.gettempdir()) / "neurovoice_models"
        model_cache_dir.mkdir(parents=True, exist_ok=True)
        model_cache_path = model_cache_dir / "FINAL_clean_oof_stacking_model.joblib"

        if (
            not model_cache_path.exists()
            or model_cache_path.stat().st_mtime < MODEL_ARCHIVE_PATH.stat().st_mtime
        ):
            temporary_model_path = model_cache_path.with_suffix(".joblib.tmp")
            with lzma.open(MODEL_ARCHIVE_PATH, "rb") as source, temporary_model_path.open("wb") as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)
            temporary_model_path.replace(model_cache_path)

        self.bundle: dict[str, Any] = joblib.load(model_cache_path)
        self.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

        required_keys = {
            "transcript_model",
            "audio_model",
            "stacker",
            "threshold",
            "feature_cols",
        }
        missing = required_keys.difference(self.bundle)
        if missing:
            raise ValueError(f"Fusion bundle is missing keys: {sorted(missing)}")

        self.transcript_model = self.bundle["transcript_model"]
        self.audio_model = self.bundle["audio_model"]
        self.stacker = self.bundle["stacker"]
        self.feature_cols = list(self.bundle["feature_cols"])
        self.threshold = float(self.bundle["threshold"])

        expected_count = int(self.config.get("expected_feature_count", 85))
        if len(self.feature_cols) != expected_count:
            raise ValueError(
                f"Expected {expected_count} acoustic features, "
                f"but the model requires {len(self.feature_cols)}."
            )

    @staticmethod
    def _positive_probability(model: Any, values: Any) -> float:
        probabilities = model.predict_proba(values)
        classes = list(model.classes_)
        if 1 not in classes:
            raise ValueError(f"Positive class 1 not found. Classes: {classes}")
        return float(probabilities[0, classes.index(1)])

    def _extract_audio_features(self, audio_path: str | Path) -> dict[str, float]:
        target_sr = self.config.get("target_sr")
        top_db = int(self.config.get("top_db", 20))
        n_fft = int(self.config.get("n_fft", 2048))
        hop_length = int(self.config.get("hop_length", 512))
        center = bool(self.config.get("center", True))
        normalize_audio = bool(self.config.get("normalize_audio", False))

        y, sr = librosa.load(str(audio_path), sr=target_sr, mono=True)
        if y.size == 0:
            raise ValueError("The recording contains no audio samples.")

        if normalize_audio:
            peak = float(np.max(np.abs(y)))
            if peak > 0:
                y = y / peak

        duration_sec = float(librosa.get_duration(y=y, sr=sr))

        rms = librosa.feature.rms(
            y=y,
            frame_length=n_fft,
            hop_length=hop_length,
            center=center,
        )[0]
        zcr = librosa.feature.zero_crossing_rate(
            y,
            frame_length=n_fft,
            hop_length=hop_length,
            center=center,
        )[0]
        centroid = librosa.feature.spectral_centroid(
            y=y, sr=sr, n_fft=n_fft, hop_length=hop_length, center=center
        )[0]
        bandwidth = librosa.feature.spectral_bandwidth(
            y=y, sr=sr, n_fft=n_fft, hop_length=hop_length, center=center
        )[0]
        rolloff = librosa.feature.spectral_rolloff(
            y=y, sr=sr, n_fft=n_fft, hop_length=hop_length, center=center
        )[0]
        flatness = librosa.feature.spectral_flatness(
            y=y, n_fft=n_fft, hop_length=hop_length, center=center
        )[0]

        intervals = librosa.effects.split(
            y,
            top_db=top_db,
            frame_length=n_fft,
            hop_length=hop_length,
        )
        voiced_duration = float(
            sum((int(end) - int(start)) / sr for start, end in intervals)
        )
        silence_duration = max(0.0, duration_sec - voiced_duration)
        voiced_ratio = voiced_duration / duration_sec if duration_sec > 0 else 0.0
        silence_ratio = silence_duration / duration_sec if duration_sec > 0 else 0.0
        num_voiced_segments = float(len(intervals))
        voiced_segments_per_sec = (
            num_voiced_segments / duration_sec if duration_sec > 0 else 0.0
        )

        mfcc = librosa.feature.mfcc(
            y=y,
            sr=sr,
            n_mfcc=20,
            n_fft=n_fft,
            hop_length=hop_length,
            center=center,
        )
        chroma = librosa.feature.chroma_stft(
            y=y,
            sr=sr,
            n_chroma=12,
            n_fft=n_fft,
            hop_length=hop_length,
            center=center,
        )

        features: dict[str, float] = {
            "duration_sec": duration_sec,
            "rms_mean": float(np.mean(rms)),
            "rms_std": float(np.std(rms)),
            "rms_min": float(np.min(rms)),
            "rms_max": float(np.max(rms)),
            "zcr_mean": float(np.mean(zcr)),
            "zcr_std": float(np.std(zcr)),
            "spectral_centroid_mean": float(np.mean(centroid)),
            "spectral_centroid_std": float(np.std(centroid)),
            "spectral_bandwidth_mean": float(np.mean(bandwidth)),
            "spectral_bandwidth_std": float(np.std(bandwidth)),
            "spectral_rolloff_mean": float(np.mean(rolloff)),
            "spectral_rolloff_std": float(np.std(rolloff)),
            "spectral_flatness_mean": float(np.mean(flatness)),
            "spectral_flatness_std": float(np.std(flatness)),
            "voiced_duration": voiced_duration,
            "silence_duration": silence_duration,
            "voiced_ratio": float(voiced_ratio),
            "silence_ratio": float(silence_ratio),
            "num_voiced_segments": num_voiced_segments,
            "voiced_segments_per_sec": float(voiced_segments_per_sec),
        }

        for index in range(20):
            features[f"mfcc_{index + 1}_mean"] = float(np.mean(mfcc[index]))
            features[f"mfcc_{index + 1}_std"] = float(np.std(mfcc[index]))

        for index in range(12):
            features[f"chroma_{index + 1}_mean"] = float(np.mean(chroma[index]))
            features[f"chroma_{index + 1}_std"] = float(np.std(chroma[index]))

        missing = [name for name in self.feature_cols if name not in features]
        if missing:
            raise ValueError(f"Missing acoustic features: {missing}")

        return features

    def predict(self, transcript: str, audio_bytes: bytes) -> dict[str, Any]:
        transcript = str(transcript).strip()
        if not transcript:
            raise ValueError("Transcript cannot be empty.")
        if not audio_bytes:
            raise ValueError("Audio is required for fusion analysis.")

        temporary_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
                audio_file.write(audio_bytes)
                temporary_path = audio_file.name

            features = self._extract_audio_features(temporary_path)
            audio_frame = pd.DataFrame(
                [{name: features[name] for name in self.feature_cols}],
                columns=self.feature_cols,
            )

            transcript_probability = self._positive_probability(
                self.transcript_model, [transcript]
            )
            audio_probability = self._positive_probability(
                self.audio_model, audio_frame
            )

            stack_input = pd.DataFrame(
                [[transcript_probability, audio_probability]],
                columns=["transcript_probability", "audio_probability"],
            )
            fusion_probability = self._positive_probability(self.stacker, stack_input)

            return {
                "score": fusion_probability,
                "threshold": self.threshold,
                "flagged": fusion_probability >= self.threshold,
                "transcript_probability": transcript_probability,
                "audio_probability": audio_probability,
                "model_type": "transcript_acoustic_fusion",
                "individual_scores": {
                    "transcript_model": transcript_probability,
                    "acoustic_model": audio_probability,
                },
            }
        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.remove(temporary_path)
