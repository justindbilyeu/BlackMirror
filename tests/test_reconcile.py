import pytest
import tempfile
from unittest.mock import patch

from black_mirror import web_layer, reconcile


@pytest.fixture
def temp_web():
    with patch("black_mirror.web_layer.WEB_DB", tempfile.mktemp(suffix=".db")):
        web_layer.ensure_db()
        yield


def test_reconcile_grounded_path(temp_web, capsys):
    obs = web_layer.add_node("observation", "The model failed at negation.")
    anomaly = web_layer.add_node("anomaly", "Negation failure anomaly.")
    claim = web_layer.add_node("claim", "Does the model understand negation?")
    web_layer.add_edge(obs, anomaly, "derives_from")
    web_layer.add_edge(anomaly, claim, "constrains")

    reconcile.reconcile(claim)
    out = capsys.readouterr().out
    assert "Grounded" in out
    assert "SMOOTHING DETECTED" not in out


def test_reconcile_ungrounded(temp_web, capsys):
    claim = web_layer.add_node("claim", "An isolated claim with no evidence.")

    reconcile.reconcile(claim)
    out = capsys.readouterr().out
    assert "ungrounded" in out.lower()


def test_reconcile_smoothing_detected(temp_web, capsys):
    obs = web_layer.add_node("observation", "Something was observed.")
    claim = web_layer.add_node("claim", "A claim with no anomaly in between?")
    web_layer.add_edge(obs, claim, "supports")

    reconcile.reconcile(claim)
    out = capsys.readouterr().out
    assert "SMOOTHING DETECTED" in out
