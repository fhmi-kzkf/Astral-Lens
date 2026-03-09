"""
╔══════════════════════════════════════════════════════════════════╗
║  ASTRAL-LENS — Digital Forensic & AI Awareness Terminal         ║
║  Entry point: Streamlit application with Cyber-Noir theme       ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# ── Page Config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="ASTRAL-LENS · Forensic Terminal",
    page_icon="⟐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Module Imports ───────────────────────────────────────────────────────────
from modules.ui_styles import inject_css, render_header, render_sidebar, noir_card, risk_badge, score_gauge
from modules.text_engine import run_full_analysis
from modules.audio_engine import run_audio_forensics
from utils.preprocessing import clean_text

# ── Apply Theme ──────────────────────────────────────────────────────────────
inject_css()
render_header()
render_sidebar()

# ── Session State Initialisation ─────────────────────────────────────────────
if "text_results" not in st.session_state:
    st.session_state["text_results"] = None
if "audio_results" not in st.session_state:
    st.session_state["audio_results"] = None


# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_signal, tab_freq, tab_awareness = st.tabs([
    "⟐ SIGNAL SCAN",
    "⟐ FREQUENCY SCAN",
    "⟐ AWARENESS HUB",
])

# ── TAB 1: SIGNAL SCAN (Text Forensics) ─────────────────────────────────────

with tab_signal:
    st.markdown("### 📡 Signal Scan — Text Forensic Analysis")
    st.markdown(
        '<p style="color:#737373; font-size:0.8rem;">Paste text from social media, news, or messages for multi-layered forensic analysis.</p>',
        unsafe_allow_html=True,
    )

    input_text = st.text_area(
        "INPUT SIGNAL",
        height=180,
        placeholder="Paste suspicious text here for forensic analysis...",
        key="text_input",
    )

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        scan_clicked = st.button("▶ INITIATE SCAN", key="btn_text_scan", use_container_width=True)
    with col_info:
        if not GEMINI_API_KEY:
            st.markdown(
                '<p style="color:#ef4444; font-size:0.75rem; margin-top:12px;">⚠ Missing GOOGLE_API_KEY in .env</p>',
                unsafe_allow_html=True,
            )

    if scan_clicked and input_text.strip() and GEMINI_API_KEY:
        cleaned = clean_text(input_text)
        with st.spinner("⟐ Scanning digital signatures... Analysing signal integrity..."):
            results = run_full_analysis(cleaned, GEMINI_API_KEY)
            st.session_state["text_results"] = results

    # ── Render Results ────────────────────────────────────────────────────
    results = st.session_state.get("text_results")
    if results:
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        st.markdown("### ⟐ FORENSIC REPORT")

        reality = results["reality_index"]
        emotions = results["affective_signals"]
        scam = results["scam_detection"]

        # ── Row 1: Reality Index + Risk Badge ─────────────────────────────
        r1c1, r1c2, r1c3 = st.columns([1, 1, 1])

        with r1c1:
            score = reality.get("reality_score", 0)
            st.markdown(score_gauge(score, "Reality Index"), unsafe_allow_html=True)

        with r1c2:
            level = reality.get("risk_level", "Medium")
            st.markdown(
                f"""
                <div style="text-align:center; padding:20px;">
                    <p style="font-size:0.7rem; color:#737373; text-transform:uppercase;
                              letter-spacing:2px; margin-bottom:12px;">Risk Assessment</p>
                    {risk_badge(level)}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with r1c3:
            scam_score = scam.get("scam_score", 0)
            scam_color = "#ef4444" if scam_score >= 60 else "#f59e0b" if scam_score >= 30 else "#10b981"
            st.markdown(
                f"""
                <div class="score-display">
                    <div class="score-value" style="color:{scam_color}; font-size:2.5rem;">{scam_score}</div>
                    <div class="score-label">Scam Index</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Row 2: Emotion Radar Chart ────────────────────────────────────
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

        emo_col, detail_col = st.columns([1, 1])

        with emo_col:
            st.markdown("#### Affective Signal Map")
            emo = emotions.get("emotions", {})
            categories = ["Fear", "Anger", "Trust", "Neutral"]
            values = [emo.get("fear", 0), emo.get("anger", 0), emo.get("trust", 0), emo.get("neutral", 0)]
            values_closed = values + [values[0]]  # close the polygon

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values_closed,
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(59,130,246,0.15)",
                line=dict(color="#3b82f6", width=2),
                marker=dict(size=6, color="#3b82f6"),
                name="Emotions",
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="#0a0a0a",
                    radialaxis=dict(
                        visible=True, range=[0, 100],
                        gridcolor="#1a1a1a", tickfont=dict(color="#737373", family="Roboto Mono", size=10),
                    ),
                    angularaxis=dict(
                        gridcolor="#1a1a1a",
                        tickfont=dict(color="#c0c0c0", family="Roboto Mono", size=12),
                    ),
                ),
                paper_bgcolor="#050505",
                showlegend=False,
                height=350,
                margin=dict(l=60, r=60, t=30, b=30),
            )
            st.plotly_chart(fig_radar, use_container_width=True, key="radar_chart")

            if emotions.get("manipulation_warning"):
                st.markdown(
                    '<div class="warning-box">⚠ HIGH EMOTIONAL MANIPULATION DETECTED — '
                    'Content is designed to provoke knee-jerk reactions rather than rational thought.</div>',
                    unsafe_allow_html=True,
                )

        with detail_col:
            st.markdown("#### Emotion Breakdown")
            for cat, val in zip(categories, values):
                color_map = {"Fear": "#ef4444", "Anger": "#f59e0b", "Trust": "#10b981", "Neutral": "#3b82f6"}
                c = color_map.get(cat, "#3b82f6")
                st.markdown(
                    f'<p style="font-family:Roboto Mono,monospace; font-size:0.8rem; color:#c0c0c0; margin:4px 0;">'
                    f'<span style="color:{c};">▸ {cat.upper()}</span>: {val}%</p>',
                    unsafe_allow_html=True,
                )
                st.progress(val / 100)

            st.markdown("---")
            st.markdown("#### Dominant Pattern")
            dominant = emotions.get("dominant_emotion", "neutral")
            st.markdown(
                f'<p style="color:#3b82f6; font-size:0.85rem;">⟐ {dominant.upper()}</p>',
                unsafe_allow_html=True,
            )

        # ── Row 3: Scam Patterns + XAI Explanation ───────────────────────
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

        xai_col, scam_col = st.columns([1, 1])

        with xai_col:
            st.markdown("#### ⟐ XAI Explanation")
            explanation = reality.get("explanation", "No explanation available.")
            noir_card(
                "Signal Intelligence Report",
                f'<p style="color:#c0c0c0; font-size:0.8rem; line-height:1.7;">{explanation}</p>',
            )

        with scam_col:
            st.markdown("#### ⟐ Scam Pattern Matches")
            matched = scam.get("matched_patterns", [])
            if matched:
                for pattern in matched:
                    st.markdown(
                        f'<p style="color:#ef4444; font-size:0.8rem; font-family:Roboto Mono,monospace;">'
                        f'▸ {pattern}</p>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    '<p style="color:#10b981; font-size:0.8rem;">✓ No known scam patterns matched.</p>',
                    unsafe_allow_html=True,
                )

            semantic = scam.get("semantic_analysis", {})
            if isinstance(semantic, dict) and semantic.get("verdict"):
                verdict_color = {"CLEAN": "#10b981", "SUSPICIOUS": "#f59e0b", "SCAM": "#ef4444"}.get(
                    semantic["verdict"], "#737373"
                )
                st.markdown(
                    f'<p style="color:{verdict_color}; font-size:0.9rem; font-weight:600; margin-top:12px;">'
                    f'Semantic Verdict: {semantic["verdict"]}</p>',
                    unsafe_allow_html=True,
                )

        # ── Emotion Analysis Detail ──────────────────────────────────────
        with st.expander("📋 DETAILED AFFECTIVE ANALYSIS"):
            analysis_text = emotions.get("analysis", "No detailed analysis available.")
            st.markdown(
                f'<p style="color:#c0c0c0; font-size:0.8rem; line-height:1.7;">{analysis_text}</p>',
                unsafe_allow_html=True,
            )

        with st.expander("📋 SEMANTIC SCAM ANALYSIS"):
            if isinstance(semantic, dict):
                for key in ["hidden_intent", "urgency_tactics", "deceptive_patterns"]:
                    v = semantic.get(key, "N/A")
                    st.markdown(
                        f'<p style="font-size:0.8rem; color:#c0c0c0;">'
                        f'<span style="color:#3b82f6; text-transform:uppercase;">{key.replace("_", " ")}</span>: {v}</p>',
                        unsafe_allow_html=True,
                    )

        # ── Export Report ────────────────────────────────────────────────
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        report_json = json.dumps(results, indent=4)
        st.download_button(
            label="⬇ EXPORT FORENSIC REPORT (JSON)",
            data=report_json,
            file_name="astral_lens_text_report.json",
            mime="application/json",
            use_container_width=True,
        )


# ── TAB 2: FREQUENCY SCAN (Audio Forensics) ─────────────────────────────────

with tab_freq:
    st.markdown("### 🔊 Frequency Scan — Audio Forensic Analysis")
    st.markdown(
        '<p style="color:#737373; font-size:0.8rem;">'
        'Upload a .wav or .mp3 file for heuristic forensic analysis of voice authenticity.</p>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "UPLOAD AUDIO SIGNAL",
        type=["wav", "mp3"],
        key="audio_upload",
    )

    if uploaded_file is not None:
        audio_col, info_col = st.columns([2, 1])
        with audio_col:
            st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")
        with info_col:
            st.markdown(
                f'<p style="font-size:0.75rem; color:#737373;">'
                f'File: <span style="color:#3b82f6;">{uploaded_file.name}</span><br>'
                f'Size: {uploaded_file.size / 1024:.1f} KB</p>',
                unsafe_allow_html=True,
            )

        if st.button("▶ INITIATE FREQUENCY SCAN", key="btn_audio_scan", use_container_width=True):
            with st.spinner("⟐ Analyzing frequency anomalies... Detecting synthetic artifacts..."):
                audio_bytes = uploaded_file.getvalue()
                audio_results = run_audio_forensics(audio_bytes, uploaded_file.name)
                st.session_state["audio_results"] = audio_results

    # ── Render Audio Results ─────────────────────────────────────────────
    audio_res = st.session_state.get("audio_results")
    if audio_res:
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        st.markdown("### ⟐ AUDIO FORENSIC REPORT")

        # File info
        finfo = audio_res.get("file_info", {})
        fi_cols = st.columns(4)
        fi_cols[0].metric("Sample Rate", f'{finfo.get("sample_rate", 0):,} Hz')
        fi_cols[1].metric("Duration", f'{finfo.get("duration_seconds", 0):.1f}s')
        fi_cols[2].metric("Samples", f'{finfo.get("samples", 0):,}')
        fi_cols[3].metric("Authenticity", f'{audio_res.get("authenticity_score", 0)}/100')

        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

        # Authenticity Score + Verdict
        auth_score = audio_res.get("authenticity_score", 0)
        auth_color = "#10b981" if auth_score >= 75 else "#f59e0b" if auth_score >= 45 else "#ef4444"
        st.markdown(
            f"""
            <div style="text-align:center; padding:16px;">
                <div style="font-family:'Share Tech Mono',monospace; font-size:3rem;
                            color:{auth_color}; text-shadow:0 0 30px {auth_color};">{auth_score}</div>
                <div style="font-size:0.7rem; color:#737373; text-transform:uppercase;
                            letter-spacing:3px; margin-top:4px;">Authenticity Score</div>
                <p style="color:{auth_color}; font-size:0.85rem; margin-top:12px;">
                    {audio_res.get("verdict", "")}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

        # Metric Cards
        m1, m2, m3 = st.columns(3)

        pitch = audio_res.get("pitch", {})
        spectral = audio_res.get("spectral", {})
        rms = audio_res.get("rms", {})

        with m1:
            p_color = "#10b981" if pitch.get("stability_score", 0) >= 70 else "#f59e0b" if pitch.get("stability_score", 0) >= 45 else "#ef4444"
            noir_card(
                "F₀ Pitch Stability",
                f'<p style="font-size:2rem; color:{p_color}; font-family:Share Tech Mono,monospace; text-shadow:0 0 15px {p_color};">'
                f'{pitch.get("stability_score", 0)}</p>'
                f'<p style="font-size:0.7rem; color:#c0c0c0; margin-top:8px;">{pitch.get("verdict", "")}</p>'
                f'<p style="font-size:0.65rem; color:#737373; margin-top:4px;">{pitch.get("detail", "")}</p>',
            )

        with m2:
            s_color = "#10b981" if spectral.get("flatness_score", 0) >= 70 else "#f59e0b" if spectral.get("flatness_score", 0) >= 45 else "#ef4444"
            noir_card(
                "Spectral Flatness",
                f'<p style="font-size:2rem; color:{s_color}; font-family:Share Tech Mono,monospace; text-shadow:0 0 15px {s_color};">'
                f'{spectral.get("flatness_score", 0)}</p>'
                f'<p style="font-size:0.7rem; color:#c0c0c0; margin-top:8px;">{spectral.get("verdict", "")}</p>'
                f'<p style="font-size:0.65rem; color:#737373; margin-top:4px;">{spectral.get("detail", "")}</p>',
            )

        with m3:
            r_color = "#10b981" if rms.get("rms_score", 0) >= 70 else "#f59e0b" if rms.get("rms_score", 0) >= 45 else "#ef4444"
            noir_card(
                "RMS Energy Dynamics",
                f'<p style="font-size:2rem; color:{r_color}; font-family:Share Tech Mono,monospace; text-shadow:0 0 15px {r_color};">'
                f'{rms.get("rms_score", 0)}</p>'
                f'<p style="font-size:0.7rem; color:#c0c0c0; margin-top:8px;">{rms.get("verdict", "")}</p>'
                f'<p style="font-size:0.65rem; color:#737373; margin-top:4px;">{rms.get("detail", "")}</p>',
            )

        # Spectrogram
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### Mel-Spectrogram")
        spec_fig = audio_res.get("spectrogram_fig")
        if spec_fig:
            st.plotly_chart(spec_fig, use_container_width=True, key="mel_spectrogram")

        # Detailed Expandable
        with st.expander("📋 DETAILED FORENSIC DATA"):
            for label, data in [("Pitch Analysis", pitch), ("Spectral Analysis", spectral), ("RMS Analysis", rms)]:
                st.markdown(f"**{label}**")
                display_data = {k: v for k, v in data.items() if k != "detail"}
                st.json(display_data)

        # ── Export Report ────────────────────────────────────────────────
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        # Remove the plotly figure object before serializing
        export_data = {k: v for k, v in audio_res.items() if k != "spectrogram_fig"}
        audio_report_json = json.dumps(export_data, indent=4)
        st.download_button(
            label="⬇ EXPORT FORENSIC REPORT (JSON)",
            data=audio_report_json,
            file_name="astral_lens_audio_report.json",
            mime="application/json",
            use_container_width=True,
        )


# ── TAB 3: AWARENESS HUB ────────────────────────────────────────────────────

with tab_awareness:
    st.markdown("### 🎓 Awareness Hub — Digital Literacy & Education")
    st.markdown(
        '<p style="color:#737373; font-size:0.8rem;">'
        "Understanding how forensic AI analysis works empowers you to critically evaluate digital content.</p>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    # ── Section: How the AI Reaches Conclusions ──────────────────────────
    st.markdown("#### ⟐ How Astral-Lens Reaches Its Conclusions")

    with st.expander("📡 REALITY INDEX — Credibility Scoring", expanded=True):
        st.markdown(
            """
            <div class="info-box">
            <strong>What it measures:</strong> The factual consistency and credibility of text content.<br><br>
            <strong>How it works:</strong><br>
            ▸ The AI examines the text for <strong>logical fallacies</strong> (circular reasoning, false equivalence)<br>
            ▸ Checks for <strong>source quality</strong> — does the text reference reputable sources?<br>
            ▸ Identifies <strong>unverifiable claims</strong> presented as fact<br>
            ▸ Detects <strong>factual inconsistencies</strong> within the text itself<br><br>
            <strong>Score Range:</strong><br>
            ▸ <span style="color:#10b981;">80-100</span>: Well-sourced, factually consistent content<br>
            ▸ <span style="color:#f59e0b;">50-79</span>: Some unverifiable claims or minor inconsistencies<br>
            ▸ <span style="color:#ef4444;">20-49</span>: Multiple red flags detected<br>
            ▸ <span style="color:#ef4444;">0-19</span>: Clear disinformation indicators
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("🎭 AFFECTIVE SIGNALS — Emotion Detection"):
        st.markdown(
            """
            <div class="info-box">
            <strong>What it measures:</strong> Emotional manipulation patterns in text.<br><br>
            <strong>How it works:</strong><br>
            ▸ Analyses the text for <strong>four primary emotional signals</strong>: Fear, Anger, Trust, and Neutral<br>
            ▸ Calculates the percentage distribution of these emotions<br>
            ▸ If <strong>Fear or Anger exceeds 65%</strong>, a manipulation warning is triggered<br><br>
            <strong>Why it matters:</strong><br>
            Disinformation campaigns often exploit <strong>Fear</strong> and <strong>Anger</strong> to bypass
            rational thinking and provoke impulsive actions. Content with artificially elevated fear/anger
            signals is designed to manipulate, not inform.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("🛡 SCAM DETECTION — Pattern Recognition"):
        st.markdown(
            """
            <div class="info-box">
            <strong>What it measures:</strong> Known and hidden scam patterns in text.<br><br>
            <strong>Dual-layer approach:</strong><br>
            ▸ <strong>Layer 1 — Rule-Based Regex:</strong> Matches against a database of known scam phrases
            (e.g., "investasi cepat", "guaranteed profit", "act now")<br>
            ▸ <strong>Layer 2 — Semantic AI Analysis:</strong> Gemini analyses the deeper intent of the text,
            catching sophisticated scams that don't use obvious keywords<br><br>
            <strong>Cross-referencing:</strong><br>
            High scam scores <strong>automatically reduce the Reality Index</strong> to reflect the combined risk.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    with st.expander("🔊 AUDIO FORENSICS — Signal Authenticity"):
        st.markdown(
            """
            <div class="info-box">
            <strong>What it measures:</strong> Whether an audio file shows signs of AI generation or manipulation.<br><br>
            <strong>Three Heuristic Indicators:</strong><br><br>
            <strong>1. F₀ Pitch Stability</strong><br>
            ▸ Extracts the fundamental frequency (F₀) of the voice<br>
            ▸ Calculates the coefficient of variation (CV)<br>
            ▸ <strong>Unnaturally low CV</strong> → voice is "too stable" → common in AI-generated speech<br>
            ▸ Natural human speech has micro-variations in pitch<br><br>
            <strong>2. Spectral Flatness</strong><br>
            ▸ Measures how "noise-like" vs "tonal" the audio spectrum is<br>
            ▸ <strong>High spectral flatness</strong> → digital aliasing or synthetic artifacts<br>
            ▸ Natural speech has rich harmonic content with low flatness<br><br>
            <strong>3. RMS Energy Dynamics</strong><br>
            ▸ Analyses the volume/energy distribution over time<br>
            ▸ Looks for <strong>natural pauses and breathing patterns</strong><br>
            ▸ AI-generated speech tends to have <strong>unnaturally uniform energy</strong><br>
            ▸ Low silence ratio + low dynamic range → synthetic indicator
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("📊 MEL-SPECTROGRAM — Visual Frequency Analysis"):
        st.markdown(
            """
            <div class="info-box">
            <strong>What it shows:</strong> A visual representation of audio frequencies over time.<br><br>
            <strong>How to read it:</strong><br>
            ▸ <strong>X-axis:</strong> Time (seconds)<br>
            ▸ <strong>Y-axis:</strong> Frequency (Hz, Mel-scaled for perceptual relevance)<br>
            ▸ <strong>Color intensity:</strong> Energy level (brighter = louder at that frequency)<br><br>
            <strong>What to look for:</strong><br>
            ▸ <span style="color:#10b981;">Natural speech</span>: Clear harmonic bands with organic variation<br>
            ▸ <span style="color:#ef4444;">Synthetic speech</span>: Overly smooth patterns, sharp cutoffs,
            or unnaturally uniform energy distribution
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div style="text-align:center; padding:20px 0; color:#737373; font-size:0.7rem;">
            <p>⟐ ASTRAL-LENS v1.0 · Built for Digital Literacy & AI Awareness ⟐</p>
            <p style="margin-top:4px;">This tool is educational — always verify findings with multiple sources.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
