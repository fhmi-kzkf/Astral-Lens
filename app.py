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
import hashlib
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
from modules.ui_styles import inject_css, render_header, noir_card, risk_badge, score_gauge
from modules.text_engine import run_full_analysis
from modules.audio_engine import run_audio_forensics
from modules.image_engine import run_image_forensics
from modules.network_engine import run_network_forensics
from modules.db_engine import init_db, log_case, get_stats, get_recent_cases
from utils.preprocessing import clean_text
from utils.document_parser import parse_uploaded_document

# ── Initialise Database ──────────────────────────────────────────────────────
init_db()

# ── Apply Theme ──────────────────────────────────────────────────────────────
inject_css()
render_header()

# ── Security Dashboard in Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding:16px 0;">
            <p style="font-family:'Share Tech Mono',monospace;
                      font-size:1.1rem; color:#3b82f6;
                      text-shadow:0 0 15px rgba(59,130,246,0.4);
                      letter-spacing:3px; margin:0;">
                ⟐ ASTRAL-LENS
            </p>
            <p style="font-size:0.6rem; color:#737373;
                      letter-spacing:2px; text-transform:uppercase;">
                v2.0 · forensic engine
            </p>
        </div>
        <div class="neon-divider"></div>
        """,
        unsafe_allow_html=True,
    )

    # Live Security Dashboard
    stats = get_stats()
    st.markdown(
        '<p style="font-family:Roboto Mono,monospace; font-size:0.7rem; '
        'color:#3b82f6; text-transform:uppercase; letter-spacing:2px; margin-bottom:12px;">'
        '⟐ Security Dashboard</p>',
        unsafe_allow_html=True,
    )

    d1, d2 = st.columns(2)
    d1.metric("Signals Scanned", stats["total_scans"])
    d2.metric("Anomalies", stats["anomalies_detected"])

    d3, d4 = st.columns(2)
    d3.metric("Avg. Score", stats["avg_score"])
    d4.metric("Images", stats["image_scans"])

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div style="padding:8px 0; font-size:0.7rem; color:#737373;
                    font-family:'Roboto Mono',monospace;">
            <p>▸ <span style="color:#3b82f6;">SIGNAL SCAN</span> — Text Forensics</p>
            <p>▸ <span style="color:#3b82f6;">FREQ SCAN</span> — Audio Forensics</p>
            <p>▸ <span style="color:#22d3ee;">VISUAL SCAN</span> — Image Forensics</p>
            <p>▸ <span style="color:#ef4444;">NETWORK SCAN</span> — IP Forensics</p>
            <p>▸ <span style="color:#a855f7;">CASE ARCHIVES</span> — History</p>
            <p>▸ <span style="color:#3b82f6;">AWARENESS</span> — Education Hub</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Session State Initialisation ─────────────────────────────────────────────
if "text_results" not in st.session_state:
    st.session_state["text_results"] = None
if "audio_results" not in st.session_state:
    st.session_state["audio_results"] = None
if "image_results" not in st.session_state:
    st.session_state["image_results"] = None
if "network_results" not in st.session_state:
    st.session_state["network_results"] = None


# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_signal, tab_freq, tab_visual, tab_network, tab_archives, tab_awareness = st.tabs([
    "⟐ SIGNAL SCAN",
    "⟐ FREQUENCY SCAN",
    "⟐ VISUAL SCAN",
    "⟐ NETWORK SCAN",
    "⟐ CASE ARCHIVES",
    "⟐ AWARENESS HUB",
])

# ── TAB 1: SIGNAL SCAN (Text Forensics) ─────────────────────────────────────

with tab_signal:
    st.markdown("### 📡 Signal Scan — Text Forensic Analysis")
    st.markdown(
        '<p style="color:#737373; font-size:0.8rem;">Paste text or upload a document (.pdf, .txt) for multi-layered forensic analysis.</p>',
        unsafe_allow_html=True,
    )

    # ── Input Mode Toggle ────────────────────────────────────────────────
    input_mode = st.radio(
        "Input Method",
        ["✏️ Paste Text", "📄 Upload Document"],
        horizontal=True,
        key="text_input_mode",
    )

    raw_input_text = ""

    if input_mode == "✏️ Paste Text":
        raw_input_text = st.text_area(
            "INPUT SIGNAL",
            height=180,
            placeholder="Paste suspicious text here for forensic analysis...",
            key="text_input",
        )
    else:
        doc_file = st.file_uploader(
            "UPLOAD DOCUMENT",
            type=["pdf", "txt"],
            key="doc_upload",
        )
        if doc_file is not None:
            with st.spinner("⟐ Extracting text from document..."):
                raw_input_text = parse_uploaded_document(doc_file.getvalue(), doc_file.name)

            if raw_input_text.startswith("[ERROR]"):
                st.markdown(
                    f'<div class="warning-box">{raw_input_text}</div>',
                    unsafe_allow_html=True,
                )
                raw_input_text = ""
            else:
                with st.expander("📋 EXTRACTED TEXT PREVIEW", expanded=False):
                    st.text(raw_input_text[:2000] + ("..." if len(raw_input_text) > 2000 else ""))

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        scan_clicked = st.button("▶ INITIATE SCAN", key="btn_text_scan", use_container_width=True)
    with col_info:
        if not GEMINI_API_KEY:
            st.markdown(
                '<p style="color:#ef4444; font-size:0.75rem; margin-top:12px;">⚠ Missing GOOGLE_API_KEY in .env</p>',
                unsafe_allow_html=True,
            )

    if scan_clicked and raw_input_text.strip() and GEMINI_API_KEY:
        cleaned = clean_text(raw_input_text)
        with st.spinner("⟐ Scanning digital signatures... Analysing signal integrity..."):
            results = run_full_analysis(cleaned, GEMINI_API_KEY, raw_text=raw_input_text)
            st.session_state["text_results"] = results

            # Log to database
            reality = results.get("reality_index", {})
            text_hash = hashlib.md5(cleaned[:256].encode()).hexdigest()[:10]
            log_case(
                scan_type="text",
                score=reality.get("reality_score", 0),
                risk_level=reality.get("risk_level", "Medium"),
                verdict=reality.get("explanation", "")[:200],
                details=results,
                input_hash=text_hash,
            )

    # ── Render Results ────────────────────────────────────────────────────
    results = st.session_state.get("text_results")
    if results:
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        st.markdown("### ⟐ FORENSIC REPORT")

        reality = results["reality_index"]
        emotions = results["affective_signals"]
        scam = results["scam_detection"]
        url_osint = results.get("url_osint", {})

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

        # ── Row 4: URL OSINT Scanner Results ─────────────────────────────
        if url_osint and url_osint.get("total_urls", 0) > 0:
            st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
            st.markdown("#### ⟐ URL OSINT Scanner")

            osint_c1, osint_c2 = st.columns([1, 2])
            with osint_c1:
                url_risk = url_osint.get("risk_score", 0)
                url_color = "#ef4444" if url_risk >= 60 else "#f59e0b" if url_risk > 0 else "#10b981"
                st.markdown(
                    f"""
                    <div class="score-display">
                        <div class="score-value" style="color:{url_color}; font-size:2rem;">{url_risk}</div>
                        <div class="score-label">URL Risk Score</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<p style="color:#737373; font-size:0.75rem; text-align:center;">'
                    f'{url_osint["total_urls"]} URL(s) detected</p>',
                    unsafe_allow_html=True,
                )

            with osint_c2:
                flagged = url_osint.get("flagged_urls", [])
                if flagged:
                    for item in flagged:
                        flags_str = " | ".join(item["flags"])
                        st.markdown(
                            f'<p style="color:#ef4444; font-size:0.75rem; font-family:Roboto Mono,monospace; margin:4px 0;">'
                            f'▸ <span style="color:#f59e0b;">{item["url"][:80]}</span><br/>'
                            f'&nbsp;&nbsp;Flags: {flags_str}</p>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        f'<p style="color:#10b981; font-size:0.8rem;">{url_osint["verdict"]}</p>',
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

                # Log to database
                log_case(
                    scan_type="audio",
                    score=audio_results.get("authenticity_score", 0),
                    risk_level="Low" if audio_results.get("authenticity_score", 0) >= 75
                              else "Medium" if audio_results.get("authenticity_score", 0) >= 45
                              else "High",
                    verdict=audio_results.get("verdict", "")[:200],
                    details={k: v for k, v in audio_results.items() if k != "spectrogram_fig"},
                    input_hash=uploaded_file.name,
                )

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


# ── TAB 3: VISUAL SCAN (Image Forensics) ────────────────────────────────────

with tab_visual:
    st.markdown("### 🖼️ Visual Scan — Image Metadata Forensics")
    st.markdown(
        '<p style="color:#737373; font-size:0.8rem;">'
        'Upload an image to extract EXIF metadata and detect forgery or AI-generation indicators.</p>',
        unsafe_allow_html=True,
    )

    img_file = st.file_uploader(
        "UPLOAD IMAGE",
        type=["jpg", "jpeg", "png", "webp", "tiff", "bmp"],
        key="image_upload",
    )

    if img_file is not None:
        img_preview_col, img_info_col = st.columns([2, 1])
        with img_preview_col:
            st.image(img_file, use_container_width=True)
        with img_info_col:
            st.markdown(
                f'<p style="font-size:0.75rem; color:#737373;">'
                f'File: <span style="color:#22d3ee;">{img_file.name}</span><br>'
                f'Size: {img_file.size / 1024:.1f} KB</p>',
                unsafe_allow_html=True,
            )

        if st.button("▶ INITIATE VISUAL SCAN", key="btn_image_scan", use_container_width=True):
            with st.spinner("⟐ Extracting metadata... Scanning for forgery indicators..."):
                img_bytes = img_file.getvalue()
                img_results = run_image_forensics(img_bytes, img_file.name)
                st.session_state["image_results"] = img_results

                # Log to database
                log_case(
                    scan_type="image",
                    score=img_results.get("authenticity_score", 0),
                    risk_level=img_results.get("risk_level", "Medium"),
                    verdict=img_results.get("verdict", "")[:200],
                    details={k: v for k, v in img_results.items()},
                    input_hash=img_results.get("file_info", {}).get("hash", ""),
                )

    # ── Render Image Results ─────────────────────────────────────────────
    img_res = st.session_state.get("image_results")
    if img_res:
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        st.markdown("### ⟐ IMAGE FORENSIC REPORT")

        # File info bar
        finfo = img_res.get("file_info", {})
        fi_cols = st.columns(4)
        fi_cols[0].metric("Format", finfo.get("format", "N/A"))
        fi_cols[1].metric("Resolution", finfo.get("size_pixels", "N/A"))
        fi_cols[2].metric("Color Mode", finfo.get("mode", "N/A"))
        fi_cols[3].metric("Authenticity", f'{img_res.get("authenticity_score", 0)}/100')

        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

        # Authenticity Score + Verdict
        auth_score = img_res.get("authenticity_score", 0)
        auth_color = "#10b981" if auth_score >= 70 else "#f59e0b" if auth_score >= 40 else "#ef4444"
        st.markdown(
            f"""
            <div style="text-align:center; padding:16px;">
                <div style="font-family:'Share Tech Mono',monospace; font-size:3rem;
                            color:{auth_color}; text-shadow:0 0 30px {auth_color};">{auth_score}</div>
                <div style="font-size:0.7rem; color:#737373; text-transform:uppercase;
                            letter-spacing:3px; margin-top:4px;">Metadata Authenticity Score</div>
                <p style="color:{auth_color}; font-size:0.85rem; margin-top:12px;">
                    {img_res.get("verdict", "")}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

        # Forensic Cards
        fc1, fc2, fc3 = st.columns(3)

        camera = img_res.get("camera", {})
        gps = img_res.get("gps", {})
        editing = img_res.get("editing", {})
        completeness = img_res.get("completeness", {})

        with fc1:
            cam_color = "#10b981" if camera.get("has_camera_info") else "#ef4444"
            noir_card(
                "📷 Camera Info",
                f'<p style="color:{cam_color}; font-size:0.85rem; margin-bottom:8px;">'
                f'{"✓ DETECTED" if camera.get("has_camera_info") else "⚠ NOT FOUND"}</p>'
                f'<p style="font-size:0.7rem; color:#c0c0c0;">Make: {camera.get("make", "N/A")}</p>'
                f'<p style="font-size:0.7rem; color:#c0c0c0;">Model: {camera.get("model", "N/A")}</p>'
                f'<p style="font-size:0.7rem; color:#c0c0c0;">Software: {camera.get("software", "N/A")}</p>'
                f'<p style="font-size:0.7rem; color:#c0c0c0;">Date: {camera.get("datetime_original", "N/A")}</p>',
            )

        with fc2:
            gps_color = "#10b981" if gps.get("has_gps") else "#f59e0b"
            noir_card(
                "📍 GPS Geolocation",
                f'<p style="color:{gps_color}; font-size:0.85rem; margin-bottom:8px;">'
                f'{"✓ LOCATED" if gps.get("has_gps") else "⚠ NO GPS DATA"}</p>'
                f'<p style="font-size:0.7rem; color:#c0c0c0;">{gps.get("detail", "")}</p>',
            )

        with fc3:
            edit_score = editing.get("score", 50)
            edit_color = "#10b981" if edit_score >= 70 else "#f59e0b" if edit_score >= 40 else "#ef4444"
            noir_card(
                "🛠 Edit Detection",
                f'<p style="color:{edit_color}; font-size:0.85rem; margin-bottom:8px;">'
                f'{editing.get("verdict", "N/A")}</p>'
                f'<p style="font-size:0.7rem; color:#c0c0c0;">Software Tag: {editing.get("software_tag", "N/A")}</p>',
            )

        # Metadata Completeness Bar
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### ⟐ Metadata Completeness")
        comp_pct = completeness.get("completeness_pct", 0)
        comp_color = "#10b981" if comp_pct >= 70 else "#f59e0b" if comp_pct >= 30 else "#ef4444"
        st.markdown(
            f'<p style="color:{comp_color}; font-size:0.85rem;">{completeness.get("verdict", "")}</p>',
            unsafe_allow_html=True,
        )
        st.progress(comp_pct / 100)

        mc1, mc2 = st.columns(2)
        with mc1:
            st.markdown("**Fields Present:**")
            for f in completeness.get("fields_present", []):
                st.markdown(
                    f'<p style="color:#10b981; font-size:0.75rem; font-family:Roboto Mono;">✓ {f}</p>',
                    unsafe_allow_html=True,
                )
        with mc2:
            st.markdown("**Fields Missing:**")
            for f in completeness.get("fields_missing", []):
                st.markdown(
                    f'<p style="color:#ef4444; font-size:0.75rem; font-family:Roboto Mono;">✗ {f}</p>',
                    unsafe_allow_html=True,
                )

        # Raw EXIF
        with st.expander("📋 RAW EXIF DATA"):
            exif_raw = img_res.get("exif_raw", {})
            if exif_raw:
                st.json(exif_raw)
            else:
                st.markdown(
                    '<p style="color:#ef4444; font-size:0.8rem;">⚠ No EXIF data found in this image.</p>',
                    unsafe_allow_html=True,
                )

        # Export
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        img_report = json.dumps(img_res, indent=4, default=str)
        st.download_button(
            label="⬇ EXPORT IMAGE FORENSIC REPORT (JSON)",
            data=img_report,
            file_name="astral_lens_image_report.json",
            mime="application/json",
            use_container_width=True,
        )


# ── TAB 4: NETWORK SCAN (IP & Server Forensics) ─────────────────────────────

with tab_network:
    st.markdown("### 🌐 Network Scan — IP & Domain Forensics")
    st.markdown(
        '<p style="color:#737373; font-size:0.8rem;">'
        'Trace the physical location and anonymity infrastructure (VPN, Proxy, Datacenter) of a suspicious IP or Domain.</p>',
        unsafe_allow_html=True,
    )

    net_input = st.text_input(
        "TRACE TARGET (Domain or IP)",
        placeholder="e.g., scam-web.com or 192.168.1.1",
        key="network_input"
    )

    if st.button("▶ EXECUTE GLOBAL TRACE", key="btn_network_trace", use_container_width=True):
        if net_input.strip():
            with st.spinner("⟐ Establishing uplink... Intercepting routing data... Locating target..."):
                net_results = run_network_forensics(net_input)
                st.session_state["network_results"] = net_results
                
                # Log to DB if successful
                if "error" not in net_results:
                    log_case(
                        scan_type="network",
                        score=net_results.get("risk_score", 0),
                        risk_level=net_results.get("risk_level", "Medium"),
                        verdict=net_results.get("verdict", "")[:200],
                        details={k: v for k, v in net_results.items() if k != "map_figure"},
                        input_hash=net_results.get("target", "")
                    )

    net_res = st.session_state.get("network_results")
    if net_res:
        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
        st.markdown("### ⟐ TRACE LOG")

        if "error" in net_res:
            st.markdown(
                f'<div class="warning-box">{net_res["error"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            n_cols = st.columns(4)
            n_cols[0].metric("Target Node", net_res.get("target", "N/A"))
            n_cols[1].metric("IP Address", net_res.get("ip_address", "N/A"))
            n_cols[2].metric("ISP", net_res.get("isp", "N/A")[:20] + ("..." if len(net_res.get("isp", "")) > 20 else ""))
            n_cols[3].metric("Risk Score", f"{net_res.get('risk_score', 0)}/100")

            st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
            
            # Risk Verdict
            rk_score = net_res.get("risk_score", 0)
            rk_color = "#ef4444" if rk_score >= 80 else "#f59e0b" if rk_score >= 40 else "#10b981"
            
            st.markdown(
                f"""
                <div style="text-align:center; padding:16px;">
                    <div style="font-family:'Share Tech Mono',monospace; font-size:3rem;
                                color:{rk_color}; text-shadow:0 0 30px {rk_color};">{rk_score}</div>
                    <div style="font-size:0.7rem; color:#737373; text-transform:uppercase;
                                letter-spacing:3px; margin-top:4px;">Infrastructure Danger Level</div>
                    <p style="color:{rk_color}; font-size:0.85rem; margin-top:12px;">{net_res.get('verdict', '')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

            nc1, nc2 = st.columns([1, 2])
            
            with nc1:
                st.markdown("#### ⟐ Infrastructure Analysis", unsafe_allow_html=True)
                
                is_proxy = net_res.get("is_proxy", False)
                is_hosting = net_res.get("is_hosting", False)
                
                px_color = "#ef4444" if is_proxy else "#10b981"
                st.markdown(
                    f'<p style="color:{px_color}; font-family:Roboto Mono; font-size:0.85rem; margin-bottom:12px;">'
                    f'{"⚠ VPN / Proxy Detected" if is_proxy else "✓ Direct Connection"}',
                    unsafe_allow_html=True,
                )
                
                hs_color = "#f59e0b" if is_hosting else "#10b981"
                st.markdown(
                    f'<p style="color:{hs_color}; font-family:Roboto Mono; font-size:0.85rem; margin-bottom:12px;">'
                    f'{"⚡ Data Center / Cloud Hosting" if is_hosting else "✓ Residential / Business IPv4"}',
                    unsafe_allow_html=True,
                )
                
                flags = net_res.get("anonymity_flags", [])
                if flags:
                    st.markdown("**Anonymity Flags:**")
                    for flag in flags:
                        st.markdown(
                            f'<p style="color:#ef4444; font-size:0.75rem;">▸ {flag}</p>',
                            unsafe_allow_html=True,
                        )
                
                st.markdown("#### ⟐ Node Registration", unsafe_allow_html=True)
                noir_card("Organization Data", 
                          f'<p style="font-size:0.7rem; color:#c0c0c0;">ASN: {net_res.get("asn", "Unknown")}</p>'
                          f'<p style="font-size:0.7rem; color:#c0c0c0;">Org: {net_res.get("organization", "Unknown")}</p>'
                          f'<p style="font-size:0.7rem; color:#c0c0c0;">Location: {net_res.get("location", "Unknown")}</p>')
            
            with nc2:
                st.markdown("#### ⟐ Global Radar Map", unsafe_allow_html=True)
                map_fig = net_res.get("map_figure")
                if map_fig:
                    st.plotly_chart(map_fig, use_container_width=True, key="network_map")
                else:
                    st.markdown("`[ERROR] Unable to generate radar map.`")

            # Export
            st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
            export_data = {k: v for k, v in net_res.items() if k != "map_figure"}
            st.download_button(
                label="⬇ EXPORT NETWORK TRACE (JSON)",
                data=json.dumps(export_data, indent=4),
                file_name="astral_lens_network_trace.json",
                mime="application/json",
                use_container_width=True,
            )


# ── TAB 5: CASE ARCHIVES ────────────────────────────────────────────────────

with tab_archives:
    st.markdown("### 📁 Case Archives — Forensic History")
    st.markdown(
        '<p style="color:#737373; font-size:0.8rem;">'
        'Browse previous forensic scans stored locally. All case data is persisted in the local SQLite database.</p>',
        unsafe_allow_html=True,
    )

    cases = get_recent_cases(50)

    if not cases:
        st.markdown(
            '<div style="text-align:center; padding:60px 0;">'
            '<p style="color:#737373; font-size:1rem;">⟐ No cases logged yet.</p>'
            '<p style="color:#737373; font-size:0.75rem;">Run a scan to populate the archive.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        # Summary stats
        stats = get_stats()
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Total Cases", stats["total_scans"])
        sc2.metric("Text Scans", stats["text_scans"])
        sc3.metric("Audio Scans", stats["audio_scans"])
        sc4.metric("Image Scans", stats["image_scans"])

        st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

        for case in cases:
            scan_icon = {"text": "📡", "audio": "🔊", "image": "🖼️", "network": "🌐"}.get(case["scan_type"], "📋")
            score = case.get("score", 0) or 0
            sc_color = "#10b981" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"
            risk = case.get("risk_level", "N/A")

            st.markdown(
                f"""
                <div class="noir-card" style="padding:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-size:1.2rem;">{scan_icon}</span>
                            <span style="color:#3b82f6; font-family:Roboto Mono; font-size:0.85rem;
                                         text-transform:uppercase; letter-spacing:1px; margin-left:8px;">
                                {case["scan_type"]} scan
                            </span>
                            <span style="color:#737373; font-size:0.7rem; margin-left:12px;">
                                {case.get("timestamp", "")}
                            </span>
                        </div>
                        <div>
                            <span style="color:{sc_color}; font-family:Share Tech Mono; font-size:1.3rem;
                                         text-shadow:0 0 10px {sc_color};">
                                {score}
                            </span>
                            <span style="color:#737373; font-size:0.6rem; margin-left:4px;">/100</span>
                            &nbsp;&nbsp;{risk_badge(risk)}
                        </div>
                    </div>
                    <p style="color:#737373; font-size:0.7rem; margin-top:8px; line-height:1.5;">
                        {case.get("verdict", "")[:150]}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ── TAB 5: AWARENESS HUB ────────────────────────────────────────────────────

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

    with st.expander("🔗 URL OSINT — Link Intelligence"):
        st.markdown(
            """
            <div class="info-box">
            <strong>What it measures:</strong> Suspicious URLs embedded in text content.<br><br>
            <strong>How it works:</strong><br>
            ▸ Extracts all URLs from the original (uncleaned) text<br>
            ▸ Checks for <strong>suspicious TLDs</strong> (.xyz, .tk, .buzz, etc.)<br>
            ▸ Scans for <strong>phishing keywords</strong> in domain names (secure-login, verify-identity)<br>
            ▸ Detects <strong>IP-based URLs</strong> and excessive subdomain chains<br><br>
            <strong>Why it matters:</strong><br>
            Phishing attacks often use deceptive URLs that mimic legitimate services. Detecting these patterns
            helps identify social engineering attempts before they succeed.
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

    with st.expander("🖼️ IMAGE FORENSICS — Metadata Analysis"):
        st.markdown(
            """
            <div class="info-box">
            <strong>What it measures:</strong> Whether an image contains authentic camera metadata (EXIF).<br><br>
            <strong>Four Analysis Layers:</strong><br><br>
            <strong>1. Camera Information</strong><br>
            ▸ Checks for device Make, Model, and capture DateTime<br>
            ▸ Authentic photos contain rich camera metadata<br><br>
            <strong>2. GPS Geolocation</strong><br>
            ▸ Checks for embedded GPS coordinates<br>
            ▸ Presence of GPS data strongly indicates a real camera capture<br><br>
            <strong>3. Editing Software Detection</strong><br>
            ▸ Scans for signatures of <strong>known editing tools</strong> (Photoshop, GIMP, etc.)<br>
            ▸ Also detects <strong>AI generator signatures</strong> (DALL-E, Midjourney, Stable Diffusion)<br><br>
            <strong>4. Metadata Completeness</strong><br>
            ▸ Scores the presence of 10 key EXIF fields<br>
            ▸ AI-generated images and screenshots typically have <strong>zero EXIF metadata</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("🌐 NETWORK FORENSICS — IP Trace"):
        st.markdown(
            """
            <div class="info-box">
            <strong>What it measures:</strong> The physical location and infrastructure anonymity of a Domain or IP.<br><br>
            <strong>How it works:</strong><br>
            ▸ Resolves domain names to physical server IPs<br>
            ▸ Looks for <strong>Anonymity Tools</strong> (VPNs, Proxies, Tor Exit Nodes)<br>
            ▸ Distinguishes between normal endpoints and <strong>Cloud Datacenters</strong><br>
            ▸ Generates an interactive <strong>3D Orthographic Radar Map</strong> using Plotly<br><br>
            <strong>Why it matters:</strong><br>
            Scammers and malware authors rarely use their home internet connections. If an email
            claims to be from a "Local Indonesian Bank", but the Network Scan shows the web server
            is hiding behind a Russian VPN, it is highly likely to be malicious.
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
            <p>⟐ ASTRAL-LENS v2.0 · Built for Digital Literacy & AI Awareness ⟐</p>
            <p style="margin-top:4px;">This tool is educational — always verify findings with multiple sources.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
