import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
from dash import Input, Output, State, html

from data.example_graphs import EXAMPLE_GRAPHS
from lib.core.pagerank import build_nodes, build_transition_matrix, compare_with_networkx, pagerank_iterations
from lib.visuals.figures import build_bar_figure, build_convergence_figure, build_matrix_heatmap, build_network_figure

analysis_df = pd.read_csv(
    "lib/core/pagerank_analysis.csv"
)


def register_callbacks(app):
    
    @app.callback(
        Output("analysis-3d-graph", "figure"),
        Input("damping-slider", "value"),
    )
    def update_analysis_3d(_):

        grouped = (
        analysis_df
        .groupby(["num_nodes", "damping"])
        ["convergence_iteration"]
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
                "title": "Wpływ liczby nodów i damping na zbieżność",

                "scene": {
                    "xaxis": {
                        "title": {
                            "text": "Liczba nodów"
                        }
                    },

                    "yaxis": {
                        "title": {
                            "text": "Damping"
                        }
                    },

                    "zaxis": {
                        "title": {
                            "text": "Iteracja zbieżności"
                        }
                    },

                    "camera": {
                        "eye": {
                            "x": 1.6,
                            "y": 1.4,
                            "z": 0.8,
                        }
                    },
                },

                "margin": {
                    "l": 0,
                    "r": 0,
                    "b": 0,
                    "t": 50,
                },
            },
        }

        return fig

    @app.callback(
        Output("analysis-convergence-graph", "figure"),
        Input("damping-slider", "value"),
    )
    def update_analysis_convergence(_):

        grouped = (
            analysis_df
            .groupby(
                ["num_nodes", "iteration", "damping"]
            )["diff"]
            .mean()
            .reset_index()
        )

        grouped = grouped[grouped["iteration"] > 0]

        fig = px.line(
            grouped,

            x="iteration",
            y="diff",

            color="damping",

            animation_frame="num_nodes",

            log_y=True,

            markers=False,

            title="Wpływ rozmiaru sieci na zbieżność",
        )

        fig.update_layout(
            xaxis_title="Iteracja",
            yaxis_title="Diff (log)",

            xaxis=dict(
                range=[0, grouped["iteration"].max()]
            ),

            margin=dict(
                l=0,
                r=0,
                t=50,
                b=0,
            ),
            transition={
                "duration": 3000,
            },

            legend_title="Damping",
        )

        return fig

    @app.callback(
        Output("analysis-table", "data"),
        Output("analysis-table", "columns"),
        Input("damping-slider", "value"),
    )
    def update_analysis_table(_):

        grouped = (
            analysis_df
            .groupby("num_nodes")
            .agg(
                avg_convergence_iteration=("convergence_iteration", "mean"),
                min_convergence_iteration=("convergence_iteration", "min"),
                max_convergence_iteration=("convergence_iteration", "max"),
            )
            .reset_index()
            .sort_values("num_nodes")
        )

        grouped["avg_convergence_iteration"] = grouped["avg_convergence_iteration"].round(4)

        columns = [
            {"name": "Rozmiar sieci", "id": "num_nodes"},
            {"name": "Średnia iteracja zbieżności", "id": "avg_convergence_iteration"},
            {"name": "Min iteracja zbieżności", "id": "min_convergence_iteration"},
            {"name": "Max iteracja zbieżności", "id": "max_convergence_iteration"},
        ]

        return grouped.to_dict("records"), columns

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
        if not playing:
            return "▷ Play"

        if speed == 1:
            return "▷ x2 Speed"

        return "▷ x1 Speed"

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

        State("play-state", "data"),
        State("play-speed", "data"),
    )
    def toggle_play(play_clicks, stop_clicks,
                    graph_name, damping, max_iter, reset_clicks,
                    playing, speed):

        ctx = dash.callback_context

        if not ctx.triggered:
            return False, 1, True, 600

        trigger = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger in {"stop-button", "graph-selector", "damping-slider", "max-iter-slider", "reset-button"}:
            return False, 1, True, 600

        if trigger == "play-button":
            if not playing:
                return True, 1, False, 600  
            else:
                new_speed = 2 if speed == 1 else 1
                interval = 400 if new_speed == 2 else 600
                return True, new_speed, False, interval

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

        comparison = compare_with_networkx(
            nodes=nodes,
            edges=edges,
            vector=final_step.vector,
            damping=damping,
            max_iter=200,
            tol=tol,
        )

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

        matrix_header = html.Tr(
            [html.Th(" ")] + [html.Th(node) for node in nodes]
        )

        matrix_rows = []

        for i, row_node in enumerate(nodes):
            row = [html.Td(row_node)]

            for j in range(len(nodes)):
                val = matrix[i, j]

                intensity = min(max(val, 0), 1)
                bg = f"rgba(196, 167, 216, {0.08 + 0.3 * intensity})"

                row.append(
                    html.Td(
                        f"{val:.3f}",
                        style={"backgroundColor": bg}
                    )
                )

            matrix_rows.append(html.Tr(row))

        matrix_table = html.Table(
            [matrix_header] + matrix_rows,
            style={
                "borderCollapse": "collapse",
                "width": "100%",
            },
        )

        table_data = steps_to_table_data(nodes, steps)

        table_header = html.Tr([html.Th(col) for col in table_data[0].keys()])

        table_rows = []

        for row in table_data:
            is_current = int(row["iteracja"]) == current.iteration

            cells = [html.Td(value) for value in row.values()]

            row_style = {}

            if is_current:
                row_style = {
                    "backgroundColor": "#F5F3FF", 
                    "fontWeight": "600",
                }

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