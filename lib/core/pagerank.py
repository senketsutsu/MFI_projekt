from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np

Edge = Tuple[str, str]

@dataclass
class PageRankStep:
    iteration: int
    vector: np.ndarray
    diff: float

def build_nodes(edges: List[Edge]) -> List[str]:
    """
    Zwraca posortowaną listę unikalnych węzłów na podstawie krawędzi.
    """
    return sorted({node for edge in edges for node in edge})

def build_transition_matrix(nodes: List[str], edges: List[Edge]) -> np.ndarray:
    """
    Buduje macierz przejścia M, gdzie M[i, j] oznacza prawdopodobieństwo przejścia z węzła j do węzła i.
    Jeśli węzeł nie ma wyjść (dangling node), to jego kolumna jest wypełniana równomiernie.
    """
    n = len(nodes)
    index = {node: i for i, node in enumerate(nodes)}
    matrix = np.zeros((n, n), dtype=float)

    outgoing: Dict[str, List[str]] = {node: [] for node in nodes}
    for source, target in edges:
        outgoing[source].append(target)

    for source in nodes:
        source_idx = index[source]
        targets = outgoing[source]

        if len(targets) == 0:
            matrix[:, source_idx] = 1.0 / n
        else:
            prob = 1.0 / len(targets)
            for target in targets:
                target_idx = index[target]
                matrix[target_idx, source_idx] = prob
    return matrix

def pagerank_iterations(matrix: np.ndarray, damping: float = 0.85, max_iter: int = 20, tol: float = 1e-6) -> List[PageRankStep]:
    """
    Iteracyjnie oblicza PageRank:
        r_(k+1) = d * M * r_k + (1-d) * v

    gdzie:
    - M to macierz przejścia,
    - d to współczynnik tłumienia,
    - v to wektor teleportacji (tu: równomierny).

    Zwraca listę kroków, żeby można było śledzić każdą iterację.
    """
    n = matrix.shape[0]
    rank = np.ones(n, dtype=float) / n
    teleport = np.ones(n, dtype=float) / n

    steps: List[PageRankStep] = [
        PageRankStep(iteration=0, vector=rank.copy(), diff=0.0)
    ]

    for iteration in range(1, max_iter + 1):
        new_rank = damping * (matrix @ rank) + (1 - damping) * teleport
        diff = np.linalg.norm(new_rank - rank, ord=1)

        steps.append(
            PageRankStep(
                iteration=iteration,
                vector=new_rank.copy(),
                diff=diff,
            )
        )
        rank = new_rank

        if diff < tol:
            break
    return steps

def compute_pagerank_from_edges(edges: List[Edge], damping: float = 0.85, max_iter: int = 20, tol: float = 1e-6):
    """
    Funkcja pomocnicza:
    z listy krawędzi buduje węzły, macierz i liczy iteracje.

    Zwraca:
    - nodes
    - matrix
    - steps
    """
    nodes = build_nodes(edges)
    matrix = build_transition_matrix(nodes, edges)
    steps = pagerank_iterations(
        matrix=matrix,
        damping=damping,
        max_iter=max_iter,
        tol=tol,
    )
    return nodes, matrix, steps