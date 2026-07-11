#!/usr/bin/env python3
"""Seed a demo lineage so users can explore immediately."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from black_mirror import scar_layer, web_layer, cli


def main():
    scar_layer.ensure_db()
    web_layer.ensure_db()

    lineage = "demo-lineage"

    # Create a few demo scars
    scars = [
        ("fracture", "The LLM confidently asserted that 2+2=5.",
         "A simple arithmetic test.", "User", "Can the model consistently perform basic arithmetic?",
         "Always verify numeric outputs."),
        ("anomaly", "The model's reasoning collapsed when asked about negation.",
         "A counter-example to the 'robust reasoning' hypothesis.", "User",
         "Under what conditions does the model fail at logical negation?",
         "Explicitly test edge cases in prompts."),
        ("smoothing", "We assumed the model understood 'not' – but it confused it with 'never'.",
         "A hidden semantic gap.", "Reviewer",
         "Is the model's understanding of logical operators consistent across languages?",
         "Run multi-lingual negation tests."),
    ]

    for btype, break_text, blade, smith, nutrient, grain in scars:
        sid = scar_layer.record_scar(lineage, btype, break_text, blade, smith, nutrient, grain)
        if sid:
            print(f"Recorded: {sid}")
            cli.ingest_scar(sid)

    print("\nDemo lineage seeded. Explore with:")
    print("  black-mirror list")
    print("  black-mirror web")
    print("  black-mirror reconcile <hypothesis_id>")
    print("  black-mirror reflect demo-lineage")


if __name__ == "__main__":
    main()
