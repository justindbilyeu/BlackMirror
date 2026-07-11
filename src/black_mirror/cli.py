"""Unified CLI for BlackMirror."""

import argparse
import sys
import sqlite3
import textwrap
import uuid

from . import scar_layer, web_layer, reconcile, viz
from .models import BreakType


def interactive_record():
    print("\n" + "=" * 60)
    print("BLACK MIRROR — RECORD A BREAK")
    print("=" * 60)
    print("You cannot leave until you document what broke.\n")

    lineage = input("Lineage ID (or Enter for new): ").strip()
    if not lineage:
        lineage = str(uuid.uuid4())
        print(f"Generated: {lineage}")

    print("\nBreak Type:")
    for i, bt in enumerate(BreakType, 1):
        print(f"  {i}. {bt.value} — {bt.name.replace('_', ' ').title()}")
    while True:
        try:
            choice = int(input("Select (1-4): "))
            btype = list(BreakType)[choice - 1].value
            break
        except (ValueError, IndexError):
            print("Invalid.")

    print("\nTHE BREAK: (blank line to finish)")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    the_break = "\n".join(lines)
    if not the_break:
        print("Aborted.")
        return

    the_blade = input("\nTHE BLADE: ").strip()
    while not the_blade:
        the_blade = input("Blade cannot be empty: ").strip()

    the_smith = input("\nTHE SMITH: ").strip() or "unknown"

    the_nutrient = input("\nTHE NUTRIENT (falsifiable question): ").strip()
    while not scar_layer._validate_nutrient(the_nutrient):
        the_nutrient = input("Re-enter nutrient: ").strip()

    the_grain = input("\nTHE GRAIN: ").strip()
    while not the_grain:
        the_grain = input("Grain cannot be empty: ").strip()

    scar_id = scar_layer.record_scar(lineage, btype, the_break, the_blade,
                                      the_smith, the_nutrient, the_grain)
    if scar_id:
        print(f"\n[✓] SCAR RECORDED: {scar_id}")
        print("The break has been metabolized.")


def record_auto(lineage: str, btype: str, the_break: str, the_blade: str,
                 the_smith: str, the_nutrient: str, the_grain: str):
    scar_id = scar_layer.record_scar(lineage, btype, the_break, the_blade,
                                      the_smith, the_nutrient, the_grain)
    if scar_id:
        print(f"Scar recorded: {scar_id}")


def show_scar(scar_id: str):
    row = scar_layer.get_scar(scar_id)
    if not row:
        print(f"Scar {scar_id} not found.")
        return

    sid, lineage, btype, break_text, blade, smith, nutrient, grain, ts = row
    print("\n" + "=" * 60)
    print(f"SCAR RECORD: {sid}")
    print("=" * 60)
    print(f"Lineage:    {lineage}")
    print(f"Type:       {btype}")
    print(f"Timestamp:  {ts}")
    print(f"Smith:      {smith}")
    print("-" * 60)
    print("THE BREAK:")
    print(textwrap.fill(break_text, width=60))
    print("-" * 60)
    print("THE BLADE:")
    print(textwrap.fill(blade, width=60))
    print("-" * 60)
    print("THE NUTRIENT:")
    print(textwrap.fill(nutrient, width=60))
    print("-" * 60)
    print("THE GRAIN:")
    print(textwrap.fill(grain, width=60))
    print("=" * 60)


def ingest_scar(scar_id: str):
    row = scar_layer.get_scar(scar_id)
    if not row:
        print(f"Scar {scar_id} not found.")
        return

    sid, lineage, btype, break_text, blade, smith, nutrient, grain, ts = row

    # Get or create lineage node
    with sqlite3.connect(web_layer.WEB_DB) as conn:
        c = conn.cursor()
        c.execute("SELECT node_id FROM nodes WHERE node_type='lineage' AND content=?", (lineage,))
        existing = c.fetchone()
        lineage_node = existing[0] if existing else web_layer.add_node("lineage", lineage)

    observation_id = web_layer.add_node("observation", break_text)
    anomaly_id = web_layer.add_node("anomaly", f"[{btype}] {break_text[:100]}")
    claim_id = web_layer.add_node("claim", nutrient)

    if observation_id and anomaly_id and claim_id and lineage_node:
        web_layer.add_edge(observation_id, anomaly_id, "derives_from")
        web_layer.add_edge(anomaly_id, claim_id, "constrains")
        if btype == "smoothing":
            web_layer.add_edge(anomaly_id, claim_id, "smoothed_over")
        web_layer.add_edge(anomaly_id, lineage_node, "derives_from")
        web_layer.add_edge(claim_id, lineage_node, "derives_from")
        blade_node = web_layer.add_node("source", f"Blade: {blade[:80]}")
        if blade_node:
            web_layer.add_edge(blade_node, anomaly_id, "derives_from")
        print(f"\n[✓] Scar {scar_id} metabolized.")
        print(f"    Observation: {observation_id}")
        print(f"    Anomaly: {anomaly_id}")
        print(f"    Constraint: {claim_id}")
    else:
        print("Ingestion failed.")


def main():
    parser = argparse.ArgumentParser(
        description="BLACK MIRROR — The Epistemic Operating System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Initialise both databases")
    subparsers.add_parser("record", help="Record a new break interactively")
    subparsers.add_parser("list", help="List all scars")

    auto_parser = subparsers.add_parser("record-auto", help="Record a scar non-interactively")
    auto_parser.add_argument("--lineage", default="default")
    auto_parser.add_argument("--type", choices=[b.value for b in BreakType], required=True)
    auto_parser.add_argument("--break", dest="the_break", required=True)
    auto_parser.add_argument("--blade", required=True)
    auto_parser.add_argument("--smith", default="unknown")
    auto_parser.add_argument("--nutrient", required=True)
    auto_parser.add_argument("--grain", required=True)

    show_parser = subparsers.add_parser("show", help="Show a single scar")
    show_parser.add_argument("scar_id")

    ingest = subparsers.add_parser("ingest", help="Metabolise a scar into the web")
    ingest.add_argument("scar_id")

    web = subparsers.add_parser("web", help="Show the evidence web")
    web.add_argument("--claim", help="Focus on a specific claim")

    viz_parser = subparsers.add_parser("viz", help="Generate Graphviz DOT file")
    viz_parser.add_argument("--output", required=True)

    rec_parser = subparsers.add_parser("reconcile", help="Check if a hypothesis is grounded")
    rec_parser.add_argument("hypothesis_id")

    ref_parser = subparsers.add_parser("reflect", help="Generate injection prompt for a lineage")
    ref_parser.add_argument("lineage_id")

    add_node_parser = subparsers.add_parser("add-node", help="Manually add a node to the evidence web")
    add_node_parser.add_argument("type", choices=sorted(web_layer.NODE_TYPES))
    add_node_parser.add_argument("content")
    add_node_parser.add_argument("--id", dest="node_id", help="Optional node ID")
    add_node_parser.add_argument("--confidence", type=float, default=1.0)

    add_edge_parser = subparsers.add_parser("add-edge", help="Manually add an edge to the evidence web")
    add_edge_parser.add_argument("from_node")
    add_edge_parser.add_argument("to_node")
    add_edge_parser.add_argument("type", choices=sorted(web_layer.EDGE_TYPES))
    add_edge_parser.add_argument("--weight", type=float, default=1.0)

    path_parser = subparsers.add_parser("path", help="Shortest path between two nodes")
    path_parser.add_argument("from_id")
    path_parser.add_argument("to_id")

    subparsers.add_parser("cycles", help="Detect circular reasoning in the evidence web")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Ensure DBs exist
    scar_layer.ensure_db()
    web_layer.ensure_db()

    if args.command == "init":
        print("Databases initialised.")
    elif args.command == "record":
        interactive_record()
    elif args.command == "record-auto":
        record_auto(args.lineage, args.type, args.the_break, args.blade,
                    args.smith, args.nutrient, args.grain)
    elif args.command == "show":
        show_scar(args.scar_id)
    elif args.command == "list":
        rows = scar_layer.list_scars()
        if not rows:
            print("No scars. The machine has not yet broken.")
        else:
            print(f"\n{'SCAR ID':<38} {'LINEAGE':<38} {'TYPE':<18} {'BLADE':<30} {'TIMESTAMP'}")
            print("-" * 130)
            for r in rows:
                print(f"{r[0]:<38} {r[1]:<38} {r[2]:<18} {r[4][:27]:<30} {r[8][:19]}")
    elif args.command == "ingest":
        ingest_scar(args.scar_id)
    elif args.command == "web":
        if args.claim:
            constraints = web_layer.get_constraints(args.claim)
            print(f"\nConstraints on {args.claim}:")
            for nid, ntype, content, w, etype in constraints:
                print(f"  [{etype}] {ntype}: {content[:60]} (w:{w})")
            fals = web_layer.get_falsifiers(args.claim)
            if fals:
                print("\nFalsifiers:")
                for nid, ntype, content in fals:
                    print(f"  [{ntype}] {content[:60]}")
            outgoing = web_layer.get_outgoing(args.claim)
            if outgoing:
                print("\nOutgoing influences:")
                for nid, ntype, content, etype, w in outgoing:
                    print(f"  [{etype}] -> {ntype}: {content[:60]} (w:{w})")
        else:
            nodes, edges = web_layer.get_graph()
            print(f"\nEVIDENCE WEB: {len(nodes)} nodes, {len(edges)} edges")
            counts = {}
            for _, (ntype, _content, _confidence) in nodes.items():
                counts[ntype] = counts.get(ntype, 0) + 1
            print("Nodes:", counts)
    elif args.command == "viz":
        viz.generate_dot(args.output)
    elif args.command == "reconcile":
        reconcile.reconcile(args.hypothesis_id)
    elif args.command == "reflect":
        p = scar_layer.generate_prompt(args.lineage_id)
        print(p if p else f"No scars for lineage {args.lineage_id}")
    elif args.command == "add-node":
        nid = web_layer.add_node(args.type, args.content, args.node_id, args.confidence)
        if nid:
            print(f"Node added: {nid} ({args.type})")
    elif args.command == "add-edge":
        eid = web_layer.add_edge(args.from_node, args.to_node, args.type, args.weight)
        if eid:
            print(f"Edge added: {args.from_node} --[{args.type}]--> {args.to_node}")
    elif args.command == "path":
        p = web_layer.shortest_path(args.from_id, args.to_id)
        print(f"\nPath: {' -> '.join(p)}" if p else f"No path found between {args.from_id} and {args.to_id}.")
    elif args.command == "cycles":
        cycles = web_layer.find_cycles()
        if not cycles:
            print("No circular reasoning detected. The web is acyclic.")
        else:
            print(f"\n[!] {len(cycles)} cycle(s) detected:")
            for i, cycle in enumerate(cycles, 1):
                print(f"  Cycle {i}: {' -> '.join(cycle)}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
