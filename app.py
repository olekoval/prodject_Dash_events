import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc


app = Dash(__name__, use_pages=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.NavbarSimple(
        children=[
                    dbc.NavItem(dbc.NavLink(f"{page['name']}", href=page["relative_path"]))
                    for page in dash.page_registry.values()
                ],
        brand="""ПМГ: Профілактика, 
                    діагностика, спостереження та лікування в 
                    амбулаторних умовах
                    """,  # Текст/логотип зліва
        brand_href="/",         # Посилання при кліку на логотип
        color="primary",        # Колір панелі (синій за замовчуванням у Bootstrap)
        dark=True,              # Білий текст для темного фону
        className="mb-4",       # Відступ знизу від панелі
        fluid=True
            ),

    dbc.Container([
##    html.H2("""ПМГ: Профілактика, 
##                    діагностика, спостереження та лікування в 
##                    амбулаторних умовах
##                    """, className="text-center my-4"),    
    dash.page_container,
    ], fluid=True)
])

if __name__ == "__main__":
    app.run(debug=True, port=8050)


    
    
