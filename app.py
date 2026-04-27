import dash
import dash_bootstrap_components as dbc

from ui.layout import create_layout
from ui.callbacks import register_callbacks

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
)
app.title = "PageRank krok po kroku"
app.layout = create_layout()

register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)