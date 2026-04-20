from dash import dcc, html
from data.example_graphs import EXAMPLE_GRAPHS

def create_layout():
    return html.Div(
        style={"maxWidth": "1400px", "margin": "0 auto", "padding": "20px", "fontFamily": "Arial"},
        children=[
            html.H1("Uproszczony PageRank w Dash"),
            html.P(
                "Aplikacja pokazuje iteracyjne obliczanie PageRank oraz pozwala prześledzić każdą iterację metody."
            ),
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr 1fr",
                    "gap": "16px",
                    "marginBottom": "20px",
                },
                children=[
                    html.Div(
                        children=[
                            html.Label("Wybierz graf:"),
                            dcc.Dropdown(
                                id="graph-selector",
                                options=[{"label": name, "value": name} for name in EXAMPLE_GRAPHS.keys()],
                                value=next(iter(EXAMPLE_GRAPHS)),
                                clearable=False,
                            ),
                        ]
                    ),
                    html.Div(
                        children=[
                            html.Label("Współczynnik tłumienia d:"),
                            dcc.Slider(
                                id="damping-slider",
                                min=0.50,
                                max=0.95,
                                step=0.05,
                                value=0.85,
                                marks={i / 100: f"{i / 100:.2f}" for i in range(50, 100, 10)},
                            ),
                        ]
                    ),
                    html.Div(
                        children=[
                            html.Label("Liczba iteracji:"),
                            dcc.Slider(
                                id="max-iter-slider",
                                min=1,
                                max=30,
                                step=1,
                                value=10,
                                marks={i: str(i) for i in range(1, 31, 5)},
                            ),
                        ]
                    ),
                ],
            ),
            html.Div(
                style={"display": "flex", "gap": "12px", "marginBottom": "20px"},
                children=[
                    html.Button("Poprzedni krok", id="prev-button", n_clicks=0),
                    html.Button("Następny krok", id="next-button", n_clicks=0),
                    html.Button("Reset", id="reset-button", n_clicks=0),
                ],
            ),
            dcc.Store(id="current-step", data=0),
            html.Div(id="iteration-info", style={"fontSize": "18px", "marginBottom": "10px"}),
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1.2fr 1fr",
                    "gap": "18px",
                    "marginBottom": "20px",
                },
                children=[
                    dcc.Graph(id="network-graph"),
                    dcc.Graph(id="bar-chart"),
                ],
            ),
            dcc.Graph(id="convergence-chart"),
            html.H3("Macierz przejścia"),
            html.Div(id="matrix-view", style={"marginBottom": "20px"}),
            html.H3("Tabela wszystkich iteracji"),
            html.Div(id="iterations-table"),
        ],
    )