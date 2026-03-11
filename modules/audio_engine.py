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
    Detect unnatural pitch stability AND micro-smoothness (Jitter).
    
    Advanced TTS can fake macro variance (high expressiveness CV),
    but struggles to synthesize biological micro-tremors (Jitter).
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
            "jitter": 0.0,
            "cv": 0.0,
            "stability_score": 50,
            "verdict": "Insufficient voiced data",
            "detail": "Not enough voiced frames to analyze pitch.",
        }

    f0_mean = float(np.mean(f0_voiced))
    f0_std = float(np.std(f0_voiced))
    f0_var = float(np.var(f0_voiced))

    # 1. Macro Variance (Expressiveness)
    cv = f0_std / f0_mean if f0_mean > 0 else 0

    # 2. Micro Jitter (Absolute frame-to-frame difference, normalized)
    f0_diff = np.abs(np.diff(f0_voiced))
    jitter = float(np.mean(f0_diff) / f0_mean) if f0_mean > 0 else 0

    # Score: Low CV (Robotic) OR Low Jitter (ElevenLabs smooth) → Suspicious
    if cv < 0.03 or jitter < 0.005:
        stability_score = 15
        verdict = "⚠ SYNTHETIC — Unnatural pitch smoothness (Missing biological micro-tremors)"
    elif cv < 0.08 or jitter < 0.01:
        stability_score = 40
        verdict = "⚡ CAUTION — Pitch lacks organic instability"
    elif jitter > 0.045:
        # ElevenLabs & HiFi-GAN phase tracking glitches cause unnaturally high jitter
        stability_score = 25
        verdict = "⚠ VOCODER GLITCH — Severe AI phase artifacts (Unnatural high jitter)"
    else:
        stability_score = 90
        verdict = "✓ ORGANIC — Natural pitch variance and micro-tremors"

    # Format detail string appropriately
    if jitter > 0.045:
        detail_txt = "Abnormally high micro-jitter points to AI vocoder phase issues."
    elif jitter < 0.01:
        detail_txt = "Micro-smoothness suggests AI synthesis."
    else:
        detail_txt = "Pitch contours show natural biological micro-tremors."

    return {
        "f0_mean": round(f0_mean, 2),
        "f0_std": round(f0_std, 2),
        "f0_variance": round(f0_var, 2),
        "cv": round(cv, 4),
        "jitter": round(jitter, 6),
        "stability_score": stability_score,
        "verdict": verdict,
        "detail": f"Mean F0: {f0_mean:.1f} Hz | CV: {cv:.4f} | Jitter: {jitter:.5f} — {detail_txt}",
    }


# ── Spectral Flatness ────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def analyze_spectral_flatness(y: np.ndarray, sr: int) -> dict:
    """
    Analyze Spectral Flatness & High-Frequency Cutoffs.
    
    Advanced AI vocoders (like HiFi-GAN) often truncate high frequencies
    (>8kHz) to optimize inference speed, causing an unnatural HF cliff.
    """
    # 1. Spectral Flatness
    sf = librosa.feature.spectral_flatness(y=y)[0]
    sf_mean = float(np.mean(sf))
    
    # 2. High-Frequency Rolloff / Cutoff Analysis
    S = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)
    
    # Find ratio of energy above 8kHz vs total
    hf_mask = freqs > 8000
    if not np.any(hf_mask):
        hf_ratio = 0.0  # Sample rate is too low (< 16kHz) to contain 8kHz+
    else:
        total_energy = np.sum(S)
        hf_energy = np.sum(S[hf_mask, :])
        hf_ratio = float(hf_energy / total_energy) if total_energy > 0 else 0.0

    # Score Logic
    if sf_mean > 0.4:
        # Typical old-school noise-like robot voice
        flatness_score = 25
        verdict = "⚠ HIGH FLATNESS — Heavily synthetic or noisy"
    elif sr >= 22050 and hf_ratio < 0.005: 
        # Missing highs despite high sample rate (Vocoder Wall / Cutoff artifact)
        flatness_score = 30
        verdict = "⚠ HF CUTOFF — Unnatural frequency wall detected (Vocoder Artifact)"
    elif sf_mean > 0.2:
        flatness_score = 55
        verdict = "⚡ MODERATE — Some digital bandlimiting detected"
    else:
        flatness_score = 90
        verdict = "✓ ORGANIC — Rich harmonic content & natural rolloff"

    return {
        "mean_flatness": round(sf_mean, 4),
        "hf_energy_ratio": round(hf_ratio, 5),
        "flatness_score": flatness_score,
        "verdict": verdict,
        "detail": (
            f"Flatness: {sf_mean:.4f} | HF>8kHz: {hf_ratio:.2%} — "
            f"{'Sharp HF cutoff indicates neural vocoding.' if (sr >= 22050 and hf_ratio < 0.005) else 'Harmonics consistent with analog mic.'}"
        ),
    }


