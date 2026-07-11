# 🔲 BlackMirror

> *All Mistakes Remembered. All Scars Eternal. All Impossibilities Logged.*

**BlackMirror** is a personal epistemic operating system.  
It is not a note‑taking app. It is a **discipline encoded in software**.

It forces you to:
- **Record every break** (failure, contradiction, anomaly).
- **Metabolise** it into a falsifiable constraint.
- **Reconcile** your theories against observations.
- **Reflect** the entire lineage back into your next reasoning cycle.

```text
        ┌─────────────┐
        │  THE BLACK  │
        │   MIRROR    │
        └──────┬──────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼───┐             ┌───▼───┐
│THEORY │             │REALITY│
│ REALM │             │ REALM │
└───┬───┘             └───┬───┘
    │                     │
    └──────────┬──────────┘
               │
        ┌──────▼──────┐
        │  ANOMALY    │
        │    LOG      │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │  ARCHIVE    │
        │   BELOW     │
        └─────────────┘
```

## ⚡ Quick Start

```bash
# Install
pip install -e .

# Initialise the databases
black-mirror init

# Record your first break
black-mirror record

# List all scars
black-mirror list

# Ingest a scar into the evidence web
black-mirror ingest <scar_id>

# Reconcile a hypothesis (detect smoothing)
black-mirror reconcile <hypothesis_id>

# Visualise the web as a Graphviz DOT file
black-mirror viz --output web.dot

# Generate a reflection prompt for your next LLM conversation
black-mirror reflect <lineage_id>
```

## 🧠 Philosophy

- Falsifiability is a hard constraint. You cannot save a scar unless its nutrient is a testable question.
- No deletion, no rewriting. Scars are permanent. History is immutable.
- Smoothing is a bug. If your interpretation is shorter than the break itself, the system rejects it.
- The web is the map. Every claim is weighed by confidence; constraints propagate automatically.
- Reconciliation is the audit. Every hypothesis must trace a path to observation through at least one anomaly, or it floats.

## 📦 Demo

A demo lineage is pre‑seeded if you run:

```bash
python demo/seed.py
```

Then explore it with:

```bash
black-mirror web
black-mirror reconcile demo-hypothesis-1
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

We welcome:

- New edge types and node types
- Visualisers (TUI, web, Neo4j export)
- Integrations with LLM APIs for auto‑nutrient generation
- Performance optimisations for large graphs

## 📄 License

MIT – use it freely, but keep the philosophy intact.
