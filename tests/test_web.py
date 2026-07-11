import pytest
import tempfile
from unittest.mock import patch

from black_mirror import web_layer


@pytest.fixture
def temp_web():
    with patch("black_mirror.web_layer.WEB_DB", tempfile.mktemp(suffix=".db")):
        web_layer.ensure_db()
        yield


def test_add_node(temp_web):
    nid = web_layer.add_node("hypothesis", "All swans are white.")
    assert nid is not None
    nodes, _ = web_layer.get_graph()
    assert len(nodes) == 1


def test_add_edge(temp_web):
    a = web_layer.add_node("observation", "A black swan exists.")
    b = web_layer.add_node("hypothesis", "All swans are white.")
    eid = web_layer.add_edge(a, b, "contradicts")
    assert eid is not None
    _, edges = web_layer.get_graph()
    assert len(edges) == 1


def test_confidence_propagation(temp_web):
    claim = web_layer.add_node("claim", "Gravity exists.", confidence=1.0)
    obs = web_layer.add_node("observation", "An apple falls.")
    web_layer.add_edge(obs, claim, "constrains")
    nodes, _ = web_layer.get_graph()
    # confidence should have decayed to 0.9
    assert nodes[claim][2] == 0.9
