"""
Astral-Lens — Image Forensic Engine
EXIF metadata extraction and forgery indicator analysis using Pillow.
"""

from PIL import Image, ExifTags
import io
import hashlib


# ── Known editing software signatures ────────────────────────────────────────

EDITOR_SIGNATURES = [
    "adobe", "photoshop", "gimp", "canva", "lightroom", "snapseed",
    "picsart", "pixlr", "affinity", "capture one", "darktable",
    "paint.net", "corel", "figma", "sketch",
]

AI_GENERATOR_SIGNATURES = [
    "dall-e", "midjourney", "stable diffusion", "firefly", "ideogram",
    "leonardo", "playground", "nightcafe", "deepai", "craiyon",
    "bing image creator", "copilot", "imagen", "flux",
]

ORGANIC_SIGNATURES = [
    "windows", "apple", "android", "samsung", "huawei", "xiaomi", 
    "oppo", "vivo", "motorola", "mediatek", "google", "oneplus"
]


def _extract_exif(image: Image.Image) -> dict:
    """Extract human-readable EXIF data from a PIL Image."""
    exif_data = image.getexif()
    if not exif_data:
        return {}

    readable = {}
    for tag_id, value in exif_data.items():
        tag_name = ExifTags.TAGS.get(tag_id, f"Unknown_{tag_id}")
        # Convert bytes to string representation
        if isinstance(value, bytes):
            try:
                value = value.decode("utf-8", errors="replace")
            except Exception:
                value = str(value)
        
        # Sanitize string of trailing null bytes (\x00) inserted by cheap camera firmwares
        if isinstance(value, str):
            value = value.replace("\x00", "").strip()
            
        readable[tag_name] = str(value)

    return readable


def _check_gps(exif: dict) -> dict:
    """Check for GPS data presence in EXIF."""
    gps_keys = [k for k in exif if "gps" in k.lower()]
    has_gps = len(gps_keys) > 0
    return {
        "has_gps": has_gps,
        "gps_fields_found": gps_keys if has_gps else [],
        "detail": "GPS geolocation data found — image was taken by a physical device."
                  if has_gps else "No GPS data — image may be a screenshot, download, or AI-generated.",
    }


def _check_camera(exif: dict) -> dict:
    """Check for camera/device metadata."""
    make = exif.get("Make", "")
    model = exif.get("Model", "")
    software = exif.get("Software", "")
    datetime_orig = exif.get("DateTimeOriginal", exif.get("DateTime", ""))

    has_camera = bool(make or model)
    return {
        "has_camera_info": has_camera,
        "make": make or "N/A",
        "model": model or "N/A",
        "software": software or "N/A",
        "datetime_original": datetime_orig or "N/A",
        "detail": f"Camera: {make} {model}" if has_camera else "No camera info — not taken by a physical device.",
    }


def _check_editing(exif: dict) -> dict:
    """Check for signs of image editing or AI generation."""
    software = exif.get("Software", "").lower()
    processing = exif.get("ImageProcessingSoftware", exif.get("ProcessingSoftware", "")).lower()
    combined = software + " " + processing

    # Check for signatures
    editors_found = [sig for sig in EDITOR_SIGNATURES if sig in combined]
    ai_found = [sig for sig in AI_GENERATOR_SIGNATURES if sig in combined]
    organic_found = [sig for sig in ORGANIC_SIGNATURES if sig in combined]

    # AI is absolute priority
    if ai_found:
        verdict = f"⚠ AI GENERATOR DETECTED — {', '.join(ai_found).upper()}"
        score = 10
    elif editors_found:
        verdict = f"⚡ EDITING SOFTWARE — {', '.join(editors_found).upper()}"
        score = 40
    elif organic_found:
        # Standard OS or Mobile handler (e.g. Windows, MediaTek, Samsung)
        verdict = f"✓ ORGANIC HANDLER — {', '.join(organic_found).capitalize()}"
        score = 90
    elif software:
        verdict = f"Software: {software}"
        score = 60 # Unrecognized software, slight suspicion but not necessarily an editor
    else:
        verdict = "No software metadata found"
        score = 50  # Neutral — could be stripped

    return {
        "editors_detected": editors_found,
        "ai_generators_detected": ai_found,
        "organic_handlers_detected": organic_found,
        "software_tag": exif.get("Software", "N/A").replace("\x00", "").strip(),
        "score": score,
        "verdict": verdict,
    }


def _assess_metadata_completeness(exif: dict) -> dict:
    """
    Score how complete the metadata is.
    Real photos from cameras have rich EXIF; AI/screenshots have none.
    """
    key_fields = [
        "Make", "Model", "DateTime", "DateTimeOriginal",
        "ExposureTime", "FNumber", "ISOSpeedRatings",
        "FocalLength", "Flash", "WhiteBalance",
    ]
    present = [f for f in key_fields if f in exif]
    
    # Many smartphones only save 3-5 fields. We shouldn't punish them for missing 'Flash'.
    num_fields = len(present)

    if num_fields >= 3:
        # 3+ fields (e.g., Make, Model, DateTime) implies standard smartphone config
        completeness = min(100.0, (num_fields / 4.0) * 100) 
        verdict = "✓ RICH METADATA — Consistent with authentic camera capture"
        risk = "Low"
    elif num_fields == 2:
        completeness = 50.0
        verdict = "⚡ PARTIAL METADATA — Some fields stripped or missing"
        risk = "Medium"
    elif num_fields == 1:
        completeness = 25.0
        verdict = "⚠ SPARSE METADATA — Most camera fields are absent"
        risk = "High"
    else:
        completeness = 0.0
        verdict = "⚠ NO METADATA — Fields stripped (Social Media transfer) or heavily processed"
        risk = "High"

    return {
        "completeness_pct": round(completeness, 1),
        "fields_present": present,
        "fields_missing": [f for f in key_fields if f not in exif],
        "risk_level": risk,
        "verdict": verdict,
    }


def run_image_forensics(image_bytes: bytes, file_name: str) -> dict:
    """
    Full forensic pipeline for an uploaded image file.

    Parameters
    ----------
    image_bytes : bytes
        Raw image file bytes.
    file_name : str
        Original filename.

    Returns
    -------
    dict with keys: exif_raw, gps, camera, editing, completeness,
                    authenticity_score, verdict, file_info
    """
    img = Image.open(io.BytesIO(image_bytes))
    exif = _extract_exif(img)

    gps = _check_gps(exif)
    camera = _check_camera(exif)
    editing = _check_editing(exif)
    completeness = _assess_metadata_completeness(exif)

    # ── Composite Authenticity Score ──────────────────────────────────────
    # Weighted: completeness 40%, editing 30%, camera 15%, GPS 15%
    cam_score = 90 if camera["has_camera_info"] else 20
    gps_score = 90 if gps["has_gps"] else 25

    authenticity = int(
        completeness["completeness_pct"] * 0.40
        + editing["score"] * 0.30
        + cam_score * 0.15
        + gps_score * 0.15
    )
    
    # ── HARD LOGIC CAPPING ──
    # 1. AI Generative Kill-Switch
    if editing["score"] <= 10 or len(editing.get("ai_generators_detected", [])) > 0:
        authenticity = 10
    
    # 2. Stripped Metadata Buffer (Social media screenshots)
    # If there's truly NO metadata, but we also DID NOT explicitly find AI editors, 
    # it shouldn't score an abysmal 21. It should sit near 45 (Inconclusive) because it's just blank.
    elif completeness["completeness_pct"] == 0.0 and authenticity < 45:
        authenticity = 45
        
    authenticity = min(max(authenticity, 0), 100)

    if authenticity >= 70:
        overall = "✓ LIKELY AUTHENTIC — Metadata consistent with genuine physical capture"
    elif authenticity > 40:
        overall = "⚡ INCONCLUSIVE — Metadata is partially stripped, modified, or saved via App"
    else:
        overall = "⚠ SUSPICIOUS — Severe metadata discrepancies or explicit Generative AI signatures flagged"

    # Risk level
    if authenticity >= 70:
        risk_level = "Low"
    elif authenticity >= 40:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # File info
    img_hash = hashlib.md5(image_bytes[:4096]).hexdigest()[:12]

    return {
        "exif_raw": exif,
        "gps": gps,
        "camera": camera,
        "editing": editing,
        "completeness": completeness,
        "authenticity_score": authenticity,
        "verdict": overall,
        "risk_level": risk_level,
        "file_info": {
            "name": file_name,
            "format": img.format or "Unknown",
            "size_pixels": f"{img.width}x{img.height}",
            "mode": img.mode,
            "hash": img_hash,
        },
    }
