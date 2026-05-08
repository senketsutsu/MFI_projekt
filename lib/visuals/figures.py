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

    pos = nx.spring_layout(
            graph,
            seed=42,
            k=0.9,          
            iterations=80   
        )

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
        line=dict(width=1, color="rgba(120,120,140,0.35)"),
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
        node_text.append(
                            f"<b>{node}</b><br>"
                            f"PageRank: {ranks[i]:.6f}"
                        )
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

def build_convergence_figure(steps: List[PageRankStep], current_iteration: int = None) -> go.Figure:
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
                line=dict(color="#c4a7d8", width=2),
                hovertemplate="Iteracja: %{x}<br>Różnica: %{y:.8f}<extra></extra>",
            )
        ]
    )

    if current_iteration is not None:
        fig.add_vline(
            x=current_iteration,
            line_width=1.5,
            line_dash="dash",
            line_color="#6d597a"
        )

    fig.update_layout(
        title="Zbieżność metody iteracyjnej",
        xaxis_title="Iteracja",
        yaxis_title="||r(k) - r(k-1)||₁",
        margin=dict(l=40, r=20, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
        ),
    )
    fig.update_xaxes(
        title_text="Iteracja",
        showline=True,
        linecolor="#E5E7EB",
        linewidth=1,
        ticks="outside",
        tickcolor="#E5E7EB",
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        title_text="||r(k) - r(k-1)||₁",
        showline=True,
        linecolor="#E5E7EB",
        linewidth=1,
        ticks="outside",
        tickcolor="#E5E7EB",
        showgrid=True,
        gridcolor="#F3F4F6",   
        zeroline=False,
    )
    return fig

def build_matrix_heatmap(matrix, nodes):
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=nodes,
            y=nodes,
            colorscale="Purples",
            showscale=True,
            hovertemplate="From %{y}<br>To %{x}<br>Value=%{z:.3f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Macierz przejścia",
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="white",
    )

    return fig

