"""Unified CLI for BlackMirror."""

import argparse
import sys
import sqlite3
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
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
