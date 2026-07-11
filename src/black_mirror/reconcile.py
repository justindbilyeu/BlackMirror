"""Reconciliation engine – trace hypotheses to observations, detect smoothing."""

from collections import deque

from .web_layer import get_graph


def reconcile(hypothesis_id: str) -> None:
    nodes, edges = get_graph()
    if hypothesis_id not in nodes:
        print(f"Hypothesis {hypothesis_id} not found.")
        return

    # Edges point from evidence toward what it constrains (e.g. anomaly -> claim),
    # so tracing a hypothesis back to its evidence means walking edges in reverse.
    adj = {}
    for f, t, _ in edges:
        adj.setdefault(t, []).append(f)

    visited = {hypothesis_id}
    q = deque([(hypothesis_id, [hypothesis_id])])
    paths_to_obs = []
    paths_to_anomaly = []

    while q:
        node, path = q.popleft()
        ntype, content, _ = nodes.get(node, (None, None, None))

        if ntype == "observation":
            paths_to_obs.append((path, node))
        if ntype == "anomaly":
            paths_to_anomaly.append((path, node))

        for nb in adj.get(node, []):
            if nb not in visited:
                visited.add(nb)
                q.append((nb, path + [nb]))

    print(f"\n{'='*60}")
    print(f"RECONCILIATION REPORT for {hypothesis_id}")
    print(f"Hypothesis: {nodes[hypothesis_id][1][:80]}")
    print(f"{'='*60}")

    if not paths_to_obs:
        print("\n[!] This hypothesis reaches NO observations. It is ungrounded.")
        return

    anomaly_set = {nid for _, nid in paths_to_anomaly}
    floating = []
    grounded = []
    for path, obs_id in paths_to_obs:
        if any(n in anomaly_set for n in path):
            grounded.append(path)
        else:
            floating.append(path)

    if floating:
        print("\n[SMOOTHING DETECTED] Paths to observation without passing through an anomaly:")
        for p in floating[:3]:
            print("  " + " -> ".join(p))
        print("\n   Reality is being interpreted without friction. Add an anomaly.")
    else:
        print("\n[✓] All paths to observations pass through anomalies. Grounded.")

    if grounded:
        print(f"\n[✓] {len(grounded)} grounded paths found.")
        for p in grounded[:2]:
            print("  " + " -> ".join(p))
