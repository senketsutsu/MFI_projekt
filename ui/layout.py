from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

from data.example_graphs import EXAMPLE_GRAPHS


ANALYSIS_SIZES = [5, 15, 25, 35, 45, 55, 65, 75, 85, 95, 100]

SIDEBAR_STYLE = {
    "position": "sticky",
    "top": "0",
    "height": "100vh",
    "padding": "1rem",
    "backgroundColor": "#f8f9fa",
    "borderRight": "1px solid #dee2e6",
    "overflowY": "auto",
}

CONTENT_STYLE = {
    "padding": "1.25rem",
}

CARD_STYLE = {
    "border": "1px solid #e9ecef",
    "borderRadius": "16px",
    "boxShadow": "0 2px 10px rgba(0,0,0,0.06)",
}

NAV_LINK_STYLE = {
    "color": "#1d4e89",
    "fontWeight": "500",
}

BUTTON_STYLE = {
    "backgroundColor": "#ede4f7",
    "borderColor": "#ede4f7",
    "color": "#35224a",
    "borderRadius": "10px",
    "fontWeight": "500",
}


def create_sidebar(collapsed=False):
    return html.Div(
        [
            html.H3("PageRank Explorer", className="mb-1"),
            html.P(
                "Uproszczony algorytm PageRank",
                className="text-muted mb-4",
            ),
            dbc.Button(
                "☰  Spis treści",
                id="collapse-button",
                n_clicks=0,
                color="light",
                className="mb-3",
                style={"width": "100%"},
            ),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavLink("Parametry", href="#section-controls", external_link=True, style=NAV_LINK_STYLE),
                        dbc.NavLink("Graf", href="#section-network", external_link=True, style=NAV_LINK_STYLE),
                        dbc.NavLink("Wektor PageRank", href="#section-bar", external_link=True, style=NAV_LINK_STYLE),
                        dbc.NavLink("Zbieżność", href="#section-convergence", external_link=True, style=NAV_LINK_STYLE),
                        dbc.NavLink("Wnioski lokalne", href="#section-analysis-local", external_link=True, style=NAV_LINK_STYLE),
                        dbc.NavLink("Macierz przejścia", href="#section-matrix", external_link=True, style=NAV_LINK_STYLE),
                        dbc.NavLink("Tabela iteracji", href="#section-table", external_link=True, style=NAV_LINK_STYLE),
                        dbc.NavLink("Analiza globalna", href="#section-analysis-global", external_link=True, style=NAV_LINK_STYLE),
                    ],
                    vertical=True,
                    pills=True,
                    className="mb-4",
                ),
                id="collapse",
                is_open=False,
            ),
            html.Hr(),
            html.H6("Dane", className="text-uppercase text-muted"),
            html.P(
                "Korzystamy z domyślnego zbioru przykładowych grafów. Możesz przełączać ich strukturę i obserwować wpływ parametrów na zbieżność.",
                className="small text-muted mb-3",
            ),
            html.Label("Wybierz graf:", className="fw-semibold"),
            dcc.Dropdown(
                id="graph-selector",
                options=[{"label": name, "value": name} for name in EXAMPLE_GRAPHS.keys()],
                value="Mały graf testowy",
                clearable=False,
                className="mb-4",
            ),
            html.Label("Współczynnik tłumienia d:", className="fw-semibold"),
            dcc.Slider(
                id="damping-slider",
                min=0.50,
                max=0.95,
                step=0.05,
                value=0.85,
                marks={i / 100: f"{i / 100:.2f}" for i in range(50, 100, 10)},
                className="mb-4",
            ),
            html.Br(),
            html.Label("Maksymalna liczba iteracji:", className="fw-semibold"),
            dcc.Slider(
                id="max-iter-slider",
                min=1,
                max=100,
                step=1,
                value=10,
                marks={i: str(i) for i in range(1, 101, 10)},
                className="mb-4",
            ),
            html.Br(),
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    "▷  Play",
                                    id="play-button",
                                    n_clicks=0,
                                    style=BUTTON_STYLE,
                                    className="w-100",
                                ),
                                width=6,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "||  Stop",
                                    id="stop-button",
                                    n_clicks=0,
                                    style=BUTTON_STYLE,
                                    className="w-100",
                                ),
                                width=6,
                            ),
                        ],
                        className="mb-2",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    "❮❮  Poprzedni",
                                    id="prev-button",
                                    n_clicks=0,
                                    style=BUTTON_STYLE,
                                    className="w-100",
                                ),
                                width=6,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Następny  ❯❯",
                                    id="next-button",
                                    n_clicks=0,
                                    style=BUTTON_STYLE,
                                    className="w-100",
                                ),
                                width=6,
                            ),
                        ],
                        className="mb-2",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    "Reset",
                                    id="reset-button",
                                    n_clicks=0,
                                    style=BUTTON_STYLE,
                                    className="w-100",
                                ),
                                width=12,
                            )
                        ]
                    ),
                ],
                className="w-100",
            ),
        ],
        style=SIDEBAR_STYLE,
    )



