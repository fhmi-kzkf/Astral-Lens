"""
Astral-Lens — Text Forensic Engine
Gemini 2.5 Flash-based multi-layered analysis:
  • Reality Index (credibility scoring)
  • Affective Signal Analysis (emotion detection)
  • Malicious Pattern Recognition (scam detection)
  • URL OSINT Scanner (phishing / suspicious link detection)
"""

import json
import re
import hashlib
from urllib.parse import urlparse

import google.generativeai as genai

# ── Known Scam Regex Patterns ────────────────────────────────────────────────

SCAM_PATTERNS = [
    (r"investasi\s+cepat", "Investasi cepat (fast investment)"),
    (r"jamin\s+profit", "Jamin profit (guaranteed profit)"),
    (r"uang\s+gratis", "Uang gratis (free money)"),
    (r"klik\s+(di\s+)?sini\s+sekarang", "Klik sini sekarang (click here now)"),
    (r"100%\s*(pasti|untung|aman)", "100% guarantee claim"),
    (r"transfer\s+(segera|sekarang)", "Transfer segera (transfer now)"),
    (r"limited\s+time\s+offer", "Limited time offer"),
    (r"act\s+now", "Act now pressure"),
    (r"congratulations.*won", "Congratulations you won"),
    (r"double\s+your\s+(money|income|bitcoin)", "Double your money"),
    (r"no\s+risk", "No risk claim"),
    (r"guaranteed\s+(returns?|profit|income)", "Guaranteed returns"),
    (r"get\s+rich\s+quick", "Get rich quick"),
    (r"wire\s+transfer", "Wire transfer request"),
    (r"send\s+(money|funds|payment)\s+(to|via)", "Send money request"),
    (r"whatsapp.*\+\d{10,}", "WhatsApp number solicitation"),
]


# ── Suspicious URL Patterns ──────────────────────────────────────────────────

SUSPICIOUS_TLD = [
    ".xyz", ".top", ".club", ".buzz", ".work", ".loan",
    ".click", ".link", ".info", ".tk", ".ml", ".ga", ".cf",
]

PHISHING_KEYWORDS = [
    "secure-login", "update-account", "verify-identity", "confirm-payment",
    "wallet-connect", "free-prize", "claim-reward", "bit.ly", "tinyurl",
    "signin", "log-in", "account-verify", "password-reset",
]


def _configure_gemini(api_key: str):
    """Configure the Gemini API client with system instructions and JSON enforcement."""
    genai.configure(api_key=api_key)
    
    # System Instructions give the AI a strong persona
    system_instruction = (
        "You are Astral-Lens, an advanced cyber-forensic AI designed to analyze "
        "digital content for disinformation, emotional manipulation, and scams. "
        "Your responses must be highly analytical, cold, and technical."
    )
    
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_instruction,
        generation_config={"response_mime_type": "application/json"}
    )


def _parse_json_response(text: str) -> dict:
    """Extract JSON from Gemini response, handling markdown code fences."""
    # Try to find JSON in code fences
    match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response", "raw": text}


def _themed_error(stage: str, e: Exception) -> str:
    """Return a Cyber-Noir styled error message instead of raw traceback."""
    err_type = type(e).__name__
    if "429" in str(e) or "ResourceExhausted" in err_type:
        return (f"⚠ SIGNAL LOST — Rate limit exceeded on {stage}. "
                "Mainframe cooling down. Retry in 60 seconds.")
    elif "APIError" in err_type or "GoogleAPIError" in err_type:
        return (f"⚠ CRITICAL FAILURE — {stage} mainframe disconnected. "
                f"Error: {err_type}")
    elif "Timeout" in err_type or "timeout" in str(e).lower():
        return (f"⚠ CONNECTION TIMEOUT — {stage} uplink severed. "
                "Check network and retry.")
    else:
        return (f"⚠ SYSTEM MALFUNCTION — {stage} encountered an anomaly: "
                f"{err_type}: {str(e)[:120]}")


# ── Reality Index ─────────────────────────────────────────────────────────────

