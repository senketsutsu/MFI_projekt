import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
from dash import Input, Output, State, html

from data.example_graphs import EXAMPLE_GRAPHS
from lib.core.pagerank import build_nodes, build_transition_matrix, pagerank_iterations
from lib.visuals.figures import (
    build_bar_figure,
    build_convergence_figure,
    build_network_figure,
)

analysis_df = pd.read_csv("lib/core/pagerank_analysis.csv")
ANALYSIS_SIZES = sorted(analysis_df["num_nodes"].unique().tolist())
ANALYSIS_DAMPINGS = sorted(analysis_df["damping"].unique().tolist())


def nearest_analysis_size(node_count):
    return min(ANALYSIS_SIZES, key=lambda size: abs(size - node_count))


def nearest_analysis_damping(damping):
    return min(ANALYSIS_DAMPINGS, key=lambda value: abs(value - damping))


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
        Output("analysis-play-state", "data"),
        Output("analysis-step-interval", "disabled"),
        Input("analysis-play-button", "n_clicks"),
        Input("analysis-stop-button", "n_clicks"),
        State("analysis-play-state", "data"),
    )
    def toggle_analysis_play(play_clicks, stop_clicks, playing):
        ctx = dash.callback_context
        if not ctx.triggered:
            return False, True

        trigger = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger == "analysis-play-button":
            return True, False

        return False, True

    @app.callback(
        Output("analysis-size-slider", "value"),
        Input("sync-analysis-size-switch", "value"),
        Input("graph-selector", "value"),
        Input("analysis-step-interval", "n_intervals"),
        State("analysis-size-slider", "value"),
    )
    def sync_or_advance_analysis_size(sync_values, graph_name, interval_tick, current_size):
        ctx = dash.callback_context
        current_size = current_size if current_size is not None else ANALYSIS_SIZES[0]

        if not ctx.triggered:
            return current_size

        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        sync_enabled = bool(sync_values and "sync" in sync_values)

        if trigger in {"sync-analysis-size-switch", "graph-selector"} and sync_enabled:
            nodes = build_nodes(EXAMPLE_GRAPHS[graph_name])
            return nearest_analysis_size(len(nodes))

        if trigger == "analysis-step-interval":
            try:
                current_index = ANALYSIS_SIZES.index(current_size)
            except ValueError:
                current_index = 0
            next_index = (current_index + 1) % len(ANALYSIS_SIZES)
            return ANALYSIS_SIZES[next_index]

        return current_size

    @app.callback(
        Output("analysis-3d-graph", "figure"),
        Input("analysis-size-slider", "value"),
    )
    def update_analysis_3d(_):
        grouped = (
            analysis_df.groupby(["num_nodes", "damping"])["convergence_iteration"]
            .mean()
            .reset_index()
        )

        pivot = grouped.pivot(
            index="damping",
            columns="num_nodes",
            values="convergence_iteration",
        )

        fig = {
            "data": [
                {
                    "type": "surface",
                    "x": pivot.columns,
                    "y": pivot.index,
                    "z": pivot.values,
                    "colorscale": "Viridis",
                    "showscale": True,
                }
            ],
            "layout": {
                "title": "Wpływ liczby węzłów i damping na zbieżność",
                "scene": {
                    "xaxis": {"title": {"text": "Liczba węzłów"}},
                    "yaxis": {"title": {"text": "Damping"}},
                    "zaxis": {"title": {"text": "Iteracja zbieżności"}},
                    "camera": {
                        "eye": {
                            "x": 1.6,
                            "y": 1.4,
                            "z": 0.8,
                        }
                    },
                },
                "margin": {"l": 0, "r": 0, "b": 0, "t": 50},
            },
        }

        return fig

    @app.callback(
        Output("analysis-convergence-graph", "figure"),
        Input("analysis-size-slider", "value"),
    )
    def update_analysis_convergence(selected_size):
        grouped = (
            analysis_df.groupby(["num_nodes", "iteration", "damping"])["diff"]
            .mean()
            .reset_index()
        )
        grouped = grouped[grouped["iteration"] > 0]
        filtered = grouped[grouped["num_nodes"] == selected_size]

        fig = px.line(
            filtered,
            x="iteration",
            y="diff",
            color="damping",
            log_y=True,
            markers=False,
            title=f"Zbieżność dla analizowanego rozmiaru sieci: {selected_size} węzłów",
        )

        fig.update_layout(
            xaxis_title="Iteracja",
            yaxis_title="Diff (log)",
            xaxis=dict(range=[0, filtered["iteration"].max()]),
            margin=dict(l=0, r=0, t=50, b=0),
            legend_title="Damping",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        return fig

    @app.callback(
        Output("analysis-table", "data"),
        Output("analysis-table", "columns"),
        Input("analysis-size-slider", "value"),
    )
    def update_analysis_table(selected_size):
        grouped = (
            analysis_df.groupby("num_nodes")
            .agg(
                avg_convergence_iteration=("convergence_iteration", "mean"),
                min_convergence_iteration=("convergence_iteration", "min"),
                max_convergence_iteration=("convergence_iteration", "max"),
            )
            .reset_index()
            .sort_values("num_nodes")
        )

        grouped["avg_convergence_iteration"] = grouped["avg_convergence_iteration"].round(2)
        grouped["selected"] = grouped["num_nodes"].apply(
            lambda value: "Tak" if value == selected_size else ""
        )

        columns = [
            {"name": "Rozmiar sieci", "id": "num_nodes"},
            {"name": "Średnia iteracja zbieżności", "id": "avg_convergence_iteration"},
            {"name": "Min iteracja zbieżności", "id": "min_convergence_iteration"},
            {"name": "Max iteracja zbieżności", "id": "max_convergence_iteration"},
            {"name": "Aktualny wybór", "id": "selected"},
        ]

        return grouped.to_dict("records"), columns

    @app.callback(
        Output("global-analysis-text", "children"),
        Input("analysis-size-slider", "value"),
        Input("damping-slider", "value"),
    )
    def update_global_analysis_text(selected_size, damping):
        nearest_damping = nearest_analysis_damping(damping)

        size_subset = analysis_df[analysis_df["num_nodes"] == selected_size]
        damping_subset = size_subset[size_subset["damping"] == nearest_damping]

        avg_conv_size = size_subset["convergence_iteration"].mean()
        min_conv_size = size_subset["convergence_iteration"].min()
        max_conv_size = size_subset["convergence_iteration"].max()

        low_damping = size_subset[size_subset["damping"] == size_subset["damping"].min()]["convergence_iteration"].mean()
        high_damping = size_subset[size_subset["damping"] == size_subset["damping"].max()]["convergence_iteration"].mean()

        avg_conv_damping = damping_subset["convergence_iteration"].mean()
        last_diff = damping_subset[damping_subset["iteration"] == damping_subset["iteration"].max()]["diff"].mean()

        trend_text = "więcej" if high_damping > low_damping else "mniej"

        return html.Ul(
            [
                html.Li(
                    f"Dla analizowanego rozmiaru {selected_size} węzłów średnia iteracja osiągnięcia zbieżności wynosi około {avg_conv_size:.2f}. "
                    f"W badanych przebiegach najszybsza zbieżność pojawiała się około iteracji {min_conv_size}, a najwolniejsza około iteracji {max_conv_size}."
                ),
                html.Li(
                    f"Dla aktualnego współczynnika tłumienia (damping factor) = {damping:.2f} wykorzystano najbliższą dostępną wartość z analizy {nearest_damping:.2f}. "
                    f"Dla tego ustawienia średnia iteracja zbieżności wynosi około {avg_conv_damping:.2f}, a końcowa średnia różnica między kolejnymi iteracjami ma rząd {last_diff:.2e}."
                ),
                html.Li(
                    f"W analizie przekrojowej dla tej skali większe wartości współczynnika tłumienia (damping factor) wymagały średnio {trend_text} iteracji do osiągnięcia zbieżności niż wartości niższe. "
                    f"Wskazuje to, że dobór tego parametru wpływa na tempo stabilizacji rankingu."
                ),
            ],
            className="mb-0",
            style={"paddingLeft": "1.2rem"},
        )

    @app.callback(
        Output("local-analysis-text", "children"),
        Input("graph-selector", "value"),
        Input("damping-slider", "value"),
        Input("max-iter-slider", "value"),
    )
    def update_local_analysis_text(graph_name, damping, max_iter):
        edges = EXAMPLE_GRAPHS[graph_name]
        nodes = build_nodes(edges)
        matrix = build_transition_matrix(nodes, edges)
        tol = 1e-6
        steps = pagerank_iterations(matrix, damping=damping, max_iter=max_iter, tol=tol)
        final_step = steps[-1]
        converged = final_step.diff < tol

        outgoing = {node: 0 for node in nodes}
        incoming = {node: 0 for node in nodes}

        for source, target in edges:
            outgoing[source] += 1
            incoming[target] += 1

        dangling_nodes = [node for node in nodes if outgoing[node] == 0]
        top_idx = int(np.argmax(final_step.vector))
        top_node = nodes[top_idx]
        top_value = final_step.vector[top_idx]

        density = len(edges) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0.0
        rank_spread = float(np.max(final_step.vector) - np.min(final_step.vector))
        nearest_size = nearest_analysis_size(len(nodes))

        spread_text = (
            "co oznacza zauważalne zróżnicowanie wartości PageRank między węzłami."
            if rank_spread >= 0.10
            else "co wskazuje na dość wyrównany rozkład wartości PageRank."
        )

        items = [
            html.Li(
                f"Wybrany graf „{graph_name}” zawiera {len(nodes)} węzłów i {len(edges)} krawędzi. "
                f"Gęstość połączeń wynosi około {density:.3f}."
            ),
            html.Li(
                f"Najwyższy PageRank ma obecnie węzeł {top_node} (≈ {top_value:.4f}). Różnica między najwyższą i najniższą wartością rankingu "
                f"wynosi około {rank_spread:.4f}, {spread_text}"
            ),
            html.Li(
                f"Dla współczynnika tłumienia (damping factor) = {damping:.2f} algorytm wykonał {len(steps) - 1} iteracji i {'osiągnął' if converged else 'nie osiągnął'} "
                f"zbieżności przy limicie {max_iter} iteracji."
            ),
        ]

        if dangling_nodes:
            items.append(
                html.Li(
                    f"Graf zawiera węzły bez krawędzi wychodzących: {', '.join(dangling_nodes)}. Taki przypadek wymaga dodatkowej redystrybucji rankingu w algorytmie PageRank "
                    f"i może wpływać na tempo zbieżności."
                )
            )
        else:
            items.append(
                html.Li(
                    "W tym grafie nie występują węzły bez krawędzi wychodzących, więc nie trzeba stosować dodatkowej redystrybucji rankingu dla dangling nodes."
                )
            )

        items.append(
            html.Li(
                [
                    f"Najbliższy rozmiar dostępny w analizie globalnej to {nearest_size} węzłów. Możesz zsynchronizować tę wartość ",
                    html.A(
                        "przełącznikiem",
                        href="#section-analysis-global",
                        style={"textDecoration": "underline", "color": "inherit", "fontWeight": "600"},
                    ),
                    " aby szybko porównać bieżący graf z analizą przekrojową.",
                ]
            )
        )

        return html.Ul(items, className="mb-0", style={"paddingLeft": "1.2rem"})

    @app.callback(
        Output("current-step", "data"),
        Input("prev-button", "n_clicks"),
        Input("next-button", "n_clicks"),
        Input("reset-button", "n_clicks"),
        Input("graph-selector", "value"),
        Input("damping-slider", "value"),
        Input("max-iter-slider", "value"),
        Input("step-interval", "n_intervals"),
        State("current-step", "data"),
        prevent_initial_call=True,
    )
    def update_step(prev_clicks, next_clicks, reset_clicks, graph_name, damping, max_iter, interval_tick, current_step):
        current_step = current_step or 0
        ctx = dash.callback_context
        if not ctx.triggered:
            return 0

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        tol = 1e-6
        auto = trigger_id == "step-interval"

        nodes = build_nodes(EXAMPLE_GRAPHS[graph_name])
        matrix = build_transition_matrix(nodes, EXAMPLE_GRAPHS[graph_name])
        steps = pagerank_iterations(matrix, damping=damping, max_iter=max_iter, tol=tol)
        max_step = len(steps) - 1

        if trigger_id in {"graph-selector", "damping-slider", "max-iter-slider", "reset-button"}:
            return 0
        if trigger_id == "prev-button":
            return max(0, current_step - 1)
        if trigger_id == "next-button":
            return min(max_step, current_step + 1)
        if auto:
            return min(max_step, current_step + 1)
        return 0

    @app.callback(
        Output("play-button", "children"),
        Input("play-state", "data"),
        Input("play-speed", "data"),
    )
    def update_play_button_label(playing, speed):
        return "▷ Play"
        # if not playing:
        #     return "▷ Play"

        # if speed == 1:
        #     return "▷ x2 Speed"

        # return "▷ x1 Speed"

    @app.callback(
        Output("play-state", "data"),
        Output("play-speed", "data"),
        Output("step-interval", "disabled"),
        Output("step-interval", "interval"),
        Input("play-button", "n_clicks"),
        Input("stop-button", "n_clicks"),
        Input("graph-selector", "value"),
        Input("damping-slider", "value"),
        Input("max-iter-slider", "value"),
        Input("reset-button", "n_clicks"),
        Input("confetti-trigger", "data"),
        State("play-state", "data"),
        State("play-speed", "data"),
    )
    def toggle_play(play_clicks, stop_clicks, graph_name, damping, max_iter, reset_clicks, confetti_fired, playing, speed):
        ctx = dash.callback_context
        if not ctx.triggered:
            return False, 1, True, 600

        trigger = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger in {"stop-button", "graph-selector", "damping-slider", "max-iter-slider", "reset-button"}:
            return False, 1, True, 600

        if trigger == "play-button":
            return True, 1, False, 600

            # new_speed = 2 if speed == 1 else 1
            # interval = 600 if new_speed == 2 else 600
            # return True, 1, False, interval

        return playing, speed, not playing, 600

    app.clientside_callback(
        """
        function(converged) {
            if (converged && window.confetti) {
                var defaults = {
                    spread: 360,
                    ticks: 50,
                    gravity: 0,
                    decay: 0.94,
                    startVelocity: 30,
                    colors: ['#FFE400', '#FFBD00', '#E89400', '#FFCA6C', '#FDFFB8']
                };

                function shoot() {
                    window.confetti({
                        ...defaults,
                        particleCount: 40,
                        scalar: 1.2,
                        shapes: ['star']
                    });

                    window.confetti({
                        ...defaults,
                        particleCount: 10,
                        scalar: 0.75,
                        shapes: ['circle']
                    });
                }

                setTimeout(shoot, 0);
                setTimeout(shoot, 100);
                setTimeout(shoot, 200);
            }

            return "";
        }
        """,
        Output("dummy-output", "children"),
        Input("confetti-trigger", "data"),
    )

    @app.callback(
        Output("collapse", "is_open"),
        Input("collapse-button", "n_clicks"),
        State("collapse", "is_open"),
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("iteration-info", "children"),
        Output("network-graph", "figure"),
        Output("bar-chart", "figure"),
        Output("convergence-chart", "figure"),
        Output("matrix-view", "children"),
        Output("iterations-table", "children"),
        Output("confetti-trigger", "data"),
        Output("has-converged", "data"),
        Input("graph-selector", "value"),
        Input("damping-slider", "value"),
        Input("max-iter-slider", "value"),
        Input("current-step", "data"),
        State("has-converged", "data"),
    )
    def update_visuals(graph_name, damping, max_iter, current_step, has_converged):
        edges = EXAMPLE_GRAPHS[graph_name]
        nodes = build_nodes(edges)
        matrix = build_transition_matrix(nodes, edges)
        tol = 1e-6
        steps = pagerank_iterations(matrix, damping=damping, max_iter=max_iter, tol=tol)

        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        safe_step = min(current_step, len(steps) - 1)
        current = steps[safe_step]
        final_step = steps[-1]
        converged = final_step.diff < tol

        if trigger_id == "graph-selector":
            has_converged = False

        info = dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.Div("Aktualna iteracja", className="text-muted small"),
                            html.Div(f"{current.iteration}", className="fw-bold fs-5"),
                        ]),
                        className="h-100",
                    ),
                    md=2,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.Div("Różnica", className="text-muted small"),
                            html.Div(f"{np.round(current.diff, 4)}", className="fw-bold fs-6"),
                        ]),
                        className="h-100",
                    ),
                    md=2,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.Div("Suma ranków", className="text-muted small"),
                            html.Div(f"{np.round(np.sum(current.vector), 2)}", className="fw-bold fs-6"),
                        ]),
                        className="h-100",
                    ),
                    md=2,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.Div("Iteracje wykonane", className="text-muted small"),
                            html.Div(f"{len(steps) - 1}", className="fw-bold fs-6"),
                        ]),
                        className="h-100",
                    ),
                    md=2,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.Div("Zbieżność", className="text-muted small"),
                            html.Div(
                                f"{'TAK' if converged else 'NIE'}",
                                className="fw-bold fs-6",
                                style={"color": "#2e7d32" if converged else "#b23a48"},
                            ),
                            html.Div(f"tol={tol:.0e}", className="small text-muted"),
                        ]),
                        className="h-100",
                    ),
                    md=2,
                ),
            ],
            className="g-3 w-100",
            style={"width": "100%"},
        )

        matrix_header = html.Tr([html.Th(" ")] + [html.Th(node) for node in nodes])
        matrix_rows = []

        for i, row_node in enumerate(nodes):
            row = [html.Td(row_node)]
            for j in range(len(nodes)):
                val = matrix[i, j]
                intensity = min(max(val, 0), 1)
                bg = f"rgba(196, 167, 216, {0.08 + 0.3 * intensity})"
                row.append(html.Td(f"{val:.3f}", style={"backgroundColor": bg}))
            matrix_rows.append(html.Tr(row))

        matrix_table = html.Table(
            [matrix_header] + matrix_rows,
            style={"borderCollapse": "collapse", "width": "100%"},
        )

        table_data = steps_to_table_data(nodes, steps)
        table_header = html.Tr([html.Th(col) for col in table_data[0].keys()])
        table_rows = []

        for row in table_data:
            is_current = int(row["iteracja"]) == current.iteration
            cells = [html.Td(value) for value in row.values()]
            row_style = {"backgroundColor": "#F5F3FF", "fontWeight": "600"} if is_current else {}
            table_rows.append(html.Tr(cells, style=row_style))

        iterations_table = html.Div(
            style={
                "maxHeight": "320px",
                "overflowY": "auto",
                "border": "1px solid #E5E7EB",
                "borderRadius": "8px",
            },
            children=[
                html.Table(
                    [table_header] + table_rows,
                    style={
                        "borderCollapse": "collapse",
                        "width": "100%",
                        "tableLayout": "fixed",
                        "fontSize": "14px",
                    },
                )
            ],
        )

        trigger_confetti = current.iteration == len(steps) - 1 and converged and not has_converged
        new_has_converged = trigger_confetti or has_converged

        if has_converged and current.iteration < len(steps) - 1:
            new_has_converged = False

        return (
            info,
            build_network_figure(nodes, edges, current.vector),
            build_bar_figure(nodes, current.vector),
            build_convergence_figure(steps, current.iteration),
            matrix_table,
            iterations_table,
            trigger_confetti,
            new_has_converged,
        )