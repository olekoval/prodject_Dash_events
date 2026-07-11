import dash
from dash import Dash, html


app = Dash(__name__, use_pages=True)

app.layout = html.Div([
    html.H1("Профілактка", style={"textAlign": "center"}),
    html.Hr(),
    
    dash.page_container
])

if __name__ == "__main__":
    app.run(debug=True, port=8050)
