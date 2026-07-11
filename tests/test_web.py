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


def test_add_node_rejects_invalid_type(temp_web):
    nid = web_layer.add_node("not_a_real_type", "Some content.")
    assert nid is None
    nodes, _ = web_layer.get_graph()
    assert len(nodes) == 0


def test_add_edge_rejects_invalid_type(temp_web):
    a = web_layer.add_node("observation", "A.")
    b = web_layer.add_node("hypothesis", "B.")
    eid = web_layer.add_edge(a, b, "not_a_real_edge")
    assert eid is None
    _, edges = web_layer.get_graph()
    assert len(edges) == 0


def test_shortest_path_found(temp_web):
    a = web_layer.add_node("observation", "A.")
    b = web_layer.add_node("anomaly", "B.")
    c = web_layer.add_node("claim", "C.")
    web_layer.add_edge(a, b, "derives_from")
    web_layer.add_edge(b, c, "constrains")

    path = web_layer.shortest_path(a, c)
    assert path == [a, b, c]


def test_shortest_path_not_found(temp_web):
    a = web_layer.add_node("observation", "A.")
    b = web_layer.add_node("claim", "B.")

    assert web_layer.shortest_path(a, b) is None


def test_find_cycles_none(temp_web):
    a = web_layer.add_node("observation", "A.")
    b = web_layer.add_node("claim", "B.")
    web_layer.add_edge(a, b, "constrains")

    assert web_layer.find_cycles() == []


def test_find_cycles_detects_cycle(temp_web):
    a = web_layer.add_node("claim", "A.")
    b = web_layer.add_node("claim", "B.")
    web_layer.add_edge(a, b, "supports")
    web_layer.add_edge(b, a, "supports")

    cycles = web_layer.find_cycles()
    assert len(cycles) == 1
    assert cycles[0][0] == cycles[0][-1]


def test_get_outgoing(temp_web):
    a = web_layer.add_node("anomaly", "A.")
    b = web_layer.add_node("claim", "B.")
    web_layer.add_edge(a, b, "constrains")

    outgoing = web_layer.get_outgoing(a)
    assert len(outgoing) == 1
    assert outgoing[0][0] == b
    assert outgoing[0][3] == "constrains"
