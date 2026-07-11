"""Configuration and database paths."""

import os

SCAR_DB = os.path.expanduser("~/.black_mirror/scars.db")
WEB_DB = os.path.expanduser("~/.black_mirror/evidence_web.db")


def ensure_dirs():
    os.makedirs(os.path.dirname(SCAR_DB), exist_ok=True)
    os.makedirs(os.path.dirname(WEB_DB), exist_ok=True)
