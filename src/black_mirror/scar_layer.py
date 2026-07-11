"""The Archive Below – immutable scar storage with falsifiability enforcement."""

import difflib
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from .config import SCAR_DB, ensure_dirs

# Auxiliary/modal verbs and comparators a genuinely testable prediction tends to
# use. Matched as whole words, not substrings — "canary" must not satisfy "can".
_FALSIFIABLE_MARKERS = [
    "is", "are", "was", "were", "does", "do", "did", "can", "could",
    "will", "would", "should", "must", "has", "have",
    "how much", "how many", "what if", "under what", "which", "when", "where",
    "before", "after", "within", "at least", "more than", "less than",
    "exceeds", "fails to",
]

# A nutrient/grain/blade this similar to the break it's supposedly compressing
# is a copy, not a compression — the density check exists to require the
# latter, and copying the break's own words trivially inflates length.
_COPY_SIMILARITY_THRESHOLD = 0.9


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
    lowered = nutrient.lower()
    if not any(re.search(rf"\b{re.escape(m)}\b", lowered) for m in _FALSIFIABLE_MARKERS):
        print("\n[INVALID NUTRIENT] Doesn't read as a testable prediction "
              "(no auxiliary verb or comparator — e.g. is/does/can/will/before/more than).")
        return False
    return True


def _is_padding(text: str) -> bool:
    """True if text looks like filler rather than real content."""
    stripped = text.strip()
    if not stripped:
        return True
    # A field that's just one or two characters repeated, e.g. "................"
    if len(stripped) > 8 and len(set(stripped.replace(" ", ""))) <= 2:
        return True
    words = stripped.split()
    if len(words) >= 4:
        unique_ratio = len(set(w.lower() for w in words)) / len(words)
        if unique_ratio < 0.4:
            return True
    return False


def _is_copy_of_break(field: str, the_break: str) -> bool:
    ratio = difflib.SequenceMatcher(None, field.strip().lower(), the_break.strip().lower()).ratio()
    return ratio >= _COPY_SIMILARITY_THRESHOLD


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
    # Anti-smoothing density check, by word count rather than raw characters —
    # padding a field with repeated characters shouldn't satisfy this.
    break_words = len(the_break.split())
    record_words = len(the_blade.split()) + len(the_nutrient.split()) + len(the_grain.split())
    if record_words < break_words:
        print("\n[SMOOTHING DETECTED] Record is shorter than the break. Expand nutrient or grain.")
        return None
    if any(_is_padding(f) for f in (the_blade, the_nutrient, the_grain)):
        print("\n[SMOOTHING DETECTED] Blade/nutrient/grain looks like padding, not real content.")
        return None
    if _is_copy_of_break(the_nutrient, the_break):
        print("\n[SMOOTHING DETECTED] Nutrient is nearly identical to the break — compress it, don't copy it.")
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
