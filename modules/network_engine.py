"""
Astral-Lens — Network Forensic Engine
IP/Domain geolocation and infrastructure anonymity detection.
"""

import requests
import socket
from urllib.parse import urlparse
import plotly.graph_objects as go

def _extract_domain(target: str) -> str:
    """Clean the target to get just the domain or IP."""
    target = target.strip()
    if target.startswith("http"):
        parsed = urlparse(target)
        return parsed.netloc.split(":")[0]  # remove port if present
    # Remove trailing slashes and paths if user pastes without http
    return target.split("/")[0].split(":")[0]

def run_network_forensics(target: str) -> dict:
    """
    Perform a trace on a domain or IP address using ip-api.com.
    
    Parameters
    ----------
    target : str
        Domain name (e.g., 'scam.xyz') or IP address.
        
    Returns
    -------
    dict with trace information and plotly map figure.
    """
    clean_target = _extract_domain(target)
    
    if not clean_target:
        return {"error": "Invalid target format. Please provide a valid domain or IP."}
        
    # Free API endpoint, supports domains and IPs
    # Fields: status, country, regionName, city, lat, lon, isp, org, as, proxy, hosting, query
    endpoint = f"http://ip-api.com/json/{clean_target}?fields=status,message,country,regionName,city,lat,lon,isp,org,as,proxy,hosting,query"
    
    try:
        response = requests.get(endpoint, timeout=10)
        data = response.json()
        
        if data.get("status") == "fail":
            return {"error": f"Trace failed: {data.get('message', 'Unknown error')} for {clean_target}"}
            
    except Exception as e:
        return {"error": f"Network uplink severed. Failed to reach trace API: {str(e)}"}

    # ── Analyze Infrastructure Anonymity ──
    is_proxy = data.get("proxy", False)
    is_hosting = data.get("hosting", False)
    
    # Calculate Risk Score
    risk_score = 10  # Base risk
    anonymity_flags = []
    
    if is_proxy:
        risk_score += 60
        anonymity_flags.append("VPN/Proxy Detected")
    if is_hosting:
        risk_score += 30
        anonymity_flags.append("Datacenter/Cloud Hosting (suspect for end-user IP)")
        
    # High risk for specific countries known for bulletproof hosting or scams
    # (Simplified heuristic for demo purposes)
    high_risk_countries = ["Russia", "China", "Nigeria", "Cyprus", "Panama", "Seychelles", "Belize"]
    if data.get("country") in high_risk_countries:
        risk_score += 20
        anonymity_flags.append(f"Jurisdiction Risk: {data.get('country')}")
        
    risk_score = min(risk_score, 100)
    
    if risk_score >= 80:
        verdict = "⚠ MALICIOUS INFRASTRUCTURE — Active evasion techniques detected"
        risk_level = "High"
    elif risk_score >= 40:
        verdict = "⚡ SUSPICIOUS INFRASTRUCTURE — Hosting or regional anomalies found"
        risk_level = "Medium"
    else:
        verdict = "✓ STANDARD INFRASTRUCTURE — No obvious active evasion detected"
        risk_level = "Low"

    # ── Generate Global Radar Map ──
    try:
        lat = data.get("lat", 0)
        lon = data.get("lon", 0)
        
        fig = go.Figure(go.Scattergeo(
            lon=[lon],
            lat=[lat],
            mode='markers+text',
            text=[clean_target],
            textposition="top center",
            marker=dict(
                size=12,
                color="#ef4444" if risk_level == "High" else "#f59e0b" if risk_level == "Medium" else "#10b981",
                line=dict(width=2, color="#ffffff"),
                symbol="circle"
            ),
            textfont=dict(color="#3b82f6", family="Roboto Mono", size=12)
        ))

        fig.update_layout(
            geo=dict(
                scope='world',
                projection_type='orthographic',
                showland=True,
                landcolor='rgba(26,26,26,1)',
                showocean=True,
                oceancolor='rgba(5,5,5,1)',
                showcountries=True,
                countrycolor='rgba(59,130,246,0.3)',
                bgcolor='rgba(0,0,0,0)',
                center=dict(lat=lat, lon=lon),
                projection_scale=2.5
            ),
            paper_bgcolor="#050505",
            plot_bgcolor="#050505",
            margin=dict(l=0, r=0, t=0, b=0),
            height=400,
        )
    except Exception:
        fig = None

    return {
        "target": clean_target,
        "ip_address": data.get("query"),
        "location": f"{data.get('city', 'Unknown')}, {data.get('regionName', 'Unknown')}, {data.get('country', 'Unknown')}",
        "isp": data.get("isp", "Unknown"),
        "organization": data.get("org", "Unknown"),
        "asn": data.get("as", "Unknown"),
        "is_proxy": is_proxy,
        "is_hosting": is_hosting,
        "anonymity_flags": anonymity_flags,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "verdict": verdict,
        "map_figure": fig
    }
