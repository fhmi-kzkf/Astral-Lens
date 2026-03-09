"""
Astral-Lens — Text Forensic Engine
Gemini 2.5 Flash-based multi-layered analysis:
  • Reality Index (credibility scoring)
  • Affective Signal Analysis (emotion detection)
  • Malicious Pattern Recognition (scam detection)
"""

import json
import re

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
            "explanation": f"Analysis failed: {str(e)}",
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
            "analysis": f"Analysis failed: {str(e)}",
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
            "hidden_intent": f"Analysis failed: {str(e)}",
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


# ── Full Analysis Orchestrator ───────────────────────────────────────────────

def run_full_analysis(text: str, api_key: str) -> dict:
    """
    Run all three analyses and cross-reference results.

    Scam detection can lower the Reality Index.
    """
    reality = analyze_reality_index(text, api_key)
    emotions = analyze_emotions(text, api_key)
    scam = detect_scam(text, api_key)

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
    }
