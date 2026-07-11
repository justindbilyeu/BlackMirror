"""The Archive Below – immutable scar storage with falsifiability enforcement."""

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from .config import SCAR_DB, ensure_dirs


def ensure_db():
    ensure_dirs()
    with sqlite3.connect(SCAR_DB) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS scars (
                scar_id TEXT PRIMARY KEY,
                lineage_id TEXT NOT NULL,
                break_type TEXT NOT NULL,
                the_break TEXT NOT NULL,
                the_blade TEXT NOT NULL,
                the_smith TEXT NOT NULL,
                the_nutrient TEXT NOT NULL,
                the_grain TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_lineage ON scars(lineage_id)")
        conn.commit()


def _validate_nutrient(nutrient: str) -> bool:
    if "?" not in nutrient:
        print("\n[INVALID NUTRIENT] Must be a question.")
        return False
    markers = ["is", "does", "can", "will", "how much", "what if", "under what", "which"]
    if not any(m in nutrient.lower() for m in markers):
        print("\n[WARNING] Nutrient may not be falsifiable.")
    return True


def record_scar(
    lineage_id: str,
    break_type: str,
    the_break: str,
    the_blade: str,
    the_smith: str,
    the_nutrient: str,
    the_grain: str,
) -> Optional[str]:
    """Store a new scar. Returns scar_id if valid, else None."""
    # Anti-smoothing density check
    if len(the_break) > len(the_nutrient) + len(the_grain) + len(the_blade):
        print("\n[SMOOTHING DETECTED] Record is shorter than the break. Expand nutrient or grain.")
        return None
    if not _validate_nutrient(the_nutrient):
        return None

    scar_id = str(uuid.uuid4())
    try:
        with sqlite3.connect(SCAR_DB) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO scars VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (scar_id, lineage_id, break_type, the_break, the_blade,
                  the_smith, the_nutrient, the_grain,
                  datetime.now(timezone.utc).isoformat()))
            conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"DB Error: {e}")
        return None
    return scar_id


def list_scars(lineage_id: Optional[str] = None) -> List[Tuple]:
    with sqlite3.connect(SCAR_DB) as conn:
        c = conn.cursor()
        if lineage_id:
            c.execute("SELECT * FROM scars WHERE lineage_id = ? ORDER BY timestamp", (lineage_id,))
        else:
            c.execute("SELECT * FROM scars ORDER BY timestamp DESC")
        return c.fetchall()


def get_scar(scar_id: str) -> Optional[Tuple]:
    with sqlite3.connect(SCAR_DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM scars WHERE scar_id = ?", (scar_id,))
        return c.fetchone()


def generate_prompt(lineage_id: str) -> str:
    rows = list_scars(lineage_id)
    if not rows:
        return ""
    prompt = "\n=== BLACK MIRROR INJECTION ===\n"
    prompt += "These breaks shaped this lineage. They are visible in the grain.\n\n"
    for i, row in enumerate(rows, 1):
        # row: scar_id, lineage, btype, break_text, blade, smith, nutrient, grain, ts
        prompt += f"[{i}] NUTRIENT: {row[6]}\n    GRAIN: {row[7]}\n\n"
    prompt += "=== END INJECTION ===\n"
    return prompt
