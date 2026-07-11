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


def test_record_rejects_substring_only_marker_match(temp_db):
    # "canary" contains "can" and "This" contains "is" as substrings, but
    # neither is a real auxiliary verb — must be rejected, not pattern-matched.
    sid = scar_layer.record_scar(
        "test", "fracture", "Assumed the config file existed.",
        "It crashed on a clean checkout.", "ci",
        "This canary situation warrants scrutiny?",
        "Check config existence before reading it every time.",
    )
    assert sid is None


def test_record_rejects_repeated_character_padding(temp_db):
    sid = scar_layer.record_scar(
        "test", "fracture", "Claimed the deploy succeeded without checking health.",
        "." * 48, "x", "." * 47 + "?", "." * 48,
    )
    assert sid is None


def test_record_rejects_repeated_word_padding(temp_db):
    sid = scar_layer.record_scar(
        "test", "fracture", "Assumed the retry logic was idempotent.",
        "filler filler filler filler filler filler", "x",
        "filler filler filler filler filler filler?",
        "filler filler filler filler filler filler",
    )
    assert sid is None


def test_record_rejects_nutrient_copied_from_break(temp_db):
    sid = scar_layer.record_scar(
        "test", "fracture",
        "The agent claimed the tests passed without running them.",
        "A rerun showed three failures.", "reviewer",
        "The agent claimed the tests passed without running them?",
        "Always run tests before claiming they pass, every time.",
    )
    assert sid is None