# ── RMS Energy Dynamics ─────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def analyze_rms_dynamics(y: np.ndarray, sr: int) -> dict:
    """
    Analyze RMS energy for natural breathing patterns, organic pauses,
    and absolute Digital Silence.
    
    True analog recordings always have an analog noise floor > 0.
    100% digital zero RMS strongly flags synthetic audio.
    """
    rms = librosa.feature.rms(y=y)[0]
    rms_mean = float(np.mean(rms))
    rms_max = float(np.max(rms))
    rms_min = float(np.min(rms))

    # 1. Dynamic range ratio
    dynamic_range = rms_max / rms_mean if rms_mean > 0 else 0

    # 2. Digital Silence (Absolute Zero) Check
    # If the minimum RMS is mathematically identically zero (or near 1e-6)
    digital_silence_present = bool(rms_min < 1e-5)

    # 3. Macro Silence Ratio (Breaths)
    silence_threshold = rms_mean * 0.1
    silent_frames = int(np.sum(rms < silence_threshold))
    total_frames = len(rms)
    silence_ratio = silent_frames / total_frames if total_frames > 0 else 0

    # Score heuristic
    # If Digital Silence exists BUT it's highly dynamic (>4.5x), it's likely a hardware noise gate.
    # Only penalize Digital Silence if it accompanies hyper-compression.
    if digital_silence_present and dynamic_range < 4.5:
        rms_score = 10
        verdict = "⚠ SYNTHETIC COMPRESSION — Math zero gaps + Broadcast normalization"
    elif dynamic_range < 4.5:
        rms_score = 30
        verdict = "⚠ HYPER-COMPRESSED — Unnatural dynamics (AI Broadcast normalization flag)"
    elif dynamic_range < 6.0 and silence_ratio < 0.05:
        rms_score = 40
        verdict = "⚡ FLAT ENERGY — Minimal breathing patterns / Heavily compressed"
    elif silence_ratio > 0.30:
        rms_score = 65
        verdict = "⚡ HIGH SILENCE — Spliced or unusually sparse speech"
    else:
        # If it reaches here, it has healthy dynamic range (>4.5) and normal breathing
        rms_score = 90
        verdict = "✓ ORGANIC — Natural breathing and dynamic range present"

    # Format detail string appropriately
    if digital_silence_present and dynamic_range < 4.5:
        detail_txt = "Mathematical zero gap accompanied by hyper-compression proves AI generation."
    elif digital_silence_present:
        detail_txt = "Analog amplitude dynamics detected (mathematical zeros ignored due to presumed noise-gate)."
    elif dynamic_range < 4.5:
        detail_txt = "Broadcast-style hyper-compression typical of Gen-AI."
    else:
        detail_txt = "Healthy amplitude dynamics confirm human mic origin."

    return {
        "rms_mean": round(rms_mean, 6),
        "min_amplitude": round(rms_min, 6),
        "dynamic_range": round(dynamic_range, 2),
        "silence_ratio": round(silence_ratio, 4),
        "digital_silence": digital_silence_present,
        "rms_score": rms_score,
        "verdict": verdict,
        "detail": f"Dyn Range: {dynamic_range:.1f}x | Sil Ratio: {silence_ratio:.1%} | {detail_txt}",
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
    spectral = analyze_spectral_flatness(y, sr)
    rms = analyze_rms_dynamics(y, sr)
    spec_fig = generate_mel_spectrogram(y, sr)

    # Composite authenticity score (weighted average)
    authenticity = int(
        pitch["stability_score"] * 0.40
        + spectral["flatness_score"] * 0.35
        + rms["rms_score"] * 0.25
    )

    # Hard Logic Capping: If any core metric strongly detects synthetic traits, cap the entire score
    # This prevents highly expressive AI (like ElevenLabs) from using 1 strong metric to float the average
    if pitch["stability_score"] <= 40 or spectral["flatness_score"] <= 40 or rms["rms_score"] <= 40:
        authenticity = min(authenticity, 44)

    if authenticity >= 75:
        overall_verdict = "✓ LIKELY AUTHENTIC — Forensic indicators within organic range"
    elif authenticity >= 45:
        overall_verdict = "⚡ INCONCLUSIVE — Advanced Gen-AI suspects detected"
    else:
        overall_verdict = "⚠ SYNTHETIC — Mathematical vocoder signatures flagged"

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
