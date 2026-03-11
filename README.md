# ⟐ ASTRAL-LENS v2.0
> **Digital Forensic & AI Awareness Terminal**

![Astral-Lens Banner](https://img.shields.io/badge/Status-Production_Ready-10b981?style=for-the-badge)
![Gemini AI](https://img.shields.io/badge/Powered_by-Gemini_2.5_Flash-3b82f6?style=for-the-badge)
![Python 3.10+](https://img.shields.io/badge/Python-3.10+-f59e0b?style=for-the-badge)

Astral-Lens is a production-ready, Cyber-Noir themed web application designed for comprehensive forensic analysis of digital content. It provides deep multi-layered insights to detect disinformation, emotional manipulation, scams, malicious infrastructure, and synthetic (AI-generated) media.

Built for hackathons, digital literacy programs, and cyber-security demonstrations, Astral-Lens combines cutting-edge LLM semantic understanding with deterministic heuristic algorithms (Digital Signal Processing, EXIF analysis, and IP routing OSINT).

---

## 🚀 Core Features (The 6 Pillars)

### 1. 📡 Signal Scan (Text Forensics)
Powered by high-speed analysis using **Google Gemini 2.5 Flash**, the text module uncovers:
- **Document Support:** Upload `.pdf` or `.txt` directly, or paste text.
- **Reality Index**: A 0-100 credibility score analyzing logical consistency and factual claims.
- **Affective Signals**: Detects the balance of Fear, Anger, Trust, and Neutral emotions to identify psychological manipulation.
- **Scam Detection**: A hybrid system combining regex rules for known local scams (e.g., "investasi cepat") and Gemini's semantic understanding of hidden urgency tactics.
- **🔗 URL OSINT Scanner**: Automatically extracts URLs, detects malicious TLDs, and identifies phishing strings.

### 2. 🔊 Frequency Scan (Audio Forensics)
Powered by **Librosa** for rapid, heuristic-based signal anomaly detection:
- **F₀ Pitch Stability**: Measures the coefficient of variation in human pitch. Unnaturally stable pitch often indicates synthetic text-to-speech.
- **Spectral Flatness**: Identifies white-noise-like properties and digital aliasing typical of deepfakes.
- **RMS Energy Dynamics**: Counts natural silence gaps (breaths/pauses) vs. unnaturally flat AI energy distribution.
- **Interactive Mel-Spectrograms**: Visualizes the frequencies using an interactive 3D/2D Plotly map.

### 3. 🖼️ Visual Scan (Image Forensics)
Extracts embedded metadata to determine image authenticity:
- **Camera Configuration & GPS**: Locates physical capture origin and device signatures.
- **Forgery Detection**: Detects signatures of known editing software (Photoshop, GIMP) and leading AI Image Generators (Midjourney, DALL-E, Stable Diffusion).
- **Metadata Completeness Scoring**: AI-generated images typically show 0% completeness due to a lack of authentic EXIF data.

### 4. 🌐 Network Scan (IP & Infrastructure Forensics)
Tracing infrastructure anonymity to expose scam operations:
- **Node Tracing**: Resolve unknown domains or IP addresses.
- **Anonymity Detection**: Automatically flags if the target is hiding behind a **VPN, Proxy, Tor Node**, or Datacenter/Cloud Hosting.
- **Global Radar Map**: Visualizes the physical server location on an interactive 3D orthographic globe.

### 5. 📁 Case Archives & Security Dashboard
- **Local SQLite Integration**: Every single scan (Text, Audio, Image, Network) is automatically securely persisted in a local database.
- **Live Security Dashboard**: Sidebar displays live statistics (total cases, anomalies detected, moving average scores).
- **Export Capabilities**: Download full JSON forensic audit reports for any investigation.

### 6. 🎓 Awareness Hub
An educational dashboard built directly into the app that natively explains the forensic heuristics and methodology behind the AI's conclusions. Perfect for bridging the gap between developers and non-technical juries/users.

---

## 🛠️ Architecture & Aesthetics
- **Theme**: Custom CSS injected for a Cyber-Noir "hacker" style (Deep black backgrounds, Neon Blue/Red/Green accents, and Monospace fonts).
- **Caching**: Heavy calculations (like Librosa Audio processing) use `@st.cache_data` to ensure an incredibly fluid UX when switching between dashboards.
- **Resilient AI**: Communication with Gemini uses **Strict Schema Mime-Types** to enforce programmatic reliability. Custom Cyber-Noir error handling masks API timeouts or Rate Limits from the end-user.

---

## 💻 Requirements & Setup

1. **Python 3.10+** (Recommended)
2. Clone this repository and navigate to the project root.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **API Keys**:
   - Copy `.env.example` to a new file named `.env`.
   - Add your [Google AI Studio](https://aistudio.google.com/app/apikey) API key for Gemini.
   ```env
   GOOGLE_API_KEY="your_api_key_here"
   ```

---

## ⚡ Running the Application

Execute the Streamlit entry script:
```bash
streamlit run app.py
```
*The forensic terminal will securely operate locally at `http://localhost:8501`.*

---

<div align="center">
  <p><i>"Veritas in machina — Truth in the machine."</i></p>
  <b>Astral-Lens</b>
</div>
