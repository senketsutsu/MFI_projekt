import random
from typing import Dict, List, Tuple

Edge = Tuple[str, str]
GraphEdges = List[Edge]


def _generate_scale_graph(node_count: int, extra_edges: int, seed: int) -> GraphEdges:
    rng = random.Random(seed)
    nodes = [f"N{i:03d}" for i in range(node_count)]
    edges_set = set()

    # pierscien zapewnia spojnosc i minimum jedna krawedz wychodzaca z kazdego wezla
    for i in range(node_count):
        edges_set.add((nodes[i], nodes[(i + 1) % node_count]))

    while len(edges_set) < node_count + extra_edges:
        source = nodes[rng.randrange(node_count)]
        target = nodes[rng.randrange(node_count)]
        if source != target:
            edges_set.add((source, target))

    return sorted(edges_set)

EXAMPLE_GRAPHS: Dict[str, GraphEdges] = {
    "Cykl prosty": [
        ("A", "B"),
        ("B", "C"),
        ("C", "A"),
    ],
    "Gwiazda": [
        ("A", "B"),
        ("A", "C"),
        ("A", "D"),
        ("A", "E"),
        ("B", "A"),
        ("C", "A"),
        ("D", "A"),
        ("E", "A"),
    ],
    "Graf z dangling node (no outlinks)": [
        ("A", "B"),
        ("B", "C"),
        ("C", "A"),
        ("C", "D"),
    ],
    "Mały graf testowy": [
        ("A", "B"),
        ("A", "C"),
        ("B", "C"),
        ("C", "A"),
        ("D", "C"),
    ],
    "Średni graf testowy": [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("C", "D"),
        ("C", "E"),
        ("D", "A"),
        ("E", "D"),
        ("F", "C"),
        ("F", "E"),
    ],
    "Skala 25 węzłów": _generate_scale_graph(node_count=25, extra_edges=50, seed=11),
    "Skala 75 węzłów": _generate_scale_graph(node_count=75, extra_edges=180, seed=17),
    "Skala 150 węzłów": _generate_scale_graph(node_count=150, extra_edges=450, seed=29),
}