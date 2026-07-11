import pytest
import tempfile
from unittest.mock import patch

from black_mirror import scar_layer


@pytest.fixture
def temp_db():
    with patch("black_mirror.scar_layer.SCAR_DB", tempfile.mktemp(suffix=".db")):
        scar_layer.ensure_db()
        yield


def test_record_valid(temp_db):
    sid = scar_layer.record_scar("test", "fracture", "The sky is blue.",
                                  "A critical observation.", "Newton",
                                  "Is the sky always blue?", "Check at dusk.")
    assert sid is not None
    rows = scar_layer.list_scars("test")
    assert len(rows) == 1


def test_record_too_short(temp_db):
    sid = scar_layer.record_scar("test", "fracture", "The sky is blue and vast.",
                                  "short", "Newton",
                                  "short", "short")
    assert sid is None


def test_record_non_falsifiable(temp_db):
    sid = scar_layer.record_scar("test", "fracture", "The sky is blue.",
                                  "A critical observation.", "Newton",
                                  "The sky is blue.", "Check at dusk.")
    assert sid is None
