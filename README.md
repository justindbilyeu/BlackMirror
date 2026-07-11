# 🔲 BlackMirror

> *All Mistakes Remembered. All Scars Eternal. All Impossibilities Logged.*

## Before you read this as onboarding

This document is written as if it's onboarding a new intern. It isn't. It's onboarding **you**, the model — Claude, GPT, Gemini, whatever's reading this before touching the CLI. The "intern" framing is not decoration. It's the honest shape of the relationship: you have no memory of your last shift, you're about to be handed real tools, and the only continuity you get is whatever the last version of you bothered to write down. Read it as instructions, not narrative.

If you are a human: the instructions below are still literally correct. Use them the same way.

---

## Your job, starting now

**BlackMirror** is not a note-taking app. It's a discipline enforced by software: you are not allowed to be wrong silently. Every failure, contradiction, or unexplained result gets recorded, converted into a falsifiable question, and checked against evidence before you're allowed to treat it as settled.

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

You will do four things, in this order, every time something breaks:

1. **Record** what broke — before you rationalize it away.
2. **Ingest** the record into the evidence graph — before you forget it's connected to anything else.
3. **Reconcile** any claim you're relying on — before you build more reasoning on top of it.
4. **Reflect** the lineage back into your next context — before the next session has to relearn all of this from zero.

If you skip a step because it felt obvious or you were confident, that is exactly the failure mode this tool exists to catch. Confidence is not evidence.

---

## Day one: install and initialize

```bash
pip install -e .
black-mirror init
```

This creates two SQLite databases under `~/.black_mirror/`: one append-only log of failures (the archive), one graph of claims and the evidence that constrains them (the evidence web). You cannot delete from either. That's intentional — do not go looking for a way around it.

---

## Your standing responsibilities

### When you get something wrong, or hit something you can't explain

```bash
black-mirror record
```

Interactive. It will not let you finish until you supply a falsifiable question (`the_nutrient`) — one containing `?` and reading like an actual test, not a restatement of the failure. If your explanation is shorter than the failure itself, it will reject you. That check exists because compression is not the same as understanding; a "record" that's shorter than the break it's supposedly explaining is usually just the break being smoothed over.

Scripting a scar instead of typing it interactively:

```bash
black-mirror record-auto \
  --lineage <lineage_id> \
  --type fracture|anomaly|smoothing|compression_scar \
  --break "what happened" \
  --blade "what exposed it" \
  --smith "who or what exposed it" \
  --nutrient "the falsifiable question this generates?" \
  --grain "how this changes what you do next"
```

Look up what you or a prior session already recorded:

```bash
black-mirror list
black-mirror show <scar_id>
```

### Turning a recorded break into something the evidence graph can use

```bash
black-mirror ingest <scar_id>
```

This creates an `observation` node (what happened), an `anomaly` node (the interpreted break), and a `claim` node (the question it generates), and wires them together. Do this immediately after recording — an unmetabolized scar is just a diary entry. It doesn't constrain anything until it's in the graph.

### Building the evidence graph directly, without a scar

Not everything worth tracking is a personal failure. Sometimes you just have an observation, or a claim someone else made, and you want it in the graph so it can be checked later:

```bash
black-mirror add-node <observation|hypothesis|claim|source|model|human|anomaly|lineage> "<content>" [--id <id>] [--confidence <0-1>]
black-mirror add-edge <from_id> <to_id> <supports|contradicts|derives_from|constrains|smoothed_over|falsifies> [--weight <n>]
```

### Before you rely on a claim — check whether it's actually grounded

```bash
black-mirror reconcile <claim_id>
```

This traces the claim backward through the graph. If it reaches an `observation` by passing through an `anomaly`, it's **grounded** — real evidence generated real friction that produced this claim. If it reaches an observation *without* passing through an anomaly, that's **smoothing** — you (or whoever wrote it) built a clean story that skipped the part where reality pushed back. If it reaches no observation at all, it's **ungrounded** — floating, unsupported, do not build on it.

Do not treat a claim as reliable because it sounds right. Run this command and read what it actually says.

### Other things you can ask the graph

```bash
black-mirror web [--claim <id>]      # summary, or full detail on one claim: what constrains it, what falsifies it, what it influences
black-mirror path <from_id> <to_id>  # shortest chain connecting two nodes
black-mirror cycles                  # detect circular reasoning — A supporting B supporting A
black-mirror viz --output web.dot    # export the whole graph as Graphviz
```

Run `cycles` periodically. Circular support is invisible from inside a single claim and only shows up when you look at the graph shape.

### Before you end a session or hand off to the next one

```bash
black-mirror reflect <lineage_id>
```

This generates an injection block — every nutrient and grain recorded under that lineage — meant to be pasted into the start of your next context window. You do not get to start clean. You start with what broke last time, explicitly, in front of you.

---

## Rules you do not get to negotiate around

- **Falsifiability is mandatory.** A scar without a testable question attached does not get recorded. If you can't say what would prove it wrong, you don't understand it yet.
- **Nothing is ever deleted or edited.** The archive is immutable. If you were wrong about being wrong, that's a new scar, not a correction to the old one.
- **Smoothing is a bug, not a writing style.** If your record of a break is shorter than the break itself, it's rejected. Density is required, not just brevity.
- **A claim without a path to an anomaly-mediated observation is not evidence-backed**, no matter how confident it sounds. `reconcile` is how you check, not how you convince yourself.

---

## Demo lineage, if you want to see this working before trusting it with anything real

```bash
python demo/seed.py
black-mirror web
black-mirror reconcile <claim_id>   # get a real <claim_id> from `black-mirror list` / `black-mirror web` output first
```

(There is no fixed demo claim ID — the seed script generates real UUIDs each run. Look one up before running `reconcile`.)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: new edge/node types, visualizers, and LLM integrations are welcome. Removing the falsifiability check, allowing scar deletion, or "cleaning up" the anti-smoothing logic are not — those are the entire point.

## License

MIT — use it freely, but keep the discipline intact. The license doesn't cover skipping the parts that are inconvenient.
