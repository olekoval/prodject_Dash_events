import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc


app = Dash(__name__, use_pages=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
dbc.Row(
    [
    dbc.Col(html.Div(
        [dcc.Link(f"{page['name']}", href=page["relative_path"]) 
         for page in dash.page_registry.values()]
        ),
            width=12, md=2),
    dbc.Col(
        [
            html.H2("""ПМГ: Профілактика, 
                        діагностика, спостереження та лікування в 
                        амбулаторних умовах
                        """),
            dash.page_container,
         ], width=12, md=10)
    ]),
fluid=True)

if __name__ == "__main__":
    app.run(debug=True, port=8050)


    
    