def analyze_reality_index(text: str, api_key: str) -> dict:
    """
    Analyse text credibility using Gemini 2.5 Flash.

    Returns dict with keys:
      reality_score (int 0-100), risk_level (str), explanation (str)
    """
    model = _configure_gemini(api_key)

    prompt = f"""Analyze the credibility and factual consistency of this text:
"{text}"

Return a JSON object matching exactly this schema:
{{
    "reality_score": <int 0-100, 100=credible>,
    "risk_level": "<Low|Medium|High>",
    "explanation": "<A clear, 3-4 sentence analytical breakdown of credibility. Cite specific examples from the text if it is suspicious.>"
}}

Scoring:
80-100: Factually consistent, neutral.
50-79: Minor inconsistencies, slight bias.
20-49: Emotional manipulation, questionable claims.
0-19: Clear disinformation, malicious intent."""

    try:
        response = model.generate_content(prompt)
        return _parse_json_response(response.text)
    except Exception as e:
        return {
            "reality_score": -1,
            "risk_level": "Error",
            "explanation": _themed_error("Reality Index", e),
        }


# ── Affective Signal Analysis ────────────────────────────────────────────────

def analyze_emotions(text: str, api_key: str) -> dict:
    """
    Detect emotional manipulation patterns.

    Returns dict with keys:
      emotions (dict of percentages), manipulation_warning (bool), analysis (str)
    """
    model = _configure_gemini(api_key)

    prompt = f"""Analyze the emotional manipulation signals in this text:
"{text}"

Return a JSON object matching exactly this schema:
{{
    "emotions": {{"fear": <int 0-100>, "anger": <int 0-100>, "trust": <int 0-100>, "neutral": <int 0-100>}},
    "manipulation_warning": <true if fear/anger > 65>,
    "dominant_emotion": "<emotion>",
    "analysis": "<A 3-4 sentence explanation of how emotions are weaponized or used naturally. Identify specific trigger phrases used in the text.>"
}}"""

    try:
        response = model.generate_content(prompt)
        return _parse_json_response(response.text)
    except Exception as e:
        return {
            "emotions": {"fear": 0, "anger": 0, "trust": 0, "neutral": 100},
            "manipulation_warning": False,
            "dominant_emotion": "neutral",
            "analysis": _themed_error("Affective Signal", e),
        }


# ── Scam Detection (Hybrid) ─────────────────────────────────────────────────

def detect_scam(text: str, api_key: str) -> dict:
    """
    Hybrid scam detection: regex + Gemini semantic analysis.

    Returns dict with keys:
      scam_score (int 0-100), matched_patterns (list), semantic_analysis (str),
      is_scam (bool)
    """
    # Phase 1 — Regex pattern matching
    matched = []
    text_lower = text.lower()
    for pattern, label in SCAM_PATTERNS:
        if re.search(pattern, text_lower):
            matched.append(label)

    regex_score = min(len(matched) * 20, 80)  # cap at 80 from regex alone

    # Phase 2 — Gemini semantic analysis
    model = _configure_gemini(api_key)

    prompt = f"""Analyze this text for scam intent, urgency, and deceptive patterns:
"{text}"
Known regex matches: {json.dumps(matched) if matched else "None"}

Return a JSON object matching exactly this schema:
{{
    "semantic_scam_score": <int 0-100>,
    "hidden_intent": "<Brief 1-2 sentence description of any hidden malicious intent>",
    "urgency_tactics": "<Brief 1-2 sentence description of any artificial urgency or pressure>",
    "deceptive_patterns": "<Brief 1-2 sentence description of deceptive language used>",
    "verdict": "<CLEAN|SUSPICIOUS|SCAM>"
}}"""

    try:
        response = model.generate_content(prompt)
        semantic = _parse_json_response(response.text)
    except Exception as e:
        semantic = {
            "semantic_scam_score": 0,
            "hidden_intent": _themed_error("Scam Detection", e),
            "urgency_tactics": "N/A",
            "deceptive_patterns": "N/A",
            "verdict": "ERROR",
        }

    # Combine scores
    sem_score = semantic.get("semantic_scam_score", 0)
    combined_score = min(int(regex_score * 0.4 + sem_score * 0.6), 100)

    return {
        "scam_score": combined_score,
        "matched_patterns": matched,
        "semantic_analysis": semantic,
        "is_scam": combined_score >= 60,
    }


# ── URL OSINT Scanner ────────────────────────────────────────────────────────

