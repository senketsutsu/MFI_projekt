from typing import List, Tuple
import networkx as nx
import numpy as np
import plotly.graph_objects as go

from lib.core.pagerank import PageRankStep

Edge = Tuple[str, str]

def build_network_figure(nodes, edges, ranks):
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    pos = nx.spring_layout(graph, seed=42)

    edge_x = []
    edge_y = []

    for source, target in graph.edges():
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        hoverinfo="none",
        line=dict(width=1, color="#b8b8c8"),
        name="Krawędzie",
    )

    node_x = []
    node_y = []
    node_text = []
    node_sizes = []

    for i, node in enumerate(nodes):
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{node}<br>PageRank = {ranks[i]:.4f}")
        node_sizes.append(28 + ranks[i] * 140)

    cmin = float(np.min(ranks))
    cmax = float(np.max(ranks))

    if cmin == cmax:
        cmax = cmin + 1e-9

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=nodes,
        textposition="top center",
        hoverinfo="text",
        hovertext=node_text,
        marker=dict(
            size=node_sizes,
            color=ranks,
            colorscale="Purples",
            cmin=cmin,
            cmax=cmax,
            line=dict(width=1, color="#6d597a"),
            showscale=True,
            colorbar=dict(title="PageRank"),
        ),
        name="Węzły",
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="Graf i aktualne wartości PageRank",
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    return fig

def build_bar_figure(nodes, ranks):
    cmin = float(np.min(ranks))
    cmax = float(np.max(ranks))

    if cmin == cmax:
        cmax = cmin + 1e-9

    fig = go.Figure(
        data=[
            go.Bar(
                x=nodes,
                y=ranks,
                text=[f"{value:.4f}" for value in ranks],
                textposition="outside",
                marker=dict(
                    color=ranks,
                    colorscale="Purples",
                    cmin=cmin,
                    cmax=cmax,
                    line=dict(width=1, color="#6d597a"),
                    showscale=False,
                ),
            )
        ]
    )

    fig.update_layout(
        title="Aktualny wektor PageRank",
        xaxis_title="Węzeł",
        yaxis_title="Wartość",
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

def build_convergence_figure(steps: List[PageRankStep]) -> go.Figure:
    """
    Buduje wykres zbieżności metody iteracyjnej:
    ||r(k) - r(k-1)||_1
    """
    fig = go.Figure(
        data=[
            go.Scatter(
                x=[step.iteration for step in steps],
                y=[step.diff for step in steps],
                mode="lines+markers",
                name="Różnica L1",
            )
        ]
    )

    fig.update_layout(
        title="Zbieżność metody iteracyjnej",
        xaxis_title="Iteracja",
        yaxis_title="||r(k) - r(k-1)||₁",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig