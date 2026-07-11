"""The Evidence Web – constraint network with confidence propagation."""

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict

from .config import WEB_DB, ensure_dirs


def ensure_db():
    ensure_dirs()
    with sqlite3.connect(WEB_DB) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                edge_id TEXT PRIMARY KEY,
                from_node TEXT NOT NULL,
                to_node TEXT NOT NULL,
                edge_type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (from_node) REFERENCES nodes(node_id),
                FOREIGN KEY (to_node) REFERENCES nodes(node_id)
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_from ON edges(from_node)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_to ON edges(to_node)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_node_type ON nodes(node_type)")
        conn.commit()


def add_node(node_type: str, content: str, node_id: Optional[str] = None,
             confidence: float = 1.0) -> Optional[str]:
    nid = node_id or str(uuid.uuid4())
    try:
        with sqlite3.connect(WEB_DB) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO nodes VALUES (?, ?, ?, ?, ?, ?)
            """, (nid, node_type, content, confidence,
                  datetime.now(timezone.utc).isoformat(), None))
            conn.commit()
    except sqlite3.IntegrityError:
        print(f"Node {nid} already exists.")
        return None
    return nid


def add_edge(from_node: str, to_node: str, edge_type: str,
             weight: float = 1.0, propagate: bool = True) -> Optional[str]:
    with sqlite3.connect(WEB_DB) as conn:
        c = conn.cursor()
        c.execute("SELECT node_id FROM nodes WHERE node_id IN (?, ?)", (from_node, to_node))
        if len(c.fetchall()) < 2:
            print("One or both nodes missing.")
            return None
        eid = str(uuid.uuid4())
        c.execute("""
            INSERT INTO edges VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (eid, from_node, to_node, edge_type, weight,
              datetime.now(timezone.utc).isoformat(), None))
        conn.commit()

    if propagate and edge_type == "constrains":
        with sqlite3.connect(WEB_DB) as conn:
            c = conn.cursor()
            c.execute("UPDATE nodes SET confidence = confidence * 0.9 WHERE node_id = ?", (to_node,))
            conn.commit()
    return eid


def get_graph() -> Tuple[Dict[str, Tuple[str, str, float]], List[Tuple[str, str, str]]]:
    with sqlite3.connect(WEB_DB) as conn:
        c = conn.cursor()
        c.execute("SELECT node_id, node_type, content, confidence FROM nodes")
        nodes = {row[0]: (row[1], row[2], row[3]) for row in c.fetchall()}
        c.execute("SELECT from_node, to_node, edge_type FROM edges")
        edges = c.fetchall()
        return nodes, edges


def get_constraints(claim_id: str) -> List[Tuple]:
    with sqlite3.connect(WEB_DB) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT n.node_id, n.node_type, n.content, e.weight, e.edge_type
            FROM nodes n JOIN edges e ON n.node_id = e.from_node
            WHERE e.to_node = ? AND e.edge_type IN ('constrains','supports','contradicts')
            ORDER BY e.weight DESC
        """, (claim_id,))
        return c.fetchall()


def get_falsifiers(hyp_id: str) -> List[Tuple]:
    with sqlite3.connect(WEB_DB) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT n.node_id, n.node_type, n.content
            FROM nodes n JOIN edges e ON n.node_id = e.from_node
            WHERE e.to_node = ? AND e.edge_type IN ('contradicts','falsifies')
        """, (hyp_id,))
        direct = c.fetchall()
        c.execute("""
            SELECT n.node_id, n.node_type, n.content
            FROM nodes n JOIN edges e ON n.node_id = e.from_node
            WHERE e.to_node = ? AND n.node_type = 'anomaly'
        """, (hyp_id,))
        anomalies = c.fetchall()
        return list(set(direct + anomalies))
