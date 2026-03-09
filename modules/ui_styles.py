"""
Astral-Lens — Cyber-Noir UI Styles
Inject CSS for the deep-black, neon-blue, monospace aesthetic.
"""

import streamlit as st


def inject_css():
    """Inject the full Cyber-Noir CSS theme into the Streamlit app."""
    st.markdown(
        """
        <style>
        /* ── Google Font Import ────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

        /* ── Root Variables ────────────────────────────────────── */
        :root {
            --bg-primary:   #050505;
            --bg-secondary: #0a0a0a;
            --bg-card:      #0d0d0d;
            --bg-card-hover:#111111;
            --neon-blue:    #3b82f6;
            --neon-cyan:    #22d3ee;
            --neon-green:   #10b981;
            --neon-red:     #ef4444;
            --neon-yellow:  #f59e0b;
            --neon-purple:  #a855f7;
            --text-primary: #d4d4d4;
            --text-muted:   #737373;
            --border-color: #1a1a1a;
            --glow-blue:    0 0 15px rgba(59,130,246,0.3);
            --glow-red:     0 0 15px rgba(239,68,68,0.3);
            --glow-green:   0 0 15px rgba(16,185,129,0.3);
        }

        /* ── Global Overrides ─────────────────────────────────── */
        html, body, [data-testid="stAppViewContainer"],
        [data-testid="stApp"] {
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
            font-family: 'Roboto Mono', 'Courier New', monospace !important;
        }

        [data-testid="stSidebar"] {
            background-color: var(--bg-secondary) !important;
            border-right: 1px solid var(--border-color) !important;
        }

        [data-testid="stHeader"] {
            background-color: transparent !important;
        }

        /* ── Headings ─────────────────────────────────────────── */
        h1, h2, h3, h4 {
            font-family: 'Share Tech Mono', 'Roboto Mono', monospace !important;
            color: var(--neon-blue) !important;
            text-shadow: var(--glow-blue);
            letter-spacing: 1.5px;
        }

        h1 { font-size: 2rem !important; }

        /* ── Tabs ─────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            background-color: var(--bg-secondary);
            border-radius: 8px;
            padding: 4px;
            border: 1px solid var(--border-color);
        }

        .stTabs [data-baseweb="tab"] {
            font-family: 'Roboto Mono', monospace !important;
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-muted) !important;
            background-color: transparent !important;
            border-radius: 6px;
            padding: 8px 20px;
            transition: all 0.3s ease;
        }

        .stTabs [aria-selected="true"] {
            color: var(--neon-blue) !important;
            background-color: rgba(59,130,246,0.1) !important;
            border-bottom: 2px solid var(--neon-blue) !important;
            text-shadow: var(--glow-blue);
        }

        /* ── Buttons ──────────────────────────────────────────── */
        .stButton > button {
            font-family: 'Roboto Mono', monospace !important;
            background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 10px 28px !important;
            font-weight: 600 !important;
            letter-spacing: 1px;
            text-transform: uppercase;
            transition: all 0.3s ease;
            box-shadow: var(--glow-blue);
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
            box-shadow: 0 0 25px rgba(59,130,246,0.5);
            transform: translateY(-1px);
        }

        /* ── Text Area & Inputs ───────────────────────────────── */
        .stTextArea textarea, .stTextInput input {
            font-family: 'Roboto Mono', monospace !important;
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 6px !important;
            transition: border-color 0.3s ease;
        }

        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: var(--neon-blue) !important;
            box-shadow: var(--glow-blue) !important;
        }

        /* ── File Uploader ────────────────────────────────────── */
        [data-testid="stFileUploader"] {
            background-color: var(--bg-card) !important;
            border: 1px dashed var(--border-color) !important;
            border-radius: 8px !important;
            padding: 20px !important;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: var(--neon-blue) !important;
        }

        /* ── Expander ─────────────────────────────────────────── */
        .streamlit-expanderHeader {
            font-family: 'Roboto Mono', monospace !important;
            background-color: var(--bg-card) !important;
            color: var(--neon-blue) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 6px !important;
        }

        /* ── Metric containers ────────────────────────────────── */
        [data-testid="stMetric"] {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            transition: all 0.3s ease;
        }

        [data-testid="stMetric"]:hover {
            border-color: var(--neon-blue);
            box-shadow: var(--glow-blue);
        }

        [data-testid="stMetricLabel"] {
            font-family: 'Roboto Mono', monospace !important;
            color: var(--text-muted) !important;
            text-transform: uppercase;
            font-size: 0.7rem !important;
            letter-spacing: 2px;
        }

        [data-testid="stMetricValue"] {
            font-family: 'Share Tech Mono', monospace !important;
            color: var(--neon-blue) !important;
            text-shadow: var(--glow-blue);
        }

        /* ── Progress bars ────────────────────────────────────── */
        .stProgress > div > div {
            background-color: var(--border-color) !important;
            border-radius: 4px;
        }

        /* ── Spinner ──────────────────────────────────────────── */
        .stSpinner > div {
            border-top-color: var(--neon-blue) !important;
        }

        /* ── Scrollbar ────────────────────────────────────────── */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--neon-blue);
        }

        /* ── Custom Noir Card ─────────────────────────────────── */
        .noir-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.3s ease;
        }
        .noir-card:hover {
            border-color: var(--neon-blue);
            box-shadow: var(--glow-blue);
        }

        .noir-card h4 {
            margin-top: 0;
            font-size: 0.85rem !important;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        /* ── Risk Level Badge ─────────────────────────────────── */
        .risk-low {
            display: inline-block;
            background: rgba(16,185,129,0.15);
            color: var(--neon-green);
            border: 1px solid var(--neon-green);
            border-radius: 4px;
            padding: 4px 14px;
            font-family: 'Roboto Mono', monospace;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            text-shadow: var(--glow-green);
        }
        .risk-medium {
            display: inline-block;
            background: rgba(245,158,11,0.15);
            color: var(--neon-yellow);
            border: 1px solid var(--neon-yellow);
            border-radius: 4px;
            padding: 4px 14px;
            font-family: 'Roboto Mono', monospace;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }
        .risk-high {
            display: inline-block;
            background: rgba(239,68,68,0.15);
            color: var(--neon-red);
            border: 1px solid var(--neon-red);
            border-radius: 4px;
            padding: 4px 14px;
            font-family: 'Roboto Mono', monospace;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            text-shadow: var(--glow-red);
            animation: pulse-red 2s ease-in-out infinite;
        }

        @keyframes pulse-red {
            0%, 100% { box-shadow: 0 0 5px rgba(239,68,68,0.3); }
            50%      { box-shadow: 0 0 20px rgba(239,68,68,0.6); }
        }

        /* ── Scan Line Animation ──────────────────────────────── */
        .scan-line {
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--neon-blue), transparent);
            animation: scanline 2s ease-in-out infinite;
            margin: 10px 0;
            border-radius: 1px;
        }

        @keyframes scanline {
            0%   { opacity: 0.3; transform: scaleX(0.3); }
            50%  { opacity: 1;   transform: scaleX(1); }
            100% { opacity: 0.3; transform: scaleX(0.3); }
        }

        /* ── Neon Divider ─────────────────────────────────────── */
        .neon-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--neon-blue), transparent);
            margin: 24px 0;
            border: none;
        }

        /* ── Score Gauge ──────────────────────────────────────── */
        .score-display {
            text-align: center;
            padding: 20px;
        }
        .score-display .score-value {
            font-family: 'Share Tech Mono', monospace;
            font-size: 3.5rem;
            font-weight: 700;
            line-height: 1;
            text-shadow: 0 0 30px currentColor;
        }
        .score-display .score-label {
            font-family: 'Roboto Mono', monospace;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 3px;
            color: var(--text-muted);
            margin-top: 8px;
        }

        /* ── Warning Box ──────────────────────────────────────── */
        .warning-box {
            background: rgba(239,68,68,0.08);
            border: 1px solid var(--neon-red);
            border-left: 4px solid var(--neon-red);
            border-radius: 6px;
            padding: 16px 20px;
            margin: 12px 0;
            font-family: 'Roboto Mono', monospace;
            font-size: 0.85rem;
            color: var(--neon-red);
        }

        .info-box {
            background: rgba(59,130,246,0.08);
            border: 1px solid var(--neon-blue);
            border-left: 4px solid var(--neon-blue);
            border-radius: 6px;
            padding: 16px 20px;
            margin: 12px 0;
            font-family: 'Roboto Mono', monospace;
            font-size: 0.85rem;
            color: var(--neon-blue);
        }

        /* ── Hide Streamlit Branding ──────────────────────────── */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header[data-testid="stHeader"] { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    """Render the Astral-Lens terminal-style header."""
    st.markdown(
        """
        <div style="text-align:center; padding: 20px 0 10px 0;">
            <h1 style="margin:0; font-size:2.2rem !important;">
                ⟐ ASTRAL-LENS ⟐
            </h1>
            <p style="color:#737373; font-size:0.75rem; letter-spacing:4px;
                       text-transform:uppercase; margin-top:4px;
                       font-family:'Roboto Mono',monospace;">
                Digital Forensic &amp; AI Awareness Terminal
            </p>
            <div class="scan-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Render the sidebar branding and API key input."""
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
                    v1.0 · forensic engine
                </p>
            </div>
            <div class="neon-divider"></div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="padding:8px 0; font-size:0.7rem; color:#737373;
                        font-family:'Roboto Mono',monospace;">
                <p>▸ <span style="color:#3b82f6;">SIGNAL SCAN</span> — Text Forensics</p>
                <p>▸ <span style="color:#3b82f6;">FREQ SCAN</span> — Audio Forensics</p>
                <p>▸ <span style="color:#3b82f6;">AWARENESS</span> — Education Hub</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def noir_card(title: str, content: str):
    """Render a styled card with HTML content."""
    st.markdown(
        f"""
        <div class="noir-card">
            <h4>{title}</h4>
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(level: str) -> str:
    """Return HTML for a risk-level badge."""
    css_class = {
        "Low": "risk-low",
        "Medium": "risk-medium",
        "High": "risk-high",
    }.get(level, "risk-medium")
    return f'<span class="{css_class}">{level} Risk</span>'


def score_gauge(value: int, label: str = "Reality Index") -> str:
    """Return HTML for a large score display."""
    if value >= 70:
        color = "var(--neon-green)"
    elif value >= 40:
        color = "var(--neon-yellow)"
    else:
        color = "var(--neon-red)"

    return f"""
    <div class="score-display">
        <div class="score-value" style="color:{color};">{value}</div>
        <div class="score-label">{label}</div>
    </div>
    """