def extract_urls(text: str) -> list[str]:
    """Extract all URLs from the raw (uncleaned) input text."""
    url_pattern = re.compile(
        r'https?://[^\s<>"\')]+|www\.[^\s<>"\')]+',
        re.IGNORECASE,
    )
    return url_pattern.findall(text)


def analyze_urls(urls: list[str]) -> dict:
    """
    Perform heuristic OSINT analysis on extracted URLs.

    Returns dict with keys:
      total_urls, flagged_urls (list), risk_score (0-100), verdict
    """
    if not urls:
        return {
            "total_urls": 0,
            "flagged_urls": [],
            "risk_score": 0,
            "verdict": "CLEAN — No URLs detected in input.",
        }

    flagged = []
    for url in urls:
        reasons = []
        parsed = urlparse(url if url.startswith("http") else f"http://{url}")
        domain = parsed.netloc.lower()

        # Check suspicious TLDs
        for tld in SUSPICIOUS_TLD:
            if domain.endswith(tld):
                reasons.append(f"Suspicious TLD: {tld}")
                break

        # Check phishing keywords in domain
        for kw in PHISHING_KEYWORDS:
            if kw in domain or kw in parsed.path.lower():
                reasons.append(f"Phishing keyword: {kw}")
                break

        # Excessively long subdomain chains
        subdomains = domain.split(".")
        if len(subdomains) > 4:
            reasons.append(f"Excessive subdomains ({len(subdomains)} levels)")

        # IP address instead of domain
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
            reasons.append("IP address used instead of domain name")

        if reasons:
            flagged.append({"url": url, "flags": reasons})

    risk_score = min(int(len(flagged) / len(urls) * 100), 100) if urls else 0

    if risk_score >= 60:
        verdict = "⚠ HIGH RISK — Multiple suspicious URLs detected"
    elif risk_score > 0:
        verdict = "⚡ CAUTION — Some URLs exhibit suspicious characteristics"
    else:
        verdict = "✓ CLEAN — No obviously suspicious URL patterns found"

    return {
        "total_urls": len(urls),
        "flagged_urls": flagged,
        "risk_score": risk_score,
        "verdict": verdict,
    }


# ── Full Analysis Orchestrator ───────────────────────────────────────────────

def run_full_analysis(text: str, api_key: str, raw_text: str = "") -> dict:
    """
    Run all analyses and cross-reference results.

    Parameters
    ----------
    text : str
        Cleaned text for AI analysis.
    api_key : str
        Gemini API key.
    raw_text : str
        Original uncleaned text (used for URL extraction).
    """
    reality = analyze_reality_index(text, api_key)
    emotions = analyze_emotions(text, api_key)
    scam = detect_scam(text, api_key)

    # URL OSINT on the RAW text (before URLs were stripped)
    urls = extract_urls(raw_text or text)
    url_osint = analyze_urls(urls)

    # Cross-reference: high scam score reduces reality index
    if scam.get("scam_score", 0) >= 60:
        penalty = int(scam["scam_score"] * 0.4)
        original = reality.get("reality_score", 50)
        reality["reality_score"] = max(0, original - penalty)
        reality["risk_level"] = "High"
        reality["explanation"] = (
            f"[SCAM PENALTY APPLIED: -{penalty} pts] "
            + reality.get("explanation", "")
        )

    # URL risk also affects scam score
    if url_osint["risk_score"] >= 60:
        url_penalty = int(url_osint["risk_score"] * 0.25)
        original = reality.get("reality_score", 50)
        reality["reality_score"] = max(0, original - url_penalty)
        if reality.get("risk_level") == "Low":
            reality["risk_level"] = "Medium"

    # Emotional manipulation also affects credibility
    fear = emotions.get("emotions", {}).get("fear", 0)
    anger = emotions.get("emotions", {}).get("anger", 0)
    if fear > 65 or anger > 65:
        emo_penalty = int(max(fear, anger) * 0.15)
        original = reality.get("reality_score", 50)
        reality["reality_score"] = max(0, original - emo_penalty)
        if reality.get("risk_level") != "High":
            reality["risk_level"] = "Medium"

    return {
        "reality_index": reality,
        "affective_signals": emotions,
        "scam_detection": scam,
        "url_osint": url_osint,
    }