def create_main_content():
    return html.Div(
        [
            dcc.Store(id="current-step", data=0),
            dcc.Store(id="play-speed", data=1),
            dcc.Store(id="confetti-trigger", data=False),
            dcc.Store(id="has-converged", data=False),
            dcc.Store(id="analysis-play-state", data=False),
            html.Div(id="dummy-output", style={"display": "none"}),
            dcc.Interval(
                id="step-interval",
                interval=800,
                disabled=True,
            ),
            dcc.Interval(
                id="analysis-step-interval",
                interval=900,
                disabled=True,
            ),
            dcc.Store(id="play-state", data=False),

            html.Div(id="section-controls"),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Parametry i stan iteracji", className="card-title"),
                        html.Div(
                            id="iteration-info",
                            style={"fontSize": "18px", "marginBottom": "0"},
                        ),
                    ]
                ),
                style={**CARD_STYLE, "width": "100%"},
                className="mb-4",
            ),

            html.Div(id="section-network"),
            html.Div(id="section-bar"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H4("Graf i aktualne wartości PageRank", className="card-title"),
                                    dcc.Graph(
                                        id="network-graph",
                                        style={"height": "380px"},
                                    ),
                                ]
                            ),
                            style=CARD_STYLE,
                            className="mb-4 h-100",
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H4("Wektor PageRank", className="card-title"),
                                    dcc.Graph(
                                        id="bar-chart",
                                        style={"height": "380px"},
                                    ),
                                ]
                            ),
                            style=CARD_STYLE,
                            className="mb-4 h-100",
                        ),
                        md=6,
                    ),
                ],
                className="g-4",
            ),

            html.Div(id="section-convergence"),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Zbieżność metody", className="card-title"),
                        dcc.Graph(id="convergence-chart"),
                    ]
                ),
                style=CARD_STYLE,
                className="mb-4",
            ),

            html.Div(id="section-analysis-local"),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H3("Wnioski dla aktualnego grafu", className="card-title mb-3"),
                        html.Div(id="local-analysis-text", className="text-muted"),
                    ]
                ),
                style={**CARD_STYLE, "border": "1px solid #ede9f7", "backgroundColor": "#fcfaff"},
                className="mb-4",
            ),

            html.Div(id="section-matrix"),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Macierz przejścia", className="card-title"),
                        html.Div(id="matrix-view"),
                    ]
                ),
                style=CARD_STYLE,
                className="mb-4",
            ),

            html.Div(id="section-table"),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Tabela wszystkich iteracji", className="card-title"),
                        html.Div(id="iterations-table"),
                    ]
                ),
                style=CARD_STYLE,
                className="mb-4",
            ),

            html.Div(id="section-analysis-global"),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H3("Analiza globalna dla różnych skal grafów", className="card-title mb-4"),

                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5("Wykres 3D zbieżności", className="card-title"),
                                                dcc.Graph(
                                                    id="analysis-3d-graph",
                                                    style={"height": "420px"},
                                                ),
                                            ]
                                        ),
                                        style=CARD_STYLE,
                                        className="h-100",
                                    ),
                                    md=6,
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5("Iteracja vs różnica", className="card-title"),
                                                dcc.Graph(
                                                    id="analysis-convergence-graph",
                                                    style={"height": "420px"},
                                                ),
                                            ]
                                        ),
                                        style=CARD_STYLE,
                                        className="h-100",
                                    ),
                                    md=6,
                                ),
                            ],
                            className="g-4 mb-3",
                        ),

                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Label("Rozmiar sieci w analizie globalnej", className="fw-semibold"),
                                        dcc.Slider(
                                            id="analysis-size-slider",
                                            min=min(ANALYSIS_SIZES),
                                            max=max(ANALYSIS_SIZES),
                                            step=None,
                                            value=ANALYSIS_SIZES[0],
                                            marks={size: str(size) for size in ANALYSIS_SIZES},
                                            className="mb-3",
                                        ),
                                    ],
                                    md=8,
                                ),
                                dbc.Col(
                                    [
                                        html.Label("Sterowanie", className="fw-semibold"),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Button(
                                                        "▷ Play",
                                                        id="analysis-play-button",
                                                        n_clicks=0,
                                                        style=BUTTON_STYLE,
                                                        className="w-100",
                                                    ),
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    dbc.Button(
                                                        "|| Stop",
                                                        id="analysis-stop-button",
                                                        n_clicks=0,
                                                        style=BUTTON_STYLE,
                                                        className="w-100",
                                                    ),
                                                    width=6,
                                                ),
                                            ],
                                            className="g-2",
                                        ),
                                    ],
                                    md=4,
                                ),
                            ],
                            className="align-items-end mb-2",
                        ),

                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Checklist(
                                        id="sync-analysis-size-switch",
                                        options=[
                                            {
                                                "label": " Dopasuj rozmiar analizy do liczby węzłów aktualnego grafu",
                                                "value": "sync",
                                            }
                                        ],
                                        value=[],
                                        switch=True,
                                        className="mt-1 mb-4",
                                    ),
                                    width=12,
                                ),
                            ]
                        ),

                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Wnioski globalne", className="card-title"),
                                    html.Div(id="global-analysis-text", className="text-muted"),
                                ]
                            ),
                            style={"border": "1px solid #ede9f7", "borderRadius": "14px", "backgroundColor": "#fcfaff"},
                            className="mb-4",
                        ),

                        html.H5("Tabela danych analitycznych", className="mb-3"),
                        dash_table.DataTable(
                            id="analysis-table",
                            page_size=12,
                            sort_action="native",
                            filter_action="native",
                            style_table={"overflowX": "auto"},
                            style_cell={
                                "textAlign": "center",
                                "padding": "8px",
                                "fontFamily": "Arial",
                                "fontSize": "14px",
                            },
                            style_header={
                                "backgroundColor": "#f1f3f5",
                                "fontWeight": "bold",
                            },
                            style_data={
                                "backgroundColor": "white",
                                "border": "1px solid #dee2e6",
                            },
                        ),
                    ]
                ),
                style=CARD_STYLE,
                className="mb-4",
            ),
        ],
        style=CONTENT_STYLE,
    )



def create_layout():
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(create_sidebar(), width=3),
                    dbc.Col(create_main_content(), width=9),
                ],
                className="g-0",
            ),
            dcc.Store(id="confetti-fire", data=0),
        ],
        fluid=True,
        className="px-0",
    )