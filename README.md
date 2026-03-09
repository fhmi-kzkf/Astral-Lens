# Astral-Lens: Digital Forensic & AI Awareness Terminal

Astral-Lens is a production-ready Cyber-Noir themed web application designed for forensic analysis of digital content. It provides deep multi-layered insights into text and audio to detect disinformation, emotional manipulation, scams, and synthetic (AI-generated) media.

## Features

### 📡 Signal Scan (Text Forensics)
Powered by high-speed analysis using **Google Gemini 2.5 Flash**, the text module uncovers:
- **Reality Index**: A 0-100 credibility score analyzing logical consistency and factual claims.
- **Affective Signals**: Detects the balance of Fear, Anger, Trust, and Neutral emotions to identify psychological manipulation.
- **Scam Detection**: A hybrid system combining regex rules for known local scams (e.g., "investasi cepat") and Gemini's semantic understanding of hidden urgency tactics.
- **Export Capabilities**: Download the forensic results as a JSON audit report.

### 🔊 Frequency Scan (Audio Forensics)
Powered by **Librosa** for rapid, heuristic-based signal anomaly detection:
- **F₀ Pitch Stability**: Measures the coefficient of variation in human pitch. Unnaturally stable pitch often indicates synthetic text-to-speech.
- **Spectral Flatness**: Identifies white-noise-like properties and digital aliasing typical of deepfakes.
- **RMS Energy Dynamics**: Counts natural silence gaps (breaths/pauses) vs. unnaturally flat AI energy distribution.
- **Interactive Mel-Spectrograms**: Visualizes the frequencies using Plotly.

### 🎓 Awareness Hub
An educational dashboard built directly into the app that explains the forensic heuristics behind the analyses. Perfect for digital literacy programs.

## Requirements & Setup

1. **Python 3.10+** recommended.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **API Keys**:
   - Copy `.env.example` to a new file named `.env`.
   - Add your [Google AI Studio](https://aistudio.google.com/app/apikey) API key for Gemini.
   ```env
   GOOGLE_API_KEY="your_api_key_here"
   ```

## Running the Application

Execute the Streamlit entry script:
```bash
streamlit run app.py
```
The terminal will open locally at `http://localhost:8501`.

## Architecture & Aesthetics
- **Theme**: Custom CSS injected for a Cyber-Noir "hacker" style (Deep black, Neon Blue, Mono fonts).
- **Caching**: The heavy audio calculations use `@st.cache_data` to ensure fluid UX when switching between dashboards.
- **Robust Parsing**: Communication with Gemini uses strict Schema Mime-Types to ensure programmatic reliability.
