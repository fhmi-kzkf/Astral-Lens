"""
Astral-Lens — Audio Forensic Engine
Librosa-based heuristic forensic indicators:
  • Pitch Stability (F0 Variance)
  • Spectral Flatness (synthetic artifact detection)
  • RMS Energy Dynamics (breathing / pause analysis)
  • Mel-Spectrogram visualisation
"""

import io
import tempfile

import librosa
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from utils.preprocessing import normalize_audio


# ── Pitch Stability (F0 Variance) ────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def analyze_pitch_stability(y: np.ndarray, sr: int) -> dict:
    """
    Detect unnatural pitch stability — a hallmark of synthetic speech.

    Low F0 variance ⇒ suspiciously stable ⇒ possibly AI-generated.
    """
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr
    )

    # Keep only voiced segments
    f0_voiced = f0[~np.isnan(f0)]

    if len(f0_voiced) < 10:
        return {
            "f0_mean": 0.0,
            "f0_std": 0.0,
            "f0_variance": 0.0,
            "stability_score": 50,
            "verdict": "Insufficient voiced data",
            "detail": "Not enough voiced frames to analyze pitch.",
        }

    f0_mean = float(np.mean(f0_voiced))
    f0_std = float(np.std(f0_voiced))
    f0_var = float(np.var(f0_voiced))

    # Coefficient of variation (normalised measure)
    cv = f0_std / f0_mean if f0_mean > 0 else 0

    # Score: low CV → suspicious stability → lower score
    if cv < 0.03:
        stability_score = 20
        verdict = "⚠ ANOMALOUS — Pitch is unnaturally stable (AI indicator)"
    elif cv < 0.08:
        stability_score = 45
        verdict = "⚡ CAUTION — Pitch stability is below natural range"
    elif cv < 0.20:
        stability_score = 80
        verdict = "✓ NORMAL — Pitch variation within human range"
    else:
        stability_score = 90
        verdict = "✓ ORGANIC — High natural pitch variation detected"

    return {
        "f0_mean": round(f0_mean, 2),
        "f0_std": round(f0_std, 2),
        "f0_variance": round(f0_var, 2),
        "coefficient_of_variation": round(cv, 4),
        "stability_score": stability_score,
        "verdict": verdict,
        "detail": (
            f"Mean F0: {f0_mean:.1f} Hz | Std: {f0_std:.1f} Hz | "
            f"CV: {cv:.4f}  — {'Low CV suggests synthetic origin.' if cv < 0.08 else 'CV within organic speech range.'}"
        ),
    }


# ── Spectral Flatness ────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def analyze_spectral_flatness(y: np.ndarray) -> dict:
    """
    Spectral flatness measures how noise-like a signal is.

    High flatness → white-noise-like → possible digital aliasing / synthesis.
    """
    sf = librosa.feature.spectral_flatness(y=y)[0]
    sf_mean = float(np.mean(sf))
    sf_std = float(np.std(sf))
    sf_max = float(np.max(sf))

    # Score: higher flatness → more suspicious
    if sf_mean > 0.4:
        flatness_score = 25
        verdict = "⚠ HIGH FLATNESS — Possible synthetic or heavily processed audio"
    elif sf_mean > 0.2:
        flatness_score = 50
        verdict = "⚡ MODERATE — Some digital processing artifacts detected"
    elif sf_mean > 0.08:
        flatness_score = 75
        verdict = "✓ NORMAL — Spectral profile consistent with natural speech"
    else:
        flatness_score = 90
        verdict = "✓ ORGANIC — Rich harmonic content (typical human voice)"

    return {
        "mean_flatness": round(sf_mean, 4),
        "std_flatness": round(sf_std, 4),
        "max_flatness": round(sf_max, 4),
        "flatness_score": flatness_score,
        "verdict": verdict,
        "detail": (
            f"Mean spectral flatness: {sf_mean:.4f} | "
            f"{'High flatness indicates noise-like spectrum.' if sf_mean > 0.2 else 'Harmonic-rich spectrum is typical of natural speech.'}"
        ),
    }


# ── RMS Energy Dynamics ─────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def analyze_rms_dynamics(y: np.ndarray, sr: int) -> dict:
    """
    Analyze RMS energy for natural breathing patterns and organic pauses.

    Natural speech has dynamic range with quiet gaps; synthetic speech
    tends to have more uniform energy distribution.
    """
    rms = librosa.feature.rms(y=y)[0]
    rms_mean = float(np.mean(rms))
    rms_std = float(np.std(rms))
    rms_max = float(np.max(rms))
    rms_min = float(np.min(rms))

    # Dynamic range ratio
    dynamic_range = rms_max / rms_mean if rms_mean > 0 else 0

    # Count "silent" frames (< 10% of mean energy) → proxy for pauses / breathing
    silence_threshold = rms_mean * 0.1
    silent_frames = int(np.sum(rms < silence_threshold))
    total_frames = len(rms)
    silence_ratio = silent_frames / total_frames if total_frames > 0 else 0

    # Score heuristic
    if dynamic_range < 1.5 and silence_ratio < 0.05:
        rms_score = 25
        verdict = "⚠ FLAT ENERGY — No natural pauses detected (AI indicator)"
    elif dynamic_range < 2.5:
        rms_score = 50
        verdict = "⚡ LOW DYNAMICS — Minimal breathing patterns found"
    elif silence_ratio > 0.15:
        rms_score = 85
        verdict = "✓ ORGANIC — Natural breathing and pauses present"
    else:
        rms_score = 70
        verdict = "✓ NORMAL — Reasonable energy dynamics"

    return {
        "rms_mean": round(rms_mean, 6),
        "rms_std": round(rms_std, 6),
        "dynamic_range": round(dynamic_range, 2),
        "silence_ratio": round(silence_ratio, 4),
        "rms_score": rms_score,
        "verdict": verdict,
        "detail": (
            f"Dynamic range: {dynamic_range:.2f}x | Silence ratio: {silence_ratio:.1%} | "
            f"{'Lack of pauses is atypical for human speech.' if silence_ratio < 0.05 else 'Pause patterns are consistent with natural speech.'}"
        ),
    }


# ── Mel-Spectrogram ─────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def generate_mel_spectrogram(y: np.ndarray, sr: int):
    """
    Generate an interactive Plotly Mel-Spectrogram with the Magma colormap.
    """
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    S_dB = librosa.power_to_db(S, ref=np.max)

    # Time and frequency axes
    times = librosa.times_like(S_dB, sr=sr)
    freqs = librosa.mel_frequencies(n_mels=128, fmax=8000)

    fig = go.Figure(
        data=go.Heatmap(
            z=S_dB,
            x=times,
            y=freqs,
            colorscale="Magma",
            colorbar=dict(
                title=dict(text="dB", font=dict(color="#c0c0c0", family="Roboto Mono")),
                tickfont=dict(color="#c0c0c0", family="Roboto Mono"),
            ),
            zmin=-80,
            zmax=0,
        )
    )

    fig.update_layout(
        title=dict(
            text="MEL-SPECTROGRAM ANALYSIS",
            font=dict(
                family="Share Tech Mono, Roboto Mono, monospace",
                size=16,
                color="#3b82f6",
            ),
        ),
        xaxis=dict(
            title=dict(text="Time (s)", font=dict(family="Roboto Mono")),
            color="#737373",
            gridcolor="#1a1a1a",
            tickfont=dict(family="Roboto Mono"),
        ),
        yaxis=dict(
            title=dict(text="Frequency (Hz)", font=dict(family="Roboto Mono")),
            color="#737373",
            gridcolor="#1a1a1a",
            tickfont=dict(family="Roboto Mono"),
        ),
        paper_bgcolor="#050505",
        plot_bgcolor="#050505",
        height=400,
        margin=dict(l=60, r=20, t=50, b=50),
    )

    return fig


# ── Composite Forensic Analysis ─────────────────────────────────────────────

def run_audio_forensics(audio_bytes: bytes, file_name: str) -> dict:
    """
    Full forensic pipeline for an uploaded audio file.

    Parameters
    ----------
    audio_bytes : bytes
        Raw audio file bytes.
    file_name : str
        Original filename (used to infer format).

    Returns
    -------
    dict with keys: pitch, spectral, rms, spectrogram_fig,
                    authenticity_score, verdict
    """
    # Write to a temporary file so librosa can read it
    suffix = ".wav" if file_name.lower().endswith(".wav") else ".mp3"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    # Load and normalise
    y, sr = librosa.load(tmp_path, sr=None, mono=True)
    y, sr = normalize_audio(y, sr)

    # Run analyses
    pitch = analyze_pitch_stability(y, sr)
    spectral = analyze_spectral_flatness(y)
    rms = analyze_rms_dynamics(y, sr)
    spec_fig = generate_mel_spectrogram(y, sr)

    # Composite authenticity score (weighted average)
    authenticity = int(
        pitch["stability_score"] * 0.40
        + spectral["flatness_score"] * 0.30
        + rms["rms_score"] * 0.30
    )

    if authenticity >= 75:
        overall_verdict = "✓ LIKELY AUTHENTIC — Forensic indicators within organic range"
    elif authenticity >= 45:
        overall_verdict = "⚡ INCONCLUSIVE — Some anomalies detected; manual review recommended"
    else:
        overall_verdict = "⚠ SUSPICIOUS — Multiple synthetic indicators flagged"

    return {
        "pitch": pitch,
        "spectral": spectral,
        "rms": rms,
        "spectrogram_fig": spec_fig,
        "authenticity_score": authenticity,
        "verdict": overall_verdict,
        "file_info": {
            "name": file_name,
            "sample_rate": sr,
            "duration_seconds": round(len(y) / sr, 2),
            "samples": len(y),
        },
    }
