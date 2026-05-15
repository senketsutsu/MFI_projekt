import dash
import dash_bootstrap_components as dbc
from dash import Input, Output

from ui.layout import create_layout
from ui.callbacks import register_callbacks

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY, dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    external_scripts=[ 
        "https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"
    ],
)

app.title = "PageRank Explorer"
app.layout = create_layout()

register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)