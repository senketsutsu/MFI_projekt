from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.example_graphs import EXAMPLE_GRAPHS
from lib.core.pagerank import build_nodes, build_transition_matrix, compare_with_networkx, pagerank_iterations


def run_validation(graph_name: str = "Skala 25 węzłów") -> None:
    edges = EXAMPLE_GRAPHS[graph_name]
    nodes = build_nodes(edges)
    matrix = build_transition_matrix(nodes, edges)
    steps = pagerank_iterations(matrix, damping=0.85, max_iter=100, tol=1e-8)

    comparison = compare_with_networkx(
        nodes=nodes,
        edges=edges,
        vector=steps[-1].vector,
        damping=0.85,
        max_iter=100,
        tol=1e-8,
    )

    print(f"Graf: {graph_name}")
    print(f"Węzły: {len(nodes)}, krawędzie: {len(edges)}")
    print(f"Iteracje: {len(steps) - 1}, diff końcowy: {steps[-1].diff:.3e}")

    if comparison.error is not None:
        print(f"Błąd porównania z NetworkX: {comparison.error}")
        return

    print(f"L1 różnica do NetworkX: {comparison.l1_diff:.3e}")
    print(f"Maksymalna różnica: {comparison.max_abs_diff:.3e}")


if __name__ == "__main__":
    run_validation()
