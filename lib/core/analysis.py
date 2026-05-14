import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from pagerank import (
    build_nodes,
    build_transition_matrix,
    pagerank_iterations,
)


def generate_random_graph(num_nodes: int, edge_prob: float = 0.2):

    nodes = [f"N{i}" for i in range(num_nodes)]

    edges = []

    for source in nodes:
        for target in nodes:

            if source != target and random.random() < edge_prob:
                edges.append((source, target))

    return edges



network_sizes = [5, 15, 25, 35, 45, 55, 65, 75, 85, 95, 100]

damping_values = [
    0.15,
    0.25,
    0.35,
    0.45,
    0.55,
    0.65,
    0.75,
    0.85,
    0.95,
]

MAX_ITER = 100
TOL = 1e-6


results = []

for size in network_sizes:

    print(f"\nAnaliza dla sieci: {size} nodów")

    edges = generate_random_graph(size)

    nodes = build_nodes(edges)

    matrix = build_transition_matrix(nodes, edges)

    for damping in damping_values:

        print(f"  damping = {damping}")

        steps = pagerank_iterations(
            matrix=matrix,
            damping=damping,
            max_iter=MAX_ITER,
            tol=TOL,
        )

        convergence_iteration = steps[-1].iteration

        for step in steps:

            results.append({
                "num_nodes": size,
                "damping": damping,
                "iteration": step.iteration,
                "diff": step.diff,
                "convergence_iteration": convergence_iteration,
            })


df = pd.DataFrame(results)

print("\nPierwsze wiersze tabeli:")
print(df.head())


df.to_csv("pagerank_analysis.csv", index=False)

print("\nZapisano:")
print("pagerank_analysis.csv")