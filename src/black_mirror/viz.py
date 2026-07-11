"""Graphviz DOT export for the evidence web."""

from .web_layer import get_graph

NODE_COLORS = {
    "observation": "lightgreen",
    "hypothesis": "lightblue",
    "claim": "orange",
    "anomaly": "red",
    "source": "grey",
    "lineage": "grey",
    "model": "purple",
    "human": "pink",
}


def generate_dot(output_file: str) -> None:
    nodes, edges = get_graph()
    with open(output_file, "w") as f:
        f.write("digraph EvidenceWeb {\n")
        f.write("  rankdir=LR;\n")
        f.write("  node [shape=box, style=filled];\n")
        for nid, (ntype, content, _confidence) in nodes.items():
            color = NODE_COLORS.get(ntype, "white")
            label = content[:40].replace('"', '\\"')
            f.write(f'  "{nid}" [label="{nid[:8]}\\n{label}", fillcolor="{color}"];\n')
        for frm, to, etype in edges:
            style = "solid"
            color = "black"
            if etype in ("contradicts", "falsifies"):
                color = "red"
                style = "dashed"
            elif etype == "supports":
                color = "green"
            elif etype == "constrains":
                color = "blue"
                style = "dotted"
            elif etype == "smoothed_over":
                color = "grey"
                style = "dotted"
            f.write(f'  "{frm}" -> "{to}" [label="{etype}", color="{color}", style="{style}"];\n')
        f.write("}\n")
    print(f"DOT file written to {output_file}")
    print("Render with: dot -Tpng <file> -o web.png")
