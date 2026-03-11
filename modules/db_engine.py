"""
Astral-Lens — Case Database Engine
Lightweight SQLite wrapper for forensic case logging and security dashboard stats.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "astral_forensics.db")


def _get_connection():
    """Get a database connection with WAL mode for performance."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    """Create the case_logs table if it does not exist."""
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS case_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL,
            scan_type   TEXT NOT NULL,       -- 'text', 'audio', 'image'
            input_hash  TEXT,                -- short hash of input for dedup display
            score       INTEGER,             -- primary score (reality/authenticity/metadata)
            risk_level  TEXT,                -- Low / Medium / High
            verdict     TEXT,                -- one-line verdict
            details     TEXT                 -- full JSON payload
        );
    """)
    conn.commit()
    conn.close()


def log_case(scan_type: str, score: int, risk_level: str, verdict: str,
             details: dict, input_hash: str = "") -> int:
    """
    Insert a completed scan into the case log.

    Returns the new row ID.
    """
    conn = _get_connection()
    cur = conn.execute(
        """INSERT INTO case_logs (timestamp, scan_type, input_hash, score, risk_level, verdict, details)
           VALUES (?, ?, ?, ?, ?, ?, ?);""",
        (
            datetime.now().isoformat(timespec="seconds"),
            scan_type,
            input_hash,
            score,
            risk_level,
            verdict,
            json.dumps(details, default=str),
        ),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def get_stats() -> dict:
    """
    Return aggregate dashboard statistics.

    Keys: total_scans, text_scans, audio_scans, image_scans,
          anomalies_detected (score < 50), avg_score
    """
    conn = _get_connection()
    row = conn.execute("SELECT COUNT(*) as total FROM case_logs;").fetchone()
    total = row["total"] if row else 0

    text_scans = conn.execute(
        "SELECT COUNT(*) as c FROM case_logs WHERE scan_type='text';").fetchone()["c"]
    audio_scans = conn.execute(
        "SELECT COUNT(*) as c FROM case_logs WHERE scan_type='audio';").fetchone()["c"]
    image_scans = conn.execute(
        "SELECT COUNT(*) as c FROM case_logs WHERE scan_type='image';").fetchone()["c"]
    anomalies = conn.execute(
        "SELECT COUNT(*) as c FROM case_logs WHERE score < 50;").fetchone()["c"]
    avg_row = conn.execute(
        "SELECT AVG(score) as a FROM case_logs WHERE score IS NOT NULL;").fetchone()
    avg_score = round(avg_row["a"], 1) if avg_row["a"] is not None else 0

    conn.close()
    return {
        "total_scans": total,
        "text_scans": text_scans,
        "audio_scans": audio_scans,
        "image_scans": image_scans,
        "anomalies_detected": anomalies,
        "avg_score": avg_score,
    }


def get_recent_cases(limit: int = 20) -> list[dict]:
    """Return the most recent N case log entries as dicts."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM case_logs ORDER BY id DESC LIMIT ?;", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
