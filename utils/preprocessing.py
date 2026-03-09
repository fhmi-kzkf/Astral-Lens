"""
Astral-Lens — Preprocessing Utilities
Text cleaning and audio normalization helpers.
"""

import re
import numpy as np


# ── Text Preprocessing ────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """
    Clean and normalise raw input text for analysis.

    Steps:
      1. Remove URLs
      2. Remove email addresses
      3. Collapse excessive whitespace
      4. Strip leading/trailing whitespace
    """
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    # Remove email addresses
    text = re.sub(r"\S+@\S+\.\S+", "", text)
    # Collapse multiple spaces / newlines
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── Audio Preprocessing ──────────────────────────────────────────────────────

def normalize_audio(y: np.ndarray, sr: int, target_sr: int = 22050):
    """
    Peak-normalise an audio signal and optionally resample.

    Parameters
    ----------
    y : np.ndarray
        Audio time-series.
    sr : int
        Original sample rate.
    target_sr : int
        Target sample rate (default 22050 Hz).

    Returns
    -------
    y_norm : np.ndarray
        Normalised (and possibly resampled) audio.
    sr_out : int
        Output sample rate.
    """
    import librosa

    # Resample if needed
    if sr != target_sr:
        y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
        sr = target_sr

    # Peak normalisation
    peak = np.max(np.abs(y))
    if peak > 0:
        y = y / peak

    return y, sr
