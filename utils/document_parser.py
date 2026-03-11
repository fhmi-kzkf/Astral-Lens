"""
Astral-Lens — Document Parser Utilities
Extract raw text from uploaded PDF and TXT files for forensic analysis.
"""

import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF file.

    Parameters
    ----------
    file_bytes : bytes
        Raw PDF file bytes.

    Returns
    -------
    str
        Extracted text content, or an error message.
    """
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages_text.append(text.strip())

        if not pages_text:
            return "[ERROR] PDF contains no extractable text (may be image-only)."

        return "\n\n".join(pages_text)

    except ImportError:
        return "[ERROR] PyPDF2 is not installed. Run: pip install PyPDF2"
    except Exception as e:
        return f"[ERROR] Failed to parse PDF: {str(e)}"


def extract_text_from_txt(file_bytes: bytes) -> str:
    """
    Decode a plain-text file from bytes.

    Parameters
    ----------
    file_bytes : bytes
        Raw file bytes.

    Returns
    -------
    str
        Decoded text content.
    """
    # Try common encodings
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            return file_bytes.decode(encoding)
        except (UnicodeDecodeError, AttributeError):
            continue

    return "[ERROR] Unable to decode text file."


def parse_uploaded_document(file_bytes: bytes, file_name: str) -> str:
    """
    Route a file to the appropriate parser based on extension.

    Parameters
    ----------
    file_bytes : bytes
        Raw file bytes.
    file_name : str
        Original filename.

    Returns
    -------
    str
        Extracted text content.
    """
    name_lower = file_name.lower()

    if name_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif name_lower.endswith(".txt"):
        return extract_text_from_txt(file_bytes)
    else:
        return f"[ERROR] Unsupported file type: {file_name}"
