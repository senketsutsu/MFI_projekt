import dash
import numpy as np
from dash import Input, Output, State, html
from data.example_graphs import EXAMPLE_GRAPHS
from lib.core.pagerank import build_nodes, build_transition_matrix, compare_with_networkx, pagerank_iterations
from lib.visuals.figures import build_bar_figure, build_convergence_figure, build_network_figure

def steps_to_table_data(nodes, steps):
    rows = []

    for step in steps:
        row = {
            "iteracja": step.iteration,
            "diff": f"{step.diff:.8f}",
        }

        for i, node in enumerate(nodes):
            row[node] = f"{step.vector[i]:.6f}"
        rows.append(row)
    return rows

def register_callbacks(app):
    @app.callback(
        Output("current-step", "data"),
        Input("prev-button", "n_clicks"),
        Input("next-button", "n_clicks"),
        Input("reset-button", "n_clicks"),
        Input("graph-selector", "value"),
        Input("damping-slider", "value"),
        Input("max-iter-slider", "value"),
        Input("tol-slider", "value"),
        State("current-step", "data"),
        prevent_initial_call=True,
    )
    def update_step(prev_clicks, next_clicks, reset_clicks, graph_name, damping, max_iter, tol_power, current_step):
        ctx = dash.callback_context
        if not ctx.triggered:
            return 0

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        tol = 10 ** (-tol_power)

        nodes = build_nodes(EXAMPLE_GRAPHS[graph_name])
        matrix = build_transition_matrix(nodes, EXAMPLE_GRAPHS[graph_name])
        steps = pagerank_iterations(matrix, damping=damping, max_iter=max_iter, tol=tol)
        max_step = len(steps) - 1

        if trigger_id in {"graph-selector", "damping-slider", "max-iter-slider", "tol-slider", "reset-button"}:
            return 0
        if trigger_id == "prev-button":
            return max(0, current_step - 1)
        if trigger_id == "next-button":
            return min(max_step, current_step + 1)
        return 0

    @app.callback(
        Output("iteration-info", "children"),
        Output("network-graph", "figure"),
        Output("bar-chart", "figure"),
        Output("convergence-chart", "figure"),
        Output("matrix-view", "children"),
        Output("iterations-table", "children"),
        Input("graph-selector", "value"),
        Input("damping-slider", "value"),
        Input("max-iter-slider", "value"),
        Input("tol-slider", "value"),
        Input("current-step", "data"),
    )
    def update_visuals(graph_name, damping, max_iter, tol_power, current_step):
        edges = EXAMPLE_GRAPHS[graph_name]
        nodes = build_nodes(edges)
        matrix = build_transition_matrix(nodes, edges)
        tol = 10 ** (-tol_power)
        steps = pagerank_iterations(matrix, damping=damping, max_iter=max_iter, tol=tol)

        safe_step = min(current_step, len(steps) - 1)
        current = steps[safe_step]
        final_step = steps[-1]
        converged = final_step.diff < tol

        comparison = compare_with_networkx(
            nodes=nodes,
            edges=edges,
            vector=final_step.vector,
            damping=damping,
            max_iter=max_iter,
            tol=tol,
        )

        comparison_block = []
        if comparison.error is None:
            comparison_block = [
                html.Span(f" | zgodność z NetworkX L1: {comparison.l1_diff:.8e}"),
                html.Span(f" | max|Δ|: {comparison.max_abs_diff:.8e}"),
            ]
        else:
            comparison_block = [
                html.Span(f" | porównanie z NetworkX niedostępne: {comparison.error}"),
            ]

        info = html.Div(
            [
                html.Strong(f"Aktualna iteracja: {current.iteration}"),
                html.Span(f" | różnica względem poprzedniej: {current.diff:.8f}"),
                html.Span(f" | suma ranków: {np.sum(current.vector):.6f}"),
                html.Span(f" | iteracje wykonane: {len(steps) - 1}"),
                html.Span(f" | zbieżność: {'TAK' if converged else 'NIE'} (tol={tol:.0e})"),
                *comparison_block,
            ]
        )

        matrix_header = html.Tr([html.Th(" ")] + [html.Th(node) for node in nodes])
        matrix_rows = []
        for i, row_node in enumerate(nodes):
            row = [html.Td(row_node)] + [html.Td(f"{matrix[i, j]:.3f}") for j in range(len(nodes))]
            matrix_rows.append(html.Tr(row))

        matrix_table = html.Table(
            [matrix_header] + matrix_rows,
            style={"borderCollapse": "collapse", "width": "100%"},
        )

        table_data = steps_to_table_data(nodes, steps)
        table_header = html.Tr([html.Th(col) for col in table_data[0].keys()])
        table_rows = []
        for row in table_data:
            style = {"backgroundColor": "#f1f5f9"} if int(row["iteracja"]) == current.iteration else {}
            table_rows.append(html.Tr([html.Td(value) for value in row.values()], style=style))

        iterations_table = html.Div(
            style={"maxHeight": "320px", "overflowY": "auto", "border": "1px solid #ddd"},
            children=[
                html.Table(
                    [table_header] + table_rows,
                    style={"borderCollapse": "collapse", "width": "100%"},
                )
            ],
        )

        return (
            info,
            build_network_figure(nodes, edges, current.vector),
            build_bar_figure(nodes, current.vector),
            build_convergence_figure(steps),
            matrix_table,
            iterations_table,
        )